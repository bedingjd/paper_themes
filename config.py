import docx2txt
# ============================================================================
# This file includes key variables used by the main_app
# ============================================================================

PROJECT_NAME = 'Proj_gemma_4_31_20260511a_test20260513_1015_V3'
#PROJECT_NAME = 'Proj_olmo31_20260216_0820'                       # name for the new MaxQDA project to be created
OUTPUT_FILES_PATH = 'Output_Proj_gemma_4_31_20260510a_20260510_1407' # 'Output_Proj_Deepseek_31_20260218_1424_20260218_1424' #'Output_Proj_Deepseek_31_20260216_1410'
#OUTPUT_FILES_PATH = 'Output_Proj_olmo31_20260216_0820'           # folder is in the same directory.  was 'output_files'
                                                                                #    This is where the output files from the AI are stored
# short description to describe this run.  This will be printed at the top of each output file
# Don't need to include the Model Name, or parameters as these will be included automatically
#RUN_DESCRIPTION = "Using LM Studio with PC with 50K context window, revised Chat-GPT prompt"
#RUN_DESCRIPTION = "Using Gemma 3-27, 8 Aug Codebook as project.qde, just the short prompt, w/ JSON, same as Proj_gemini_25_pro_shortPrompt to test reliability across runs, and whether Gemma is as good as Gemini."
#RUN_DESCRIPTION = "Using Deepseek R1, 0528, 8 Aug Codebook as .qdc file (used to be project.qde), just the short prompt, output in original format, just one paper, tell model to specifically use NO CODE, Temperature = 0" 
#RUN_DESCRIPTION = "Using Deepseek R1, 0528, 8 Aug Codebook as .qdc file (used to be project.qde), just the short prompt, output in csv, just one paper, Temperature = 0" 
#RUN_DESCRIPTION = "Using Olmo 3_1, 8 Aug Codebook as excel file, just the short prompt, output in csv, just one paper, Temperature = 0" 
RUN_DESCRIPTION = "Using Deepseek 3_1, 8 Aug Codebook as .pdq with added GUIDs, just the revised Feb 2026 prompt, output in csv and xml, just one paper, Temperature = 0" 
#RUN_DESCRIPTION = "Using Olmo 3_1, 8 Aug Codebook as .pdq with added GUIDs, just the revised Feb 2026 prompt, output in csv and xml, just one paper, Temperature = 0" 
RUN_DESCRIPTION = "Using Gemma 4-31-31B, 8 Aug Codebook as .pdq with added GUIDs, just the revised Feb 2026 prompt, output in csv and xml, just one paper, Temperature = 0" 

# point to the correct server
BASE_URL = "https://openrouter.ai/api/v1"               # OpenRouter server
#BASE_URL = "http://localhost:1234/v1"                   # PC, check the IP address
#BASE_URL = "http://192.168.1.187:1234/v1"                   # PC, check the IP address
BASE_URL = "http://192.168.1.187:1234/v1"                   # PC, check the IP address
#api_key="lm-studio"                                     # For LM Studio, not sure this is needed to checked

# The name of the AI model you would like to use
# list of models and rates at: https://ai.google.dev/gemini-api/docs/rate-limits
# You can also run the program and select option 3 to get a list of all models, but it doesn't identify the ones with a free tier
#MODEL_NAME = "gemini-2.5-flash-preview-04-17"           # The name of the model you want to use. 
MODEL_NAME = "gemini-2.5-flash-lite-preview-06-17"
MODEL_NAME_OPENAI = "deepseek/deepseek-r1:free"          # The name of the model you want to use for OpenAI Router, list of free models here: https://openrouter.ai/models?max_price=0
MODEL_NAME_OPENAI = "deepseek/deepseek-r1-0528:free"
MODEL_NAME_OPENAI = "google/gemini-2.5-pro-exp-03-25"
MODEL_NAME_OPENAI = "qwen/qwen3-235b-a22b:free"
MODEL_NAME_OPENAI = "meta-llama/llama-3.2-3b-instruct:free"
MODEL_NAME_OPENAI = "mistralai/mistral-small-24b-instruct-2501:free"
MODEL_NAME_OPENAI = "mistralai/mistral-small-3.1-24b-instruct:free"
MODEL_NAME_OPENAI = "mistralai/mistral-small-3.2-24b-instruct:free"
MODEL_NAME_OPENAI = "meta-llama/llama-3.2-3b-instruct:free"
MODEL_NAME_OPENAI = "google/gemini-2.0-flash-exp:free"
MODEL_NAME_OPENAI = "z-ai/glm-4.5-air:free"
MODEL_NAME_OPENAI = "x-ai/grok-4"
MODEL_NAME_OPENAI = "z-ai/glm-4.5-air:free"
MODEL_NAME_OPENAI = "deepseek/deepseek-r1-0528:free"
MODEL_NAME_OPENAI = "deepseek/deepseek-r1-0528-qwen3-8b:free"
MODEL_NAME_OPENAI = "openai/gpt-oss-20b"                        # in LM Studio on the PC
MODEL_NAME_OPENAI = "google/gemini-2.5-pro"
MODEL_NAME_OPENAI = "google/gemma-3-27b"                        # in LM studio on the PC

MODEL_NAME_OPENAI = "openai/gpt-oss-20b"
MODEL_NAME_OPENAI = "deepseek/deepseek-r1-0528-qwen3-8b:free"
MODEL_NAME_OPENAI = "openai/gpt-5-pro"
MODEL_NAME_OPENAI = "google/gemini-3-flash-preview"
MODEL_NAME_OPENAI = "allenai/olmo-3.1-32b-think"
MODEL_NAME_OPENAI = "nex-agi/deepseek-v3.1-nex-n1"
MODEL_NAME_OPENAI = "google/gemma-4-31b"                        # in LM studio on the PC


# set model config items:
MAX_CODES_PER_UNIT = 2
MAX_CODES_PER_PAPER = 30
MIN_CONFIDENCE = 0.70
GRANULARITY = "sentence"                                # "sentence" or "paragraph"
MODEL_TEMPERATURE = 0.0                                 # was 1.0



# location of the source folder.  Place the papers to be coded inside the source folder
# path and name of the qdpx file
QDPX_NAME = "references/2025-06-16_ICLS_Conf_Themes_ALL_just10.qdpx"                       # Name of the .qdpx file  was "2025-05-12_5_3.qdpx"
sources_directory_path = "sources/"
USER_NAME = 'jwmcelde'                                  # this will mark all codings with this user name
EXFILES_PATH = 'sources'                                # was "/home/jomac/projects/Donaldson/ExFiles"  was "ExFiles"


# this section for Codebook information.  The codebook can be in either the project file or in an Excel file
CODEBOOK_IN_QDE = True                                  # set to false if codebook is in Excel file          <------------ *** was True
CODEBOOK_QDE_PATH = 'project.qde'                       # path to qde file, with Codebook included.  Was Project5bb/project.qde 'resources/project.qde'
CODEBOOK_QDE_PATH = 'AllCodes_8_aug.qdc'                
CODEBOOK_QDE_PATH = 'AllCodes_8_aug_v2.qdc'             # this is the one with the new codes. Also pasted in the paper info from old project.qde
CODEBOOK_QDE_PATH = 'references/project_with_generated_codes.qde'
CODEBOOK_EXCEL_PATH = 'resources/codebook_small_3_5.xlsx'     # path to Excel file
CODEBOOK_IN_WORD = "202508_updated_codebook/2025-08-08 ICLS Conference Themes - Codebook.docx"
#CODEBOOK_EXCEL_PATH = '/202508_updated_codebook/2025_08_08_Codebook_with_GUID.xlsx'


# ================
# Learning Science Paper Location
LEARNING_SCIENCES_OVERVIEW_FILENAME = 'references/00_Learning_Sciences_Overview_converted.rtf'

# ============================================================================
# Model Information
# ============================================================================



# ============================================================================
# Prompt Information
# ============================================================================
# NOTE: do not change the function variables, or variables names, 
#       they are just placeholders that will be filled in by the main_app code
#       later.
# ============================================================================
def createThePrompt(qde_content, paper_ID, this_paper):
    prompt_content = f"""
        LENA2 Coding Assistant is tailored to analyze papers, focusing on specific themes. 
        
        Step 1: It always starts by analyzing the codebook.  The codebook is located in ({qde_content}), 
        and the codes are in the <CodeBook><Codes> section.  Each code is listed with a Unique Identification (ID) (guid), and a name.
        
        Step 2: It then reads the paper to understand the overall context.
        The paper Unique IDs (guid) is ({paper_ID})
        The paper content is ({this_paper}).
        
        Step 3: LENA2 then determines which codes from the codebook apply to the paper.
        a. It analyzes each paragraph, one at at time, and selects any codes that apply to that paragraph.
        b. LENA2 ensures all the codes are considered.
        c. For every code identified, LENA2 also identifies which paragraph matches the codes it found, aligning them with codes strictly from the existing codebook 
        which contains the name of the codes with a brief definition.
        This assistant provides coding by quoting 
        the exact paragraph and then referring only to the guid and the exact code names listed in the codebook, 
        such as 'guid="A8FDF7D5-91FA-43CA-97AF-FB7DA8A77DB4" name="ASSMNT - Affective Outcomes"', 
        'guid="2B887F2B-2CF1-4393-8A31-41737901F9EC" name="ASSMNT - Authentic Assessment"',
        or 'guid="0897F606-3A15-4092-9760-DBA29E0DD86C" name="COMMCOLAB - Community Partnerships"'
        d. It reports a confidence level (e.g., 'Confidence: 79%') for each code.
        e. It reports the start and end of the paragraph, referenced by indicating the number of characters from the start of the paper
        to the first character in the paragraph.  And also identifies the number of characters until the last character in the paragraph.
        f. It only uses the codes listed in the codebook exactly as written in the codebook (including spelling mistakes).
        g. Importantly, ence a code is applied, do not use it again in the same paper.
        
        Step 4: After the paper is completely coded LENA2 also produces the results in a qdpx format.
        
        LENA2 Coding Assistant must output structured data in JSON format, which will later be converted into XML.
        The JSON structure should match this schema:

        {{
        "guid": "<guid of paper>",
        "plain_text_path": "<path>",
        "name": "<document name>",
        "creating_user": "402C8B2D-A9B1-4D7F-854C-7F1E14F390ED",
        "modifying_user": "402C8B2D-A9B1-4D7F-854C-7F1E14F390ED",
        "modified_datetime": "2024-03-08T14:34:57Z",
        "creation_datetime": "2024-03-08T14:34:57Z",
        "selections": [
            {{
            "guid": "<selection guid>",
            "creating_user": "402C8B2D-A9B1-4D7F-854C-7F1E14F390ED",
            "modifying_user": "402C8B2D-A9B1-4D7F-854C-7F1E14F390ED",
            "start_position": <start position>,
            "end_position": <end position>,
            "sentence": <sentence>,
            "creation_datetime": "2024-05-30T20:33:52Z",
            "modified_datetime": "2024-05-30T20:33:52Z",
            "coding": {{
                "creating_user": "402C8B2D-A9B1-4D7F-854C-7F1E14F390ED",
                "guid": "<coding guid>",
                "creation_datetime": "2024-05-30T20:33:52Z",
                "code_ref": {{
                "target_guid": "<code reference GUID>",
                "code_name": "<code name>"
                }}
            }}
            }}
        ]
        }}

        The output **must** be in this JSON format.

        """
    return prompt_content


def createThePromptByCodeCategory(qde_content, paper_ID, this_paper):
    prompt_content = f"""
        LENA2 Coding Assistant is tailored to analyze papers, focusing on specific themes. 
        
        Step 1: It always starts by analyzing the CodeBook.  The CodeBook is located in ({qde_content}), 
        which is json, and the codes are in the 'Code' section, which is a list of codes.
        Each code is listed with a Unique Identification (ID) (guid), and a name, as well as a Decription
        to decribe when the code should be used.
        
        Step 2: It then reads the paper to understand the overall context.
        The paper Unique IDs (guid) is ({paper_ID})
        The paper content is ({this_paper}).
        
        Step 3: LENA2 then determines which codes from the codebook apply to the paper.
        It analyzes each paragraph in the paper, one at at time, and selects any codes that apply to that paragraph.
        LENA2 ensures all the codes are considered.
        
        For every code identified, LENA2 also identifies which paragraph matches the codes it found, aligning them with codes strictly from the existing codebook 
        which contains the name of the codes with a brief definition.
        This assistant provides coding by quoting 
        the exact paragraph and then referring only to the guid and the exact code names listed in the codebook, 
        such as 'guid="A8FDF7D5-91FA-43CA-97AF-FB7DA8A77DB4" name="ASSMNT - Affective Outcomes"', 
        'guid="2B887F2B-2CF1-4393-8A31-41737901F9EC" name="ASSMNT - Authentic Assessment"',
        or 'guid="0897F606-3A15-4092-9760-DBA29E0DD86C" name="COMMCOLAB - Community Partnerships"'
        It reports a confidence level (e.g., 'Confidence: 79%') for each code.
        It reports the start and end of the paragraph, referenced by indicating the number of characters from the start of the paper
        to the first character in the paragraph.  And also identifies the number of characters until the last character in the paragraph.
        It only uses the codes listed in the codebook exactly as written in the codebook (including spelling mistakes).  
        
        Step 4: After the paper is completely coded LENA2 also produces the results in a JSON format.
        
        LENA2 Coding Assistant must output structured data in JSON format, which will later be converted into XML.
        The JSON structure should match this schema:

        {{
        "guid": "<guid of paper>",
        "plain_text_path": "<path>",
        "name": "<document name>",
        "creating_user": "402C8B2D-A9B1-4D7F-854C-7F1E14F390ED",
        "modifying_user": "402C8B2D-A9B1-4D7F-854C-7F1E14F390ED",
        "modified_datetime": "2024-03-08T14:34:57Z",
        "creation_datetime": "2024-03-08T14:34:57Z",
        "selections": [
            {{
            "guid": "<selection guid>",
            "creating_user": "402C8B2D-A9B1-4D7F-854C-7F1E14F390ED",
            "modifying_user": "402C8B2D-A9B1-4D7F-854C-7F1E14F390ED",
            "start_position": <start position>,
            "end_position": <end position>,
            "sentence": <sentence>,
            "creation_datetime": "2024-05-30T20:33:52Z",
            "modified_datetime": "2024-05-30T20:33:52Z",
            "coding": {{
                "creating_user": "402C8B2D-A9B1-4D7F-854C-7F1E14F390ED",
                "guid": "<coding guid>",
                "creation_datetime": "2024-05-30T20:33:52Z",
                "code_ref": {{
                "target_guid": "<code reference GUID>",
                "code_name": "<code name>"
                }}
            }}
            }}
        ]
        }}

        The output **must** be in this JSON format.

        """
    return prompt_content



def createThePromptByCodeCategory2(qde_content, paper_ID, this_paper,
                                   granularity=GRANULARITY,           # "sentence" or "paragraph"
                                    max_codes_per_unit=MAX_CODES_PER_UNIT,              # tighten if still overcoding
                                    max_codes_per_paper=MAX_CODES_PER_PAPER,
                                    min_confidence=MIN_CONFIDENCE):
    prompt_content = f"""
        You are LENA2, a **high-precision** qualitative coding assistant. Your top priority is to **avoid false positives**. 
If you are not confident a code matches its definition based on explicit evidence in the text, **do not assign it**.

## Inputs
- CODEBOOK XML (excerpt): {qde_content}
  - Codes are under <CodeBook><Codes>. Each <Code> has a unique GUID and a name/definition.
- PAPER
  - GUID: {paper_ID}
  - TEXT: {this_paper}

## Procedure (two stages)
1) **Screening (Do NOT output results yet):**
   - Read the code definitions carefully. For each code, note key **inclusion** criteria and **exclusion** criteria in your own head.
   - Split the paper by {granularity}. For each {granularity}, consider **at most {max_codes_per_unit}** candidate codes that
     plausibly match. If none clearly match, choose **zero**.

2) **Verification (Output only verified results):**
   For each candidate from stage 1, verify against this rubric. Assign the code **only if all are satisfied**:
   R1. Evidence: A **verbatim quote** (1–3 sentences) from the paper directly expresses the code’s concept.
   R2. Alignment: The evidence aligns with the code’s core definition (not just a vague thematic proximity).
   R3. Exclusions: The code’s **exclusion criteria** do not apply.
   R4. Specificity: This code is more specific/appropriate than available alternatives.
   R5. Confidence ≥ {min_confidence} given the evidence.

## Output JSON schema (STRICT)
Return **only** JSON (no extra text), in this format:

{{
  "guid": "{paper_ID}",
  "granularity": "{granularity}",
  "min_confidence": {min_confidence},
  "plain_text_path": "<path>",
  "name": "<document name>",
  "creating_user": "402C8B2D-A9B1-4D7F-854C-7F1E14F390ED",
  "modifying_user": "402C8B2D-A9B1-4D7F-854C-7F1E14F390ED",
  "modified_datetime": "2024-03-08T14:34:57Z",
  "creation_datetime": "2024-03-08T14:34:57Z",
  "selections": [
    {{
    "guid": "<selection guid>",
    "creating_user": "402C8B2D-A9B1-4D7F-854C-7F1E14F390ED",
    "modifying_user": "402C8B2D-A9B1-4D7F-854C-7F1E14F390ED",
    "start_position": <start position>,
    "end_position": <end position>,
    "sentence": <sentence>,
    "creation_datetime": "2024-05-30T20:33:52Z",
    "modified_datetime": "2024-05-30T20:33:52Z",
    "coding": {{
        "creating_user": "402C8B2D-A9B1-4D7F-854C-7F1E14F390ED",
        "guid": "<coding guid>",
        "creation_datetime": "2024-05-30T20:33:52Z",
        "code_ref": {{
        "target_guid": "<code reference GUID>",
        "code_name": "<code name>"
        }}
    }}
    }}
  "codings": [
    {{
      "unit_index": <integer index of the {granularity} starting at 0>,
      "text_span": {{
        "start_char": <int>,     // inclusive
        "end_char": <int>        // exclusive
      }},
      "evidence_quote": "<verbatim snippet from paper>",
      "code_ref": {{
        "target_guid": "<GUID from codebook>",
        "code_name": "<name from codebook>"
      }},
      "rubric": {{
        "R1_evidence": true|false,
        "R2_alignment": true|false,
        "R3_exclusions_clear": true|false,
        "R4_specific": true|false
      }},
      "confidence": <float 0..1>
    }}
  ],
  "rejected_considerations": [
    {{
      "unit_index": <int>,
      "code_ref": {{
        "target_guid": "<GUID>",
        "code_name": "<name>"
      }},
      "reason": "why it was rejected (e.g., failed R2 or confidence < threshold)"
    }}
  ]
}}

### Hard constraints
- **Precision over recall**: If uncertain, **omit** the code.
- **Caps**: No more than {max_codes_per_unit} codes per {granularity}. No more than {max_codes_per_paper} codings total.
- **GUIDs must match the codebook.**
- If no codes apply anywhere, return: {{ "paper_guid": "{paper_ID}", "granularity":"{granularity}", "min_confidence": {min_confidence}, "codings": [], "rejected_considerations": [] }}

        """
    return prompt_content



'''
Test Prompt:  Used Word verion of Codebook
I'm doing a research study. I have collected all of the conference papers (they were PDF, but I transformed them all to RTF) from all of the International Conference of the Learning Science meetings since 1996. I have 5,315 papers. 
I want to analyze the evolution of and interaction between themes over time. I want to code all the data for themes, but not based on words (not lexical search). I coded 101 of the conference papers manually, and this process resulted in a robust codebook (attached). 
Please analyze the attached conference paper and tell me which codes apply in every category, and what sentence/paragraph you are using as evidence (use the title of the paper and the author affiliations if there are no other sources of evidence in the manuscript because the whole manuscript is your evidence).
'''
def createThePromptshort(qde_content, paper_ID, this_paper,
                                   granularity=GRANULARITY,           # "sentence" or "paragraph"
                                    max_codes_per_unit=MAX_CODES_PER_UNIT,              # tighten if still overcoding
                                    max_codes_per_paper=MAX_CODES_PER_PAPER,
                                    min_confidence=MIN_CONFIDENCE):
    prompt_content = f"""
    I'm doing a research study. I have collected all of the conference papers (they were PDF, but I transformed them all to RTF) from all of the International Conference of the Learning Science meetings since 1996. I have 5,315 papers. 
    I want to analyze the evolution of and interaction between themes over time. I want to code all the data for themes, but not based on words (not lexical search). I coded 101 of the conference papers manually, and this process resulted in a robust codebook (attached). 
    Please analyze {this_paper} and tell me which codes apply in every category, and what sentence/paragraph you are using as evidence (use the title of the paper and the author affiliations if there are no other sources of evidence in the manuscript because the whole manuscript is your evidence).
    ## Inputs
    - CODEBOOK XML: {qde_content}
        - Codes are under <CodeBook><Codes>. Each <Code> has a unique GUID and a name/definition.
        - PAPER
    - GUID: {paper_ID}
    - TEXT: {this_paper}
    """

    return prompt_content



# this is the short prompt above plus the output language from the previous output efforts
def createThePromptshort2(qde_content, paper_ID, this_paper,
                                   granularity=GRANULARITY,           # "sentence" or "paragraph"
                                    max_codes_per_unit=MAX_CODES_PER_UNIT,              # tighten if still overcoding
                                    max_codes_per_paper=MAX_CODES_PER_PAPER,
                                    min_confidence=MIN_CONFIDENCE):
    prompt_content = f"""
    I'm doing a research study. I have collected all of the conference papers (they were PDF, but I transformed them all to RTF) from all of the International Conference of the Learning Science meetings since 1996. I have 5,315 papers. 
    I want to analyze the evolution of and interaction between themes over time. I want to code all the data for themes, but not based on words (not lexical search). I coded 101 of the conference papers manually, and this process resulted in a robust codebook (attached). 
    Please analyze {this_paper} and tell me which codes apply in every category, and what sentence/paragraph you are using as evidence (use the title of the paper and the author affiliations if there are no other sources of evidence in the manuscript because the whole manuscript is your evidence).
    
    ## Inputs
    - CODEBOOK XML: {qde_content}
        - Codes are under <CodeBook><Codes>. Each <Code> has a unique GUID and a name/definition.
        - PAPER
    - GUID: {paper_ID}
    - TEXT: {this_paper}

    ## Output JSON schema (STRICT)
    After the initial output identifying which codes apply in every category, and what sentence/paragraph is being using as evidence,
    provide the same information in JSON format.  Separate the two with the word 'json'
    Return the JSON portion (no extra text), in this format:
    ***json***
    {{
    "guid": "{paper_ID}",
    "plain_text_path": "<path>",
    "name": "<document name>",
    "creating_user": "402C8B2D-A9B1-4D7F-854C-7F1E14F390ED",
    "modifying_user": "402C8B2D-A9B1-4D7F-854C-7F1E14F390ED",
    "modified_datetime": "2024-03-08T14:34:57Z",
    "creation_datetime": "2024-03-08T14:34:57Z",
    "selections": [
        {{
        "guid": "<selection guid>",
        "creating_user": "402C8B2D-A9B1-4D7F-854C-7F1E14F390ED",
        "modifying_user": "402C8B2D-A9B1-4D7F-854C-7F1E14F390ED",
        "start_position": <start position>,
        "end_position": <end position>,
        "sentence": <sentence>,
        "creation_datetime": "2024-05-30T20:33:52Z",
        "modified_datetime": "2024-05-30T20:33:52Z",
        "coding": {{
            "creating_user": "402C8B2D-A9B1-4D7F-854C-7F1E14F390ED",
            "guid": "<coding guid>",
            "creation_datetime": "2024-05-30T20:33:52Z",
            "code_ref": {{
            "target_guid": "<code reference GUID>",
            "code_name": "<code name>"
            }}
        }}
        }}
    "codings": [
        {{
        "text_span": {{
            "start_char": <int>,     // inclusive
            "end_char": <int>        // exclusive
        }},
        "evidence_quote": "<verbatim snippet from paper>",
        "code_ref": {{
            "target_guid": "<GUID from codebook>",
            "code_name": "<name from codebook>"
        }},
        "confidence": <float 0..1>
        }}
    ],
    }}
    """

    return prompt_content


# this is the short prompt above plus the output language from the previous output efforts
def createThePromptshortExcel(qde_content, paper_ID, this_paper,
                                   granularity=GRANULARITY,           # "sentence" or "paragraph"
                                    max_codes_per_unit=MAX_CODES_PER_UNIT,              # tighten if still overcoding
                                    max_codes_per_paper=MAX_CODES_PER_PAPER,
                                    min_confidence=MIN_CONFIDENCE):
    prompt_content = f"""
    I'm doing a research study. I have collected all of the conference papers (they were PDF, but I transformed them all to RTF) from all of the International Conference of the Learning Science meetings since 1996. I have 5,315 papers. 
    I want to analyze the evolution of and interaction between themes over time. I want to code all the data for themes, but not based on words (not lexical search). I coded 101 of the conference papers manually, and this process resulted in a robust codebook (attached). 
    Please analyze {this_paper} and tell me which codes apply in every category, and what sentence/paragraph you are using as evidence (use the title of the paper and the author affiliations if there are no other sources of evidence in the manuscript because the whole manuscript is your evidence).
    
    ## Inputs
    - CODEBOOK XML: {qde_content}
        - Codes are under <CodeBook><Codes>. Each <Code> has a unique GUID and a name/definition.
        - PAPER
    - GUID: {paper_ID}
    - TEXT: {this_paper}

    ## Output in a comma delimited file, .csv (STRICT)
   Please provide the following information, in a comma delimited format:
    - GUID
    - code unique ID
    - code name
    - and the sentence or paragraph from the paper that represents the code selected.

    
    """

    return prompt_content

# this is the short prompt above plus the output language from the previous output efforts
def createThePromptshortExcel2(qde_content, paper_ID, this_paper,
                                   granularity=GRANULARITY,           # "sentence" or "paragraph"
                                    max_codes_per_unit=MAX_CODES_PER_UNIT,              # tighten if still overcoding
                                    max_codes_per_paper=MAX_CODES_PER_PAPER,
                                    min_confidence=MIN_CONFIDENCE):
    prompt_content = f"""
    I'm doing a research study. I have collected all of the conference papers (they were PDF, but I transformed them all to RTF) from all of the International Conference of the Learning Science meetings since 1996. I have 5,315 papers. 
    I want to analyze the evolution of and interaction between themes over time. I want to code all the data for themes, but not based on words (not lexical search). I coded 101 of the conference papers manually, and this process resulted in a robust codebook (attached). 
    Please analyze {this_paper} and tell me which codes apply in every category, and what sentence/paragraph you are using as evidence (use the title of the paper and the author affiliations if there are no other sources of evidence in the manuscript because the whole manuscript is your evidence).
    For each code category, there is a code that indicates no codes in that category apply, please use that code if no other codes apply.
    
    ## Inputs
    - CODEBOOK XML: {qde_content}
        - Codes are under <CodeBook><Codes>. Each <Code> has a unique GUID and a name/definition.
        - PAPER
    - GUID: {paper_ID}
    - TEXT: {this_paper}

    ## Output in a comma delimited file, .csv (STRICT)
   Please provide the following information, in a comma delimited format:
    - GUID
    - code unique ID
    - code name
    - and the sentence or paragraph from the paper that represents the code selected.

    
    """

    return prompt_content


def readInWordCodebook(filename):
    extracted_text = docx2txt.process(filename)
    return extracted_text

# this is the short prompt above plus the output language from the previous output efforts, reads in Codebook from .docx file
def createThePromptshortExcel3(qde_content, paper_ID, this_paper,
                                   granularity=GRANULARITY,           # "sentence" or "paragraph"
                                    max_codes_per_unit=MAX_CODES_PER_UNIT,              # tighten if still overcoding
                                    max_codes_per_paper=MAX_CODES_PER_PAPER,
                                    min_confidence=MIN_CONFIDENCE):
    #qde_content_revised = readInWordCodebook(CODEBOOK_IN_WORD)
    #print(f"The codes: {qde_content_revised}")
    prompt_content = f"""
    I'm doing a research study. I have collected all of the conference papers (they were PDF, but I transformed them all to RTF) from all of the International Conference of the Learning Science meetings since 1996. I have 5,315 papers. 
    I want to analyze the evolution of and interaction between themes over time. I want to code all the data for themes, but not based on words (not lexical search). I coded 101 of the conference papers manually, and this process resulted in a robust codebook (attached). 
    Please analyze {this_paper} and tell me which codes apply in every category, and what sentence/paragraph you are using as evidence (use the title of the paper and the author affiliations if there are no other sources of evidence in the manuscript because the whole manuscript is your evidence).
    For each code category, at least one code should apply.  For each code category, there is a code that indicates no codes in that category apply, please use that code if no other codes apply.
    
    ## Inputs
    - CODEBOOK: {qde_content}
    - GUID: {paper_ID}
    - TEXT: {this_paper}

    ## Output in a comma delimited file, .csv (STRICT)
   Please provide the following information, in a comma delimited format:
    - GUID
    - code unique ID
    - code name
    - and the sentence or paragraph from the paper that represents the code selected.

    
    """

    return prompt_content

def createThePrompt20260209(qde_content, paper_ID, this_paper, learning_science_overview,
                            granularity=GRANULARITY,                            # "sentence" or "paragraph"
                            max_codes_per_unit=MAX_CODES_PER_UNIT,              # tighten if still overcoding
                            max_codes_per_paper=MAX_CODES_PER_PAPER,
                            min_confidence=MIN_CONFIDENCE):

    prompt_content = f"""

    Background: We are conducting an analysis of all conference papers from the International Conference of the Learning Sciences from 1996 until the present. We are coding each paper according to a detailed codebook. We are generally applying codes at the paragraph level except for when we apply codes to the title of the paper or the author names/affiliations. Often multiple codes in each category may be used. One paragraph may have multiple codes from the same or different categories applied to them. After a code has been used once, we don’t need to look for it again in the same paper. Some categories may not be stated but could be inferred. For example, in the geographical location if they don't mention where it was conducted, we look at the institution affiliations near the top of the paper and code them if appropriate. Another example is in the category of learning theories or the category of other theories, when the paper might not name the theory but they might cite people who make it obvious what theory they are using. We never code the references list. Every category in the codebook should be represented in each paper, so each category has a code for when no other codes in that category apply.

    LENA2 Coding Assistant is tailored to analyze papers, focusing on specific themes. All themes are associated with the Learning Sciences (remember that “the Learning Sciences” is a completely different field than “the Science of Learning”), and overview of the Learning Sciences is found in the file ({learning_science_overview}) 
        
        Step 1: It always starts by analyzing the codebook.  The codebook is located in ({qde_content}. The codebook is structured with many categories, and codes under each category. The codebook contains a definition paragraph about each category. Each code is listed with a name and a description.
        
        Step 2: It then analyzes the entire paper to understand the overall context.
        The paper is in the file ({this_paper}), and the paper GUID is ({paper_ID}).
        
        Step 3: LENA2 then determines which codes from the codebook must be applied somewhere in the paper, remembering that at least one code from each category in the codebook must be applied in each paper.
        a. It identifies the most relevant paragraph for each code that needs to be applied, remembering that after a code is used once in a paper it should not be used again. Every category in the codebook must be represented by application of at least one code in that category. If no relevant codes in a category are applicable, the null code for that category (e.g., “THRYOTHER - NO OTHER THEORIES MENTIONED”) should be applied to the title of the paper.
        b. LENA2 ensures all the codes are considered.
        c. For every code identified, LENA2 also identifies which paragraphs best match the codes it found, aligning them with codes strictly from the existing codebook which contains the name of the codes with a brief definition.
        This assistant provides coding by quoting 
        the exact paragraph and then referring only to the guid and the exact code names listed in the codebook, 
        such as 'guid="A8FDF7D5-91FA-43CA-97AF-FB7DA8A77DB4" name="ASSMNT - Affective Outcomes"', 
        'guid="2B887F2B-2CF1-4393-8A31-41737901F9EC" name="ASSMNT - Authentic Assessment"',
        or 'guid="0897F606-3A15-4092-9760-DBA29E0DD86C" name="COMMCOLAB - Community Partnerships"'
        d. It reports a confidence level (e.g., 'Confidence: 79%') for each code.
        e. It reports the start and end of the paragraph, referenced by indicating the number of characters from the start of the paper
        to the first character in the paragraph.  And also identifies the number of characters until the last character in the paragraph.
        f. It only uses the codes listed in the codebook exactly as written in the codebook (including spelling mistakes).
        g. Importantly, once a code is applied, do not use it again in the same paper.
        
        Step 4: After the paper is completely coded LENA2 also produces the results in a qdpx format.
        
        LENA2 Coding Assistant must output structured data in JSON format, which will later be converted into XML.
        The JSON structure should match this schema:

        {{
        "guid": "<guid of paper>",
        "plain_text_path": "<path>",
        "name": "<document name>",
        "creating_user": "402C8B2D-A9B1-4D7F-854C-7F1E14F390ED",
        "modifying_user": "402C8B2D-A9B1-4D7F-854C-7F1E14F390ED",
        "modified_datetime": "2024-03-08T14:34:57Z",
        "creation_datetime": "2024-03-08T14:34:57Z",
        "selections": [
            {{
            "guid": "<selection guid>",
            "creating_user": "402C8B2D-A9B1-4D7F-854C-7F1E14F390ED",
            "modifying_user": "402C8B2D-A9B1-4D7F-854C-7F1E14F390ED",
            "start_position": <start position>,
            "end_position": <end position>,
            "sentence": <sentence>,
            "creation_datetime": "2024-05-30T20:33:52Z",
            "modified_datetime": "2024-05-30T20:33:52Z",
            "coding": {{
                "creating_user": "402C8B2D-A9B1-4D7F-854C-7F1E14F390ED",
                "guid": "<coding guid>",
                "creation_datetime": "2024-05-30T20:33:52Z",
                "code_ref": {{
                "target_guid": "<code reference GUID>",
                "code_name": "<code name>"
                }}
            }}
            }}
        ]
        }}

        The output **must** be in this JSON format.
        """
    
    return prompt_content


# this outputs in csv format
def createThePrompt20260216(qde_content, paper_ID, this_paper, learning_science_overview,
                            granularity=GRANULARITY,                            # "sentence" or "paragraph"
                            max_codes_per_unit=MAX_CODES_PER_UNIT,              # tighten if still overcoding
                            max_codes_per_paper=MAX_CODES_PER_PAPER,
                            min_confidence=MIN_CONFIDENCE):

    prompt_content = f"""

    Background: We are conducting an analysis of all conference papers from the International Conference of the Learning Sciences from 1996 until the present. We are coding each paper according to a detailed codebook. We are generally applying codes at the paragraph level except for when we apply codes to the title of the paper or the author names/affiliations. Often multiple codes in each category may be used. One paragraph may have multiple codes from the same or different categories applied to them. After a code has been used once, we don’t need to look for it again in the same paper. Some categories may not be stated but could be inferred. For example, in the geographical location if they don't mention where it was conducted, we look at the institution affiliations near the top of the paper and code them if appropriate. Another example is in the category of learning theories or the category of other theories, when the paper might not name the theory but they might cite people who make it obvious what theory they are using. We never code the references list. Every category in the codebook should be represented in each paper, so each category has a code for when no other codes in that category apply.

    LENA2 Coding Assistant is tailored to analyze papers, focusing on specific themes. All themes are associated with the Learning Sciences (remember that “the Learning Sciences” is a completely different field than “the Science of Learning”), and overview of the Learning Sciences is found in the file ({learning_science_overview}) 
        
        Step 1: It always starts by analyzing the codebook.  The codebook is located in ({qde_content}. The codebook is structured with many categories, and codes under each category. The codebook contains a definition paragraph about each category. Each code is listed with a name and a description.
        
        Step 2: It then analyzes the entire paper to understand the overall context.
        The paper is in the file ({this_paper}), and the paper GUID is ({paper_ID}).
        
        Step 3: LENA2 then determines which codes from the codebook must be applied somewhere in the paper, remembering that at least one code from each category in the codebook must be applied in each paper.
        a. It identifies the most relevant paragraph for each code that needs to be applied, remembering that after a code is used once in a paper it should not be used again. Every category in the codebook must be represented by application of at least one code in that category. If no relevant codes in a category are applicable, the null code for that category (e.g., “THRYOTHER - NO OTHER THEORIES MENTIONED”) should be applied to the title of the paper.
        b. LENA2 ensures all the codes are considered.
        c. For every code identified, LENA2 also identifies which paragraphs best match the codes it found, aligning them with codes strictly from the existing codebook which contains the name of the codes with a brief definition.
        This assistant provides coding by quoting 
        the exact paragraph and then referring only to the guid and the exact code names listed in the codebook, 
        such as 'guid="A8FDF7D5-91FA-43CA-97AF-FB7DA8A77DB4" name="ASSMNT - Affective Outcomes"', 
        'guid="2B887F2B-2CF1-4393-8A31-41737901F9EC" name="ASSMNT - Authentic Assessment"',
        or 'guid="0897F606-3A15-4092-9760-DBA29E0DD86C" name="COMMCOLAB - Community Partnerships"'
        d. It reports a confidence level (e.g., 'Confidence: 79%') for each code.
        e. It reports the start and end of the paragraph, referenced by indicating the number of characters from the start of the paper
        to the first character in the paragraph.  And also identifies the number of characters until the last character in the paragraph.
        f. It only uses the codes listed in the codebook exactly as written in the codebook (including spelling mistakes).
        g. Importantly, once a code is applied, do not use it again in the same paper.
        
        Step 4: After the paper is completely coded LENA2 also produces the results in a csv format.
        
        ## Output in a comma delimited file, .csv (STRICT)
        Please provide the following information, in a comma delimited format:
            - GUID
            - code unique ID
            - code name
            - and the sentence or paragraph from the paper that represents the code selected.
        """
    
    return prompt_content