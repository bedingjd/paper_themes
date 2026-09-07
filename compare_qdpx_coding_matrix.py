#!/usr/bin/env python3
"""Compare thematic coding in two QDPX projects.

The program reads project.qde directly from each ZIP-based .qdpx archive.  Its
primary unit is a binary TextSource/code decision: was a code used at least
once in that source?  It also reports selection counts and character ranges,
but repeated applications of one code do not inflate set-based agreement.

No third-party packages are required, except the graph requires matplotlib (added to env requirements)

USAGE:
In bash terminal: python3 compare_qdpx_coding.py session_1.qdpx session_2.qdpx -o comparison_results
- By default, unmatched sources are reported but excluded from reliability calculations. 
  Add '--include-unmatched-sources' to treat missing sources as having no selected codes.
- For the graph/matrix:
  - It is stored under: comparison_results/graphs/
  - You can control readibility with:
    - --themes-per-page 25
  - Or turn off the graphs with:
    - --no-graphs
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
import zipfile
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from xml.etree import ElementTree as ET


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


@dataclass
class SourceCoding:
    guid: str
    name: str
    path: str
    codes: Counter[str] = field(default_factory=Counter)
    ranges: dict[str, list[tuple[int | None, int | None]]] = field(default_factory=dict)


@dataclass
class ProjectData:
    path: Path
    name: str
    code_names: dict[str, str]
    sources: dict[str, SourceCoding]


def read_project(path: Path) -> ProjectData:
    """Read project.qde from a QDPX archive (or read a QDE file directly)."""
    if path.suffix.lower() == ".qde":
        xml_bytes = path.read_bytes()
    else:
        try:
            with zipfile.ZipFile(path) as archive:
                candidates = [n for n in archive.namelist() if Path(n).name.lower() == "project.qde"]
                if not candidates:
                    raise ValueError(f"{path}: archive contains no project.qde")
                xml_bytes = archive.read(sorted(candidates, key=lambda n: (n.count("/"), n))[0])
        except zipfile.BadZipFile as exc:
            raise ValueError(f"{path}: not a valid QDPX/ZIP file") from exc

    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise ValueError(f"{path}: project.qde is not well-formed XML: {exc}") from exc

    code_names: dict[str, str] = {}
    for element in root.iter():
        if local_name(element.tag) == "Code":
            guid = element.get("guid") or element.get("GUID")
            if guid:
                code_names[guid.upper()] = element.get("name") or guid

    sources: dict[str, SourceCoding] = {}
    for element in root.iter():
        if local_name(element.tag) != "TextSource":
            continue
        guid = (element.get("guid") or "").upper()
        name = element.get("name") or guid or "(unnamed source)"
        plain_path = element.get("plainTextPath") or ""
        source = SourceCoding(guid=guid, name=name, path=plain_path)
        for selection in element:
            if local_name(selection.tag) != "PlainTextSelection":
                continue
            start = as_int(selection.get("startPosition"))
            end = as_int(selection.get("endPosition"))
            # Usually CodeRef is under Coding, but descendant search tolerates variants.
            refs = [d for d in selection.iter() if local_name(d.tag) == "CodeRef"]
            for ref in refs:
                code_guid = (ref.get("targetGUID") or ref.get("targetGuid") or "").upper()
                if not code_guid:
                    continue
                source.codes[code_guid] += 1
                source.ranges.setdefault(code_guid, []).append((start, end))
        # Preserve duplicate names by initially keying with GUID/path; matching happens later.
        key = guid or plain_path or name
        if key in sources:
            raise ValueError(f"{path}: duplicate TextSource identity {key!r}")
        sources[key] = source
    return ProjectData(path, root.get("name") or path.stem, code_names, sources)


def as_int(value: str | None) -> int | None:
    try:
        return int(value) if value is not None else None
    except ValueError:
        return None


def source_match_key(source: SourceCoding, mode: str) -> str:
    if mode == "guid":
        return source.guid
    if mode == "name":
        return source.name.casefold().strip()
    if mode == "path":
        return Path(source.path.removeprefix("internal://")).name.casefold()
    raise ValueError(mode)


def indexed_sources(project: ProjectData, mode: str) -> dict[str, SourceCoding]:
    result: dict[str, SourceCoding] = {}
    for source in project.sources.values():
        key = source_match_key(source, mode)
        if not key:
            continue
        if key in result:
            raise ValueError(f"{project.path}: duplicate source {mode} {key!r}; choose another --match-by mode")
        result[key] = source
    return result


def choose_match_mode(a: ProjectData, b: ProjectData, requested: str) -> str:
    if requested != "auto":
        return requested
    scores = {}
    for mode in ("guid", "path", "name"):
        ka = {source_match_key(s, mode) for s in a.sources.values()} - {""}
        kb = {source_match_key(s, mode) for s in b.sources.values()} - {""}
        scores[mode] = len(ka & kb)
    return max(("guid", "path", "name"), key=lambda mode: scores[mode])


def safe_ratio(numerator: float, denominator: float) -> float | None:
    return numerator / denominator if denominator else None


def fmt(value: float | None) -> str:
    return "NA" if value is None or math.isnan(value) else f"{value:.6f}"


def cohen_kappa(n11: int, n10: int, n01: int, n00: int) -> tuple[float | None, float | None]:
    total = n11 + n10 + n01 + n00
    if not total:
        return None, None
    observed = (n11 + n00) / total
    a_yes = n11 + n10
    b_yes = n11 + n01
    expected = (a_yes * b_yes + (total - a_yes) * (total - b_yes)) / (total * total)
    kappa = safe_ratio(observed - expected, 1 - expected)
    return observed, kappa


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def safe_filename(value: str, maximum: int = 90) -> str:
    """Return a portable filename component."""
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._")
    return (cleaned or "unnamed")[:maximum]


def draw_split_square(
    ax: object, x: float, y: float, session_1: int, session_2: int,
    size: float = 0.82,
) -> None:
    """Draw one diagonal cell: lower-left=S1, upper-right=S2."""
    from matplotlib.patches import Rectangle

    agreement = session_1 == session_2
    border_color = "#2f9e2f" if agreement else "#e32620"
    left, bottom = x - size / 2, y - size / 2
    ax.add_patch(Rectangle(
        (left, bottom), size, size, facecolor="white",
        edgecolor=border_color, linewidth=3.0, zorder=2,
    ))
    # The matrix's y-axis is inverted so paper 1 appears at the top. In data
    # coordinates this rising line therefore renders from upper-left to
    # lower-right on the page.
    ax.plot([left, left + size], [bottom, bottom + size],
            color="#102f3d", linewidth=1.5, zorder=3)
    # Account for that same inverted y-axis so the values remain visually in
    # the requested triangles: Session 1 lower-left, Session 2 upper-right.
    ax.text(left + size * 0.28, bottom + size * 0.75, str(session_1),
            ha="center", va="center", fontsize=7.5, color="black", zorder=4)
    ax.text(left + size * 0.72, bottom + size * 0.25, str(session_2),
            ha="center", va="center", fontsize=7.5, color="black", zorder=4)


def draw_coding_matrix_page(
    ax: object,
    code_guids: list[str],
    code_names: dict[str, str],
    comparison_keys: list[str],
    sources_1: dict[str, SourceCoding],
    sources_2: dict[str, SourceCoding],
    title: str,
) -> None:
    """Draw papers as rows and themes as diagonal split-square columns."""
    for row, key in enumerate(comparison_keys):
        selected_1 = set(sources_1[key].codes) if key in sources_1 else set()
        selected_2 = set(sources_2[key].codes) if key in sources_2 else set()
        for column, code in enumerate(code_guids):
            draw_split_square(ax, column, row, int(code in selected_1), int(code in selected_2))

    labels = [code_names.get(code, code) for code in code_guids]
    paper_names = [(sources_1.get(key) or sources_2[key]).name for key in comparison_keys]
    ax.set_xticks(range(len(code_guids)), labels, rotation=55, ha="right", fontsize=7)
    ax.set_yticks(range(len(comparison_keys)), paper_names, fontsize=8)
    ax.set_xlim(-0.55, max(len(code_guids) - 0.45, 0.55))
    ax.set_ylim(-0.55, max(len(comparison_keys) - 0.45, 0.55))
    ax.invert_yaxis()
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("Themes / codes")
    ax.set_ylabel("Papers / TextSources")
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.tick_params(axis="both", length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)


def create_coding_matrix(
    output_file: Path,
    code_guids: list[str],
    code_names: dict[str, str],
    comparison_keys: list[str],
    sources_1: dict[str, SourceCoding],
    sources_2: dict[str, SourceCoding],
    themes_per_page: int = 40,
) -> None:
    """Create the paginated paper-by-theme split-square matrix."""
    try:
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_pdf import PdfPages
    except ImportError as exc:
        raise RuntimeError(
            "Graph creation requires matplotlib. Install it with: python3 -m pip install matplotlib"
        ) from exc

    output_file.parent.mkdir(parents=True, exist_ok=True)
    chunks = [code_guids[i:i + themes_per_page] for i in range(0, len(code_guids), themes_per_page)] or [[]]
    with PdfPages(output_file) as pdf:
        for page_number, chunk in enumerate(chunks, start=1):
            width = max(12.0, min(24.0, 0.48 * max(len(chunk), 1)))
            height = max(7.5, min(16.0, 0.55 * max(len(comparison_keys), 1) + 4.5))
            fig, ax = plt.subplots(figsize=(width, height))
            first = 1 + (page_number - 1) * themes_per_page
            last = first + len(chunk) - 1
            title = f"Thematic coding matrix — themes {first}–{last} of {len(code_guids)}"
            draw_coding_matrix_page(ax, chunk, code_names, comparison_keys,
                                    sources_1, sources_2, title)
            fig.text(
                0.5, 0.985,
                "Each cell: lower-left = Session 1; upper-right = Session 2; "
                "green border = agreement; red border = disagreement",
                ha="center", va="top", fontsize=9,
            )
            fig.subplots_adjust(left=0.18, right=0.99, top=0.91, bottom=0.27)
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)


def create_result_graphs(
    graph_directory: Path,
    comparison_keys: list[str],
    sources_1: dict[str, SourceCoding],
    sources_2: dict[str, SourceCoding],
    code_names: dict[str, str],
    themes_per_page: int,
) -> int:
    """Create one paginated paper-by-theme matrix PDF."""
    # Include every codebook theme so jointly-unselected themes correctly show
    # agreement=1. Sort by human-readable theme name for a stable x-axis.
    all_codes = set(code_names)
    for key in comparison_keys:
        all_codes.update(sources_1[key].codes if key in sources_1 else ())
        all_codes.update(sources_2[key].codes if key in sources_2 else ())
    ordered_codes = sorted(all_codes, key=lambda code: (code_names.get(code, code).casefold(), code))

    create_coding_matrix(
        graph_directory / "coding_matrix.pdf", ordered_codes, code_names,
        comparison_keys, sources_1, sources_2, themes_per_page,
    )
    return 1


def compare(a: ProjectData, b: ProjectData, output: Path, match_by: str,
            include_unmatched: bool, make_graphs: bool = True,
            themes_per_page: int = 40) -> dict[str, object]:
    output.mkdir(parents=True, exist_ok=True)
    mode = choose_match_mode(a, b, match_by)
    ia, ib = indexed_sources(a, mode), indexed_sources(b, mode)
    shared = sorted(ia.keys() & ib.keys())
    only_a, only_b = sorted(ia.keys() - ib.keys()), sorted(ib.keys() - ia.keys())
    comparison_keys = sorted(ia.keys() | ib.keys()) if include_unmatched else shared
    code_names = {**a.code_names, **b.code_names}
    code_universe = sorted({c for k in comparison_keys for c in ((ia.get(k).codes if k in ia else {}) | (ib.get(k).codes if k in ib else {}))})

    source_rows: list[dict[str, object]] = []
    difference_rows: list[dict[str, object]] = []
    total_intersection = total_union = 0
    exact = 0
    for key in comparison_keys:
        sa, sb = ia.get(key), ib.get(key)
        ca, cb = set(sa.codes if sa else ()), set(sb.codes if sb else ())
        both, a_only, b_only = ca & cb, ca - cb, cb - ca
        union = ca | cb
        jaccard = safe_ratio(len(both), len(union))
        if not union: jaccard = 1.0
        dice = safe_ratio(2 * len(both), len(ca) + len(cb))
        if not ca and not cb: dice = 1.0
        is_exact = ca == cb
        exact += int(is_exact)
        total_intersection += len(both)
        total_union += len(union)
        status = "shared" if sa and sb else ("session_1_only" if sa else "session_2_only")
        source_rows.append({
            "source_key": key, "source_name": (sa or sb).name, "status": status,
            "session_1_unique_codes": len(ca), "session_2_unique_codes": len(cb),
            "codes_in_both": len(both), "session_1_only_codes": len(a_only),
            "session_2_only_codes": len(b_only), "jaccard": fmt(jaccard),
            "dice_f1": fmt(dice), "exact_code_set_match": is_exact,
        })
        for code in sorted(union):
            if code in both and (sa.codes[code] == sb.codes[code]):
                continue
            difference_rows.append({
                "source_key": key, "source_name": (sa or sb).name,
                "code_guid": code, "code_name": code_names.get(code, "(unknown code)"),
                "session_1_present": code in ca, "session_2_present": code in cb,
                "session_1_selection_count": sa.codes[code] if sa else 0,
                "session_2_selection_count": sb.codes[code] if sb else 0,
                "session_1_ranges": json.dumps(sa.ranges.get(code, []) if sa else []),
                "session_2_ranges": json.dumps(sb.ranges.get(code, []) if sb else []),
            })

    # Binary source-by-code contingency table, including jointly absent decisions.
    n11 = n10 = n01 = n00 = 0
    code_rows: list[dict[str, object]] = []
    for code in code_universe:
        c11 = c10 = c01 = c00 = 0
        for key in comparison_keys:
            pa = code in ia[key].codes if key in ia else False
            pb = code in ib[key].codes if key in ib else False
            if pa and pb: c11 += 1
            elif pa: c10 += 1
            elif pb: c01 += 1
            else: c00 += 1
        observed, kappa = cohen_kappa(c11, c10, c01, c00)
        dice = safe_ratio(2 * c11, 2 * c11 + c10 + c01)
        code_rows.append({"code_guid": code, "code_name": code_names.get(code, "(unknown code)"),
                          "both_selected": c11, "session_1_only": c10, "session_2_only": c01,
                          "neither_selected": c00, "percent_agreement": fmt(observed),
                          "cohen_kappa": fmt(kappa), "positive_agreement_dice": fmt(dice)})
        n11 += c11; n10 += c10; n01 += c01; n00 += c00

    observed, kappa = cohen_kappa(n11, n10, n01, n00)
    positive = safe_ratio(2 * n11, 2 * n11 + n10 + n01)
    negative = safe_ratio(2 * n00, 2 * n00 + n10 + n01)
    summary: dict[str, object] = {
        "session_1": str(a.path), "session_2": str(b.path), "source_match_method": mode,
        "session_1_sources": len(ia), "session_2_sources": len(ib), "shared_sources": len(shared),
        "session_1_only_sources": len(only_a), "session_2_only_sources": len(only_b),
        "unmatched_sources_in_agreement_metrics": include_unmatched,
        "sources_compared": len(comparison_keys), "codes_in_compared_universe": len(code_universe),
        "exact_source_code_set_matches": exact,
        "exact_source_code_set_match_rate": safe_ratio(exact, len(comparison_keys)),
        "macro_mean_source_jaccard": safe_ratio(sum(float(r["jaccard"]) for r in source_rows), len(source_rows)),
        "micro_jaccard": safe_ratio(total_intersection, total_union),
        "binary_decisions_both_yes": n11, "binary_decisions_session_1_only_yes": n10,
        "binary_decisions_session_2_only_yes": n01, "binary_decisions_both_no": n00,
        "overall_percent_agreement": observed, "cohen_kappa": kappa,
        "positive_agreement_dice_f1": positive, "negative_agreement": negative,
        "differences_rows": len(difference_rows),
    }
    write_csv(output / "source_agreement.csv", list(source_rows[0].keys()) if source_rows else ["source_key"], source_rows)
    write_csv(output / "code_agreement.csv", list(code_rows[0].keys()) if code_rows else ["code_guid"], code_rows)
    write_csv(output / "coding_differences.csv", list(difference_rows[0].keys()) if difference_rows else ["source_key"], difference_rows)
    unmatched_rows = ([{"session": 1, "source_key": k, "source_name": ia[k].name} for k in only_a] +
                      [{"session": 2, "source_key": k, "source_name": ib[k].name} for k in only_b])
    write_csv(output / "unmatched_sources.csv", ["session", "source_key", "source_name"], unmatched_rows)
    if make_graphs:
        summary["graph_files_created"] = create_result_graphs(
            output / "graphs", comparison_keys, ia, ib, code_names, themes_per_page
        )
    (output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare TextSource coding between two QDPX/QDE projects.")
    parser.add_argument("session_1", type=Path)
    parser.add_argument("session_2", type=Path)
    parser.add_argument("-o", "--output", type=Path, default=Path("qdpx_comparison"))
    parser.add_argument("--match-by", choices=("auto", "guid", "path", "name"), default="auto")
    parser.add_argument("--include-unmatched-sources", action="store_true",
                        help="Treat a source absent from one project as having no codes (default: compare shared sources only).")
    parser.add_argument("--no-graphs", action="store_true",
                        help="Do not create the overall and per-TextSource PDF graphs.")
    parser.add_argument("--themes-per-page", type=int, default=40,
                        help="Maximum themes shown on each PDF page (default: 40).")
    args = parser.parse_args()
    if args.themes_per_page < 1:
        parser.error("--themes-per-page must be at least 1")
    try:
        summary = compare(read_project(args.session_1), read_project(args.session_2),
                          args.output, args.match_by, args.include_unmatched_sources,
                          not args.no_graphs, args.themes_per_page)
    except (OSError, ValueError, RuntimeError) as exc:
        parser.exit(2, f"error: {exc}\n")
    print(json.dumps(summary, indent=2))
    print(f"\nDetailed reports written to: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
