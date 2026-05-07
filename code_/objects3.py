from code_.utils import *
import os
import zipfile
from code_.codebook3 import *
from datetime import datetime, timezone
from code_.source2 import *
from xml.dom.minidom import parseString


#print(uuid.uuid4())
#Handle MAXQDA tag crap


#Contains everything

class Project:
    # consider combining codes and sets
    def __init__(self, cName, cUsername, cTextSourcePath):
        self.name = cName #Name of the project
        self.username = cUsername #Name of the User
        self.userGuid = getGuid()
        #TODO: assign guids and rename the files
        self.codebook = Codebook()
        self.sources = Source(cTextSourcePath, cName)

    def createQDPX(self):
        os.makedirs(self.name, exist_ok=True)
        os.makedirs(f"{self.name}/sources", exist_ok=True)
        projectString = self.toString()

        try:
            print("\n=======================================================")
            print(f"...PROJECT STRING: {projectString}")
            print("=======================================================")
            xml = parseString(projectString)
            projectBytes = xml.toprettyxml(indent="  ", encoding="utf-8")
            projectString = projectBytes.decode("utf-8")

        finally:

            with open(f"./{self.name}/project.qde", "w") as qdpxFile:
                qdpxFile.write(projectString)

            print(projectString)

        self.sources.createSourceFiles()

        folder_path = f"./{self.name}"
        zip_filename = f"{self.name}.qdpx"

        with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, folder_path))



    def toString(self):
        result = f"""<Project name="{self.name}" modifiedDateTime="{getDateTime()}" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" origin="MAXQDA 24 (Release 24.7.0)" xsi:schemaLocation="urn:QDA-XML:project:1.0 http://schema.qdasoftware.org/versions/Project/v1.0/Project.xsd" xmlns="urn:QDA-XML:project:1.0"><Users><User guid = "{self.userGuid}" name=\"{self.username}\" /></Users>"""   # NOTE: Re-ordered, removed: name=\"{self.username}\", capitalized B in CodeBook

        # add in codes
        result += self.codebook.toString()
        result += """<Sources>"""                            # NOTE: capitalized B in CodeBook
        
        # add in sources
        result += self.sources.toString(self.userGuid)
        
        '''
        result += "</Sources><Sets>"

        # add in Sets
        result += self.sources.setsToString()

        result += "</Sets></Project>"
        '''
        # NOTE: Modified this section to take out Sets
        result += "</Sources>"
        
        # add in Sets (if needed later)
        #result += "<Sets>"
        #result += self.sources.setsToString()
        #result += "</Sets>"

        result += "</Project>"

        return result


    def addCode(self, name, category, description = "", guid=getGuid(), color=""):    # NOTE: allow for passing in the guid, else it will be generated
        self.codebook.addCode(name, category, description, guid, color)

    def addSource(self, name, set, guid=""):                    # NOTE: allow for passing in the guid, else it will be generated in addSource()
        self.sources.addSource(name, set, guid)

    def addSelection(self, source, code, start, end):
        self.sources.addSelection(source, self.codebook.getCodeGuid(code), start, end, self.userGuid)   # NOTE: This was the old version

    def addSelectionWithKnownTargetGUID(self, source, code, start, end):
        self.sources.addSelection(source, code, start, end, self.userGuid)

    # useful when reading all the codes from a .qde file, saves effort of parsing each code
    # and adding the codes individually
    def addAllCodesAsOnce(self, codes):
        self.codebook.addAllCodesAtOnce(codes)

#Functions for generating strings
def code_to_string(name, is_codable, color, guid, description, sub_codes=None):
    if not sub_codes:
        return (f'<Code name="{name}" isCodable="{str(is_codable)}" color="{color}" guid="{guid}">'
                f'<Description>{description}</Description></Code>')
    else:
        result = (f'<Code name="{name}" isCodable="{str(is_codable)}" color="{color}" guid="{guid}">')
        for sub_code in sub_codes:
            result += code_to_string(**sub_code)
        result += "</Code>"
        return result

def text_source_to_string(creation_time, name, modified_datetime, modifying_user, guid, creating_user, plain_text_path):
    return (f'<TextSource creationDateTime="{creation_time}" '
            f'name="{name}" '
            f'modifiedDateTime="{modified_datetime}" '
            f'modifyingUser="{modifying_user}" '
            f'guid="{guid}" '
            f'creatingUser="{creating_user}" '
            f'plainTextPath="{plain_text_path}" />')

def plain_text_selection_to_string(creating_user, modifying_user, start_position, end_position, guid, modified_datetime, creation_datetime, code_ref_target_guid):
    return (f'   <PlainTextSelection creatingUser="{creating_user}" modifiedDateTime="{modified_datetime}" '
            f'guid="{guid}" modifyingUser="{modifying_user}" endPosition="{end_position}" '
            f'startPosition="{start_position}" creationDateTime="{creation_datetime}" '
            f'name="{start_position},{end_position}">'
            f'    <Coding creatingUser="{creating_user}" guid="{guid}" creationDateTime="{creation_datetime}">'
            f'     <CodeRef targetGUID="{code_ref_target_guid}"/>'
            f'    </Coding>'
            f'   </PlainTextSelection>')

def set_to_string(name, guid, member_sources=None):
    result = f'<Set name="{name}" guid="{guid}">'
    for member_guid in (member_sources or []):
        result += f'<MemberSource targetGUID="{member_guid}"/>'
    result += '</Set>'
    return result
