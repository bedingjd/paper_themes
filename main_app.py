#
# this version utilizes openrouter.ai
# https://openrouter.ai/docs/quickstart

'''
python3 -m venv path/to/venv
source path/to/venv/bin/activate
python3 -m pip install xyz
'''

from config import *                            # import our configurations
#from config_by_sentence_20250619 import *       # import configs to code papers by sentence
#from config_by_para_20250623 import *           # import configs to code papers by paragraph

import os                                       # used for file info
import sys                                      # for input
import xml.etree.ElementTree as ET
import docx2txt
import pandas as pd                             # used to read-in Excel into Pandas Dataframe
#from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import xmltodict                                # used in qde_to_json to convert .qde to json
import json                                     # used in qde_to_json to convert .qde to json
import xml.etree.ElementTree as ET
from pydantic import BaseModel, Field
from google import genai
#import genai
from google.genai import types
#import google.generativeai as genai  # used for generate() function ?

from xml.dom import minidom
from datetime import datetime                   # for capturing current time, used for timing, and in log file names for example
import time                                     # for the wait function
import uuid

from datetime import datetime                   # so we can capture the current time for a timestamp

# needed to openrouter.ai use directly
import requests
import openai
from openai import OpenAI

import zipfile                                  # to unzip qdxp file

# import the items needed to convert AI output into MaxQDA project file
from code_.objects3 import *
import re                                           # for regular expressions

import shutil                                   # for file copy

import chardet                                  # to detect file character encodings automatically



# ====================================
# Set up key variables
# ====================================
#chosen_model = "gpt-4o-mini"
chosen_model = "o3-mini"
#chosen_model = "o3-mini-2025-01-31"
#chosen_model = "gpt-4o"
openrouter_model = "google/gemini-2.0-flash-lite-preview-02-05:free"            # this worked
openrouter_model = "deepseek/deepseek-r1:free"
openrouter_model="google/gemini-2.0-pro-exp-02-05:free"                         # https://openrouter.ai/google/gemini-2.0-pro-exp-02-05:free/api
#openrouter_model = "deepseek/deepseek-chat:free"                               # had to remove first message
temp = 0.7
my_max_tokens = 15000         # was 100, 4000, 7000 would not complete all the papers.  15000 worked


#sources_directory_path = "sources/"
# ======= end of key variables =======

# ======= classes to parse the output = (written by my AI overlords)
#import xml.etree.ElementTree as ET
#from xml.dom import minidom
#from datetime import datetime
#import uuid

class CodeRef:
    def __init__(self, target_guid, name):
        self.target_guid = target_guid
        self.name = name

    def to_xml(self):
        code_ref_element = ET.Element("CodeRef", targetGUID=self.target_guid, name=self.name)
        return code_ref_element


class Coding:
    def __init__(self, creating_user, guid, creation_datetime, code_ref, code_name):
        self.creating_user = creating_user
        self.guid = guid
        self.creation_datetime = creation_datetime
        self.code_ref = code_ref
        self.code_name = code_name

    def to_xml(self):
        coding_element = ET.Element("Coding", creatingUser=self.creating_user, guid=self.guid, creationDateTime=self.creation_datetime)
        coding_element.append(self.code_ref.to_xml())
        coding_element.append(self.code_name.to_xml())
        return coding_element


class PlainTextSelection:
    def __init__(self, creating_user, modifying_user, start_position, end_position, guid, creation_datetime, modified_datetime, coding):
        self.creating_user = creating_user
        self.modifying_user = modifying_user
        self.start_position = str(start_position)
        self.end_position = str(end_position)
        self.guid = guid
        self.creation_datetime = creation_datetime
        self.modified_datetime = modified_datetime
        self.coding = coding

    def to_xml(self):
        selection_element = ET.Element(
            "PlainTextSelection",
            creatingUser=self.creating_user,
            modifyingUser=self.modifying_user,
            startPosition=self.start_position,
            endPosition=self.end_position,
            guid=self.guid,
            creationDateTime=self.creation_datetime,
            modifiedDateTime=self.modified_datetime,
            name=f"{self.start_position},{self.end_position}",
        )
        selection_element.append(self.coding.to_xml())
        return selection_element


class TextSource:
    def __init__(self, creating_user, modifying_user, guid, plain_text_path, name, modified_datetime, creation_datetime, selections):
        self.creating_user = creating_user
        self.modifying_user = modifying_user
        self.guid = guid
        self.plain_text_path = plain_text_path
        self.name = name
        self.modified_datetime = modified_datetime
        self.creation_datetime = creation_datetime
        self.selections = selections

    def to_xml(self):
        text_source_element = ET.Element(
            "TextSource",
            creatingUser=self.creating_user,
            modifyingUser=self.modifying_user,
            guid=self.guid,
            plainTextPath=self.plain_text_path,
            name=self.name,
            modifiedDateTime=self.modified_datetime,
            creationDateTime=self.creation_datetime,
        )
        for selection in self.selections:
            text_source_element.append(selection.to_xml())
        return text_source_element


def prettify_xml(elem):
    """Generate a pretty-printed XML string."""
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

# ====================================



# Used to describe the output xml schema
class Book(BaseModel):
    title: str = Field(..., description="Title of the book")
    author: str = Field(..., description="Author of the book")
    isbn: str = Field(..., description="ISBN of the book")

# ====================================

# some classes to define the Structured Output desired
class CodeReference(BaseModel):
    target_guid: str
    code_name: str

class Coding(BaseModel):
    creation_datetime: str
    code_ref: CodeReference

class Codings(BaseModel):
    start_position: str
    end_position: str
    sentence: str
    coding: Coding

class PaperCoding(BaseModel):
    guid: str
    paper_name: str
    selections: list[Codings]
    #final_answer: str

# ====================================

# a function to determine the character encoding of a file
# idea from this search: https://www.bing.com/search?pglt=297&q=python+windows+UnicodeDecodeError%3A+%27charmap%27+codec+can%27t+decode+byte+0x9d+in+position+6445%3A+character+maps+to+%3Cundefined%3E&cvid=8b8cee47a9d64b1481fcd9767dd492f3&gs_lcrp=EgRlZGdlKgYIABBFGDkyBggAEEUYOTIHCAEQ6wcYQNIBCDQyODJqMGo3qAIAsAIA&FORM=ANNTA1&adppc=EDGEESS&PC=NMTS&source=chrome.ob
def getCharEncoding(file_path):
    with open(file_path, "rb") as raw:
        result = chardet.detect(raw.read(10000))
    encoding = result["encoding"]
    return encoding


# a function to read in text file
def read_text_file(file_path):
    with open(file_path, 'r', encoding=getCharEncoding(file_path)) as file:
        text = file.read()
    return text


# function to get a list of the source (papers) file names
def get_filenames(directory):
    """Gets a list of filenames from a directory.
    Args:
        directory: The path to the directory.
    Returns:
        A list of filenames in the directory.
    """

    filenames = []
    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)):
            filenames.append(filename)
    return filenames

# reads the papers into a dictionary where the key is the paper unique ID (file name sans extension),
#    and the value is the text of the paper
'''
def read_files_to_dict(directory):
    file_dict = {}
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            with open(filepath, 'r') as file:
                file_dict[filename] = file.read()
    return file_dict
'''

def read_files_to_dict(list_of_filenames, directory):
    file_dict = {}
    for filename in list_of_filenames:
        # just get the filename, no extension, this is the unique ID
        split_name = filename.split(".")
        short_name = split_name[0]
        # read in the file (paper)
        filepath = os.path.join(directory, filename)
        thisFile = read_text_file(filepath)
        # populate the dictionary with the short_name (unique ID), and thisFile (contents of the paper)
        file_dict[short_name] = thisFile
    return file_dict

def get_paper_IDs(list_of_filenames, directory):
    file_IDs = []
    for filename in list_of_filenames:
        # just get the filename, no extension, this is the unique ID
        split_name = filename.split(".")
        short_name = split_name[0]
        file_IDs.append(short_name)
    return file_IDs

# to read in the Learning Sciences Overview paper (in .rtf), or read in any .rtf file
def readInRTF_file(filename):
    with open(filename, "r", encoding=getCharEncoding(filename)) as file:
        raw_rtf_content = file.read()
    return raw_rtf_content



# analyze one paper via Gemini Google AI Pro
def analyze_one_paper(qde_content, paperID, this_paper):
    global MODEL_NAME

    prompt_content = createThePrompt(qde_content, paperID, this_paper)

    prompt_content8b = f"""
    LENA2 Coding Assistant is tailored to analyze papers, focusing on specific themes. 
    
    Step 1: It always starts by analyzing the codebook.  The cookbook is located in ({qde_content}), 
    and the codes are in the <CodeBook><Codes> section.  Each code is listed with a Unique Identification (ID) (guid), and a name.
    
    Step 2: It then reads the paper to understand the overall context.
    The paper Unique IDs (guid) is ({paper_ID})
    The paper content is ({this_paper}).
    
    Step 3: LENA2 then determines which codes from the codebook apply to the paper.
    At least five codes will be identifed for the paper
    LENA2 ensures all the codes are considered.
    At least one code from each code section will be identified for the paper
    For every code identified, LENA2 also identifies which sentences match the codes it found, aligning them with codes strictly from the existing codebook 
    which contains the name of the codes with a brief definition.
    This assistant provides coding by quoting 
    the exact sentence, or sentences and then referring only to the guid and the exact code names listed in the codebook, 
    such as 'guid="A8FDF7D5-91FA-43CA-97AF-FB7DA8A77DB4" name="ASSMNT - Affective Outcomes"', 
    'guid="2B887F2B-2CF1-4393-8A31-41737901F9EC" name="ASSMNT - Authentic Assessment"',
    or 'guid="0897F606-3A15-4092-9760-DBA29E0DD86C" name="COMMCOLAB - Community Partnerships"'
    It reports a confidence level (e.g., 'Confidence: 79%') for each code.
    It reports the start and end of the sentence, or sentences, referenced by indicating the number of characters from the start of the paper
      to the first character in the sentence.  And also identifies the number of characters until the last character in the sentence.
    It only uses the codes listed in the codebook exactly as written in the codebook (including spelling mistakes).  
    
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

    # ========== For Google AI Studio
    response = client.models.generate_content(
        #model="gemini-2.0-flash",
        #model="gemini-2.0-pro-exp-02-05",                      # this one used to work
        #model="gemini-2.5-flash-preview-04-17",                 # this is working 15 May 2025, list of models and rates at: https://ai.google.dev/gemini-api/docs/rate-limits
        model = MODEL_NAME,
        #model="gemini-2.0-flash-thinking-experimental-01-21",
        #model="gemini-2.0-flash-thinking-exp-01-21",
        contents=prompt_content,
        
        #generation_config = genai.types.GenerationConfig(
        #    temperature=1,
        #    top_p=0.95,
        #    top_k=40,
        #    max_output_tokens=8192,
        #    response_mime_type="text/plain",
        #
        #)
        

    )

    print(response.text)

    return response



# analyze one paper via Gemini Google AI Pro
def analyze_one_paper_via_code_category(qde_content, paperID, this_paper):
    global MODEL_NAME

    prompt_content = createThePromptByCodeCategory(qde_content, paperID, this_paper)

    # ========== For Google AI Studio
    response = client.models.generate_content(
        model = MODEL_NAME,
        contents=prompt_content,
        
        #generation_config = genai.types.GenerationConfig(
        #    temperature=1,
        #    top_p=0.95,
        #    top_k=40,
        #    max_output_tokens=8192,
        #    response_mime_type="text/plain",
        #
        #)
        

    )

    print(response.text)

    return response



# analyze one paper via OpenAI
def analyze_one_paper_via_code_category_via_openai(client, qde_content, paperID, this_paper):
    global MODEL_NAME_OPENAI

    #prompt_content = createThePromptByCodeCategory2(qde_content, paperID, this_paper)
    # This is the correct one:
    #prompt_content = createThePromptshort(qde_content, paperID, this_paper)
    #prompt_content = createThePromptshort2(qde_content, paperID, this_paper)  # <===== TODO: CHANGE THIS
                                                                                # was createThePromptshort
    #prompt_content = createThePromptshortExcel(qde_content, paperID, this_paper)
    #prompt_content = createThePromptshortExcel2(qde_content, paperID, this_paper)
    #prompt_content = createThePromptshortExcel3(qde_content, paperID, this_paper) # <====== this for csv output

    # read in the Learning Sciences Overview rtf file
    raw_learning_sciences = readInRTF_file(LEARNING_SCIENCES_OVERVIEW_FILENAME)
    #prompt_content = createThePrompt20260209(qde_content, paperID, this_paper, raw_learning_sciences)
    # for csv format
    prompt_content = createThePrompt20260216(qde_content, paperID, this_paper, raw_learning_sciences)

    # using this on 9 Feb 2026
    

    # ========== For Open AI
    '''
    response = client.responses.create(
        model = MODEL_NAME_OPENAI,
        #contents=prompt_content,
        #messages=prompt_content,
        #instructions=prompt_content,
        
        #generation_config = genai.types.GenerationConfig(
        #    temperature=1,
        #    top_p=0.95,
        #    top_k=40,
        #    max_output_tokens=8192,
        #    response_mime_type="text/plain",
        #
        #)
        input=[
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt_content},
            ]
        }]
        

    )

    #print(response.text)
    print(response)
    '''
    # this code example based on quickstart guide here: https://openrouter.ai/docs/quickstart
    json_schema = PaperCoding.model_json_schema()       # from example here: https://docs.vllm.ai/en/latest/features/structured_outputs/#online-serving-openai-api
    completion = client.chat.completions.create(                                                   # <====================

    #completion = client.responses.parse(
    #extra_headers={
        #"HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
        #"X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
    #},
    model=MODEL_NAME_OPENAI,
    messages=[
        {
        "role": "user",
        "content": prompt_content,
        "temperature": MODEL_TEMPERATURE,
        }
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "car-description",
            "schema": PaperCoding.model_json_schema()
        },
    },
    )
    
    print(f"This papers response is {completion.choices[0].message.content}")

    # just added this for llama rate limiting.                                  TODO: remove this later
    if MODEL_NAME_OPENAI == 'meta-llama/llama-3.2-3b-instruct:free':
        time.sleep(60)                # can only submit once per minute

    #exit()
    response = completion.choices[0].message.content
    return response




# Function to parse .qde file using the specified XML schema
def parse_qde(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        extracted_text = []
        
        # Extracting document contents based on the schema
        for document in root.findall(".//QDASoftware:Document", namespaces={"QDASoftware": "http://schema.qdasoftware.org/versions/Project/v1.0/Project.xsd"}):
            doc_title = document.get("Name", "Untitled")
            doc_content = document.find("QDASoftware:Content", namespaces={"QDASoftware": "http://schema.qdasoftware.org/versions/Project/v1.0/Project.xsd"}).text \
                          if document.find("QDASoftware:Content", namespaces={"QDASoftware": "http://schema.qdasoftware.org/versions/Project/v1.0/Project.xsd"}) is not None else ""
            extracted_text.append(f"Title: {doc_title}\n{doc_content}\n")
        
        return "\n".join(extracted_text)
    except Exception as e:
        print(f"Error parsing .qde file: {e}")
        return ""

# Function to parse project.qde file and parse to json
def parse_qde_to_json(file_path):
    """Parses a QDE (XML) file and converts it to JSON format."""
    
    tree = ET.parse(file_path)
    root = tree.getroot()

    def parse_element(element):
        """Recursively parses an XML element and converts it into a dictionary."""
        parsed_data = {
            "tag": element.tag,
            "attributes": element.attrib,
            "text": element.text.strip() if element.text else ""
        }
        
        children = [parse_element(child) for child in element]
        if children:
            parsed_data["children"] = children

        return parsed_data

    parsed_json = parse_element(root)

    return json.dumps(parsed_json, indent=4)


# another attempt to parse the project.qde file to json.  Using this one in the prompt
def qde_to_json(filepath):
    # Read XML file
    with open(filepath, encoding=getCharEncoding(filepath)) as xml_file:
        data_dict = xmltodict.parse(xml_file.read())

    # Convert to JSON
    json_data = json.dumps(data_dict)

    return json_data


# to log the response from the AI
def write_raw_data(timestamp_filename, content):
    with open(timestamp_filename, "a", encoding="utf-8") as f_temp:
        f_temp.write("\n=======================================================\n")
        f_temp.write(".......RAW DATA.......\n")
        f_temp.write(str(content))
    return

# to log the response from the AI, without any fancy lines
def write_just_raw_data(timestamp_filename, content):
    with open(timestamp_filename, "a", encoding="utf-8") as f_temp:
        f_temp.write(str(content))
    return


# determine if the OS is windows
def determine_if_windows():
    if os.name == 'nt':
        print("... using Windows OS")
        return True
    else:
        print("... using OS other than Windows")
        return False
    

# creates a copy of the file as a .zip, returns the name of the zip file
def copy_qdxp_file(filepath):
    # determine name to rename the file
    parts = filepath.split('.')
    copy_name = parts[0] + '.zip'
    if determine_if_windows():
        # it's windows, copy this way
        os.system(f'copy {filepath} {copy_name}')
    else:
        os.system(f'cp {filepath} {copy_name}')
    return copy_name


def unzip_qdxp_file(filepath):
    with zipfile.ZipFile(filepath, 'r') as zip_ref:
        zip_ref.extractall('.')

    return

def print_menu():
    print("\n======================================================")
    print("[1] (deprecated) Ask the AI to code the papers, one PAPER at a time")
    print("[2] (deprecated) Ask the AI to code the papers, one CODE CATEGORY at a time")
    print("[3] (deprecated) Convert the coded papers to a .qdxp file (if papers were coded one PAPER at a time)")
    print("[4] (deprecated) Convert the coded papers to a .qdxp file (if papers were coded one CATEGORY at a time)")
    print("[5] (deprecated) List currently available models (Gemini)")
    print("[6] Ask the AI to code the papers, one CODE CATEGORY at a time")
    print("[7] Convert the coded papers to a .qdxp file (if papers were coded one CATEGORY at a time via #6)")

    print("[9] Quit")

    return

# list all the Google models available
def listTheModels(client):
    # list the Google AI Studio models
    print("List of models that support generateContent:\n")
    for m in client.models.list():
        for action in m.supported_actions:
            if action == "generateContent":
                print(m.name)

    print("List of models that support embedContent:\n")
    for m in client.models.list():
        for action in m.supported_actions:
            if action == "embedContent":
                print(m.name)

# make a folder on the hard drive with the supplied folderName
def makeOutputFolder(folderName):
    # check to see if it exists
    if os.path.exists(folderName):
        return
    # if not, make the folder
    if determine_if_windows():
        # it's windows, copy this way
        os.system(f'mkdir {folderName}')
    else:
        os.system(f'mkdir {folderName}')
    return

# ==========================================================================
# these functions copied from convertOutput_three.py

# helper function to generate timestamp as string (for logging, file naming)
def generate_timestamp():
    # get current data and time for a timestamp
    current_datetime = datetime.now()
    #current_time = current_datetime.strftime("%H:%M:%S")
    current_time = current_datetime.strftime("%H%M")
    #current_date = current_datetime.strftime("%Y-%m-%d")
    current_date = current_datetime.strftime("%Y%m%d")
    timestamp = "" + str(current_date) + "_" + str(current_time)

    return timestamp


# helper function to log
def log_this(filename, content):
    timestamp = "At:  " + generate_timestamp() + "\n"
    with open(filename, "a", errors="ignore", encoding="utf-8") as f_temp:                            # *** we're ignoring encoding errors
        f_temp.write("\n=======================================================\n")
        f_temp.write(str(timestamp))
        f_temp.write(str(content))
    return


# function to get a list of the file names in a directory
def get_filenames(directory):
    """Gets a list of filenames from a directory.
    Args:
        directory: The path to the directory.
    Returns:
        A list of filenames in the directory.
    """
    filenames = []
    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)):
            # check to ensure we just look at the papers (not .DS_Store on mac)
            if filename.endswith(".txt") or filename.endswith(".xml"):              # <======= Just pulls out the .txt and .xml files
                filenames.append(filename)
    return filenames


# function to parse the output file, to just get the json part out of it
# returns 'None' if there was no json to split on
def parse_output_file(filename, path):
    with open(path+"/"+filename, encoding=getCharEncoding(filename)) as thisFile:
        text = thisFile.read()
        json_parts = str(text).split('json', 1)         # 'json' is the delimiter, 1 is the max number of splits
        #data_dict = xmltodict.parse(xml_file.read())
        
        #print(f"JUST THE JSON = {json_parts[1]}")
        #print('\n')
    
    '''
    if len(json_parts) == 1:
        return json_parts
    '''
    try:
        return json_parts[1].strip()
    except:
        print(f"----------------------------------------------------")
        print(f"ERROR: the file {filename} did not have a JSON split")
        print(f"----------------------------------------------------")
        return 'None'
    

# function to parse the output file, to just get the emergency Paper GUID out
# We added this to the file just in case the AI didn't provide it
# returns 'None' if there was no paper GUID
def parse_output_file_emergency_PaperGUID(filename, path):
    with open(path+"/"+filename, encoding=getCharEncoding(filename)) as thisFile:
        try:
            text = thisFile.read()
            indexOfStartOfGUID = str(text).find('Paper GUID:') + len('Paper GUID: ')
            indexOfStartOfLine = str(text).find('==')
            if (indexOfStartOfLine - indexOfStartOfGUID) > 36:
                stopPointDelta = 36
            else:
                stopPointDelta =  indexOfStartOfLine
            thisPaperGUID = str(text)[indexOfStartOfGUID : (indexOfStartOfGUID + stopPointDelta)].strip()
            print(f"This Emergency Paper GUID is |{thisPaperGUID}|")
            return thisPaperGUID

        except:
            print(f"----------------------------------------------------")
            print(f"ERROR: the file {filename} did not have an emergency Paper GUID")
            print(f"----------------------------------------------------")
            return 'None'
    

# used to read in the name of the paper from the source
def read_in_paper_name(file_path):
    try:
        with open(file_path, 'r', encoding=getCharEncoding(file_path)) as file:
            paper_name = file.readline()
            paper_name = paper_name.strip()                         # .strip() removes trailing newline characters
            print(f"Extracted the paper name as: {paper_name}") 
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return paper_name



# parses the project.qde file to json.  Using this to get the codebook info
def qde_to_json(filepath):
    # Read XML file
    with open(filepath, encoding=getCharEncoding(filepath)) as xml_file:
        data_dict = xmltodict.parse(xml_file.read())

    # Convert to JSON
    json_data = json.dumps(data_dict)

    return json_data


# Take the json (with demographic details) and split the codings from the front-end
def split_out_codings(the_json):
    parts = the_json.split('selections', 1)
    #print(f"The number of parts is {len(parts)}")
    if len(parts) < 2:
        front_end = None
        codings = None
    else:
        front_end = parts[0]
        codings = parts[1]
    return front_end, codings


# use regular expression pattern matching to just extract the pure json, all of it
def extract_pure_json(the_text):
    #pattern = "\".+\": \".+\""                          # this pattern looks for "<anything>": "<anything>"
    pattern = "{(?s:.)*}"                               # this pattern looks for {"<anything>"}
    for match in re.finditer(pattern, the_text):        # find the matches
        print(f"\ninside extract_pure_json(): THE MATCH for {{'<anything>'}} IS {match.group()}")
        return match.group()
        '''
        match_details = match.group().split(':')        # split at the : to get the key-value pair
        key = match_details[0]                          # set the key to 1st value (index = 0)
        key = key.replace('"', '')                      # remove "
        value = match_details[1]                        # set the value to the 2nd value (index = 1)
        value = value.replace('"', '').strip()          # remove " and any whitespace
        theCoding[key] = value                          # add key-value to the dictionary
        '''
    exit()
    
    # remove all the stuff we've already found
    remaining = re.sub(pattern, '', aCoding)
    return 


# creates a dictionary of key-value pairs based on the simple json provided
def parse_a_json_coding(aCoding):
    #print("\n\nInside parse_a_json_coding")
    theCoding = {}
    #pattern = "\"[a-zA-z0-9]+\": \"[a-zA-z0-9]+\""
    pattern = "\".+\": \".+\""                          # this pattern looks for "<anything>": "<anything>"
    for match in re.finditer(pattern, aCoding):         # find the matches
        #print(f"THE MATCH IS {match}")
        match_details = match.group().split(':')        # split at the : to get the key-value pair
        key = match_details[0]                          # set the key to 1st value (index = 0)
        key = key.replace('"', '')                      # remove "
        value = match_details[1]                        # set the value to the 2nd value (index = 1)
        value = value.replace('"', '').strip()          # remove " and any whitespace
        theCoding[key] = value                          # add key-value to the dictionary
    
    # remove all the stuff we've already found
    remaining = re.sub(pattern, '', aCoding)

    # find the start and stop numbers
    pattern_page_numbers = "\".+\": .+"                 # this pattern looks for "<anything>": <anything>
    for match in re.finditer(pattern_page_numbers, remaining):
        match_details = match.group().split(':')        # split at the : to get the key-value pair
        key = match_details[0]                          # set the key to 1st value (index = 0)
        key = key.replace('"', '')                      # remove "
        value = match_details[1]                        # set the value to the 2nd value (index = 1)
        value = value.replace(',', '').strip()                           # remove any commas and whitespace
        if key == 'start_position' or key == 'end_position':
            # convert from string to an int
            try:
                value = int(value)
            except:
                value = -1                              # there was an error in the number, so just make it -1
                pass
        theCoding[key] = value                          # add key-value to the dictionary


    # print(f"THIS PARSE DICTIONARY: {theCoding}")
    return theCoding



# creates a dictionary of key-value pairs based on the CodeBook json provided
def parse_a_CodeBook_json_coding(aCoding):
    #print(f"\n\nInside parse_a_CodeBook_json_coding with {aCoding}")
    theCoding = {}
    pattern = "\"@.+?\": \".+?\""                       # this pattern looks for "@<anything>": "<anything>"
    for match in re.finditer(pattern, aCoding):         # find the matches
        #print(f"......THE MATCH IS {match.group()}")

        match_details = match.group().split(':')        # split at the : to get the key-value pair
        key = match_details[0]                          # set the key to 1st value (index = 0)
        key = key.replace('"', '')                      # remove "
        key = key.replace('@', '')                      # remove the @
        value = match_details[1]                        # set the value to the 2nd value (index = 1)
        value = value.replace('"', '').strip()          # remove " and any whitespace
        theCoding[key] = value   

    print(f"...and the coding is {theCoding}")
    return theCoding
   


# use this function to pull out the CodeBook codes, if the CodeBook was imported via the qde
def parse_codebook_via_qde(codebook_content, project):
    theCodes = []                               # list to hold the codes
    '''
    The input is expected to be a lot of entries that look like the following:
    {"Codes": {"Code": [
    {"@isCodable": "true", 
    "@guid": "74143963-4753-47D0-865E-2373FC78996E", 
    "@name": "What Worked", 
    "@color": "#008c7c", 
    "Code": [
    {"@isCodable": "true", 
    "@guid": "C081CF73-DE5D-46E6-B86A-6AAE2614D049", 
    "@name": "WORKED - reflection - reflection contributed to learning", 
    "@color": "#6da529"},
    '''
    '''
    with open("look_at_qde.txt", "w") as file:
        file.write(codebook_content)
    '''
    
    # to pull out just the codes
    pattern = "\"CodeBook\": (.+) \"Sources\":"                     
    theCodesRaw = re.search(pattern, codebook_content).group()
    #print(f"...theCodes: {theCodesRaw}")

    '''
    # then each individual code
    theCodesSplit = theCodesRaw.split('}, {')
    print(f"...CODES SPLIT {theCodesSplit}")

    # pull out each code info individually
    count = 0
    for code in theCodesSplit:
        pattern_each_code = "\"@.+\": \".+\""           # this pattern looks for "@<anything>": <anything>
        for match in re.finditer(pattern_each_code, str(theCodesRaw)):
            #print(f"this match: {match.group()}")
            thisCode = {}
            match_details = match.group().split(':')        # split at the : to get the key-value pair
            key = match_details[0]                          # set the key to 1st value (index = 0)
            key = key.replace('"', '')                      # remove "
            value = match_details[1]                        # set the value to the 2nd value (index = 1)
            value = value.replace('"', '').strip()          # remove " and any whitespace
            thisCode[key] = value                           # add key-value to the dictionary
        theCodes.append(thisCode)
        if count == 0:
            print(f"...ALL THE CODES AT COUNT = 0 {theCodes}")
            count += 1

    #print(f"...ALL THE CODES: {theCodes}")
    '''

    '''
    ONE CODE
    "Code": [{"@isCodable": "true", 
    "@guid": "C081CF73-DE5D-46E6-B86A-6AAE2614D049", 
    "@name": "WORKED - reflection - reflection contributed to learning", 
    "@color": "#6da529"
    '''

    pattern_for_one = "[[]{.+}"
    for aMatch in re.finditer(pattern_for_one, str(theCodesRaw)):
        #print(f"...aMatch: {aMatch}")

        # ? is non greedy
        pattern_each_code = "\"@isCodable\": \".+?\", " \
        "\"@guid\": \".+?\", " \
        "\"@name\": \".+?\", " \
        "\"@color\": \".+?\""
        for match in re.finditer(pattern_each_code, str(aMatch.group())):
                #print(f"...this match: {match.group()}")
                thisCode = parse_a_CodeBook_json_coding(match.group())
                #print(f"...this match as dictionary: {thisCode}")
                theCodes.append(thisCode)
            


    return theCodes

# use this function to pull out the CodeBook codes, if the CodeBook was imported via the qde.
# This version of the function just pulls out all the Codes in mass, in xml.  It does not attempt
# to parse out each code.  This might be better for multiple levels of codes, since
# the function above, parse_codebook_via_qde(), just seems to work for one level
# of codes
def parse_codebook_via_qde3(codebook_file, project):                            # <======= good function here, used in most of the analysis
    theCodes = []                               # list to hold the codes
    '''
    The input is expected to be a lot of entries that look like the following:
    {"Codes": {"Code": [
    {"@isCodable": "true", 
    "@guid": "74143963-4753-47D0-865E-2373FC78996E", 
    "@name": "What Worked", 
    "@color": "#008c7c", 
    "Code": [
    {"@isCodable": "true", 
    "@guid": "C081CF73-DE5D-46E6-B86A-6AAE2614D049", 
    "@name": "WORKED - reflection - reflection contributed to learning", 
    "@color": "#6da529"},
    '''
    with open(codebook_file, encoding=getCharEncoding(codebook_file)) as xml_file:
        #print("\n=======================================================\n")
        #print(f"...THE XML FILE: {str(xml_file.read())}")
        # to pull out just the codes
        #pattern = "<CodeBook>.+</CodeBook>"
        pattern = r"<CodeBook>[\s\S]+</CodeBook>"                    
        theCodesRaw = re.search(pattern, str(xml_file.read()))
        theCodes = theCodesRaw.group()
        #print(f"...theCodes: {theCodes}")


    return theCodes

# use this function to pull out the CodeBook codes, if the CodeBook was imported via the .qdc file.
# This version of the function just pulls out all the Codes in mass, in xml.  It does not attempt
# to parse out each code.
def parse_codebook_via_qde3_qdc(codebook_file, project):                            # <======= used when the CodeBook is in a .qdc file with an off <CodeBook...> tag
    theCodes = []                               # list to hold the codes
    '''
    The input is expected to be a lot of entries that look like the following:
    {"Codes": {"Code": [
    {"@isCodable": "true", 
    "@guid": "74143963-4753-47D0-865E-2373FC78996E", 
    "@name": "What Worked", 
    "@color": "#008c7c", 
    "Code": [
    {"@isCodable": "true", 
    "@guid": "C081CF73-DE5D-46E6-B86A-6AAE2614D049", 
    "@name": "WORKED - reflection - reflection contributed to learning", 
    "@color": "#6da529"},
    '''
    with open(codebook_file, encoding=getCharEncoding(codebook_file)) as xml_file:
        #print("\n=======================================================\n")
        #print(f"...THE XML FILE: {str(xml_file.read())}")
        # to pull out just the codes
        #pattern = "<CodeBook>.+</CodeBook>"
        pattern = r"<CodeBook.+>[\s\S]+</CodeBook>"                    
        theCodesRaw = re.search(pattern, str(xml_file.read()))
        theCodes = theCodesRaw.group()
        #print(f"...theCodes: {theCodes}")


    return theCodes



# this finds String A inside String B.  It was initially written by ChatGPT, and modified slightly
def find_string_position(a: str, b: str):
    """
    Finds the position of string `a` in string `b`.
    
    Returns:
        A tuple (chars_before, chars_to_end):
            - chars_before: number of characters from the start of `b` to the start of `a`
            - chars_to_end: number of characters to the end of the string
            - (originally written with) chars_after: number of characters from the end of `a` to the end of `b`
    If `a` is not found in `b`, returns (-1, -1).
    """
    index = b.find(a)
    if index == -1:
        return -1, -1  # a not found in b
    
    chars_before = index
    #chars_after = len(b) - (index + len(a))
    chars_to_end = chars_before + len(a)
    return chars_before, chars_to_end


# since the AIs have trouble counting, this fixes the character counts in the AI response
def fix_the_character_counts(response, paper):

    # the following was the original idea, similar to the way we parse the output file
    '''
    front, codings = split_out_codings(response)

    # next three lines remove everything before and after the [ and ]
    just_codings = codings.split('[')
    just_codings = just_codings[1].split(']')
    just_codings = just_codings[0].strip()
    #just_codings = "[\n" + just_codings + "]"

    #the_codings = just_codings.split('},{')
    the_codings = just_codings.split('},')
    #print(f"THE CODINGS: {the_codings}")
    for coding in the_codings:
        #print(f"...THIS CODING IS: {coding}")
        
        this_coding_dictionary = parse_a_json_coding(coding)
        print(f"THIS PARSE DICTIONARY: {this_coding_dictionary}")
        log_this(LOG_FILE_NAME,f"Inside fix_the_character_counts ... THIS PARSE DICTIONARY: \n{this_coding_dictionary}")
        #source = short_name                                             # NOTE: may want to change this to GUID
        source = this_paper_guid

        # need to check to see if these exist first
        does_this_one_exist = True
        if 'sentence' in this_coding_dictionary:
            does_this_one_exist = True
        else:
            does_this_one_exist = False
        
        if does_this_one_exist:
            sentence = this_coding_dictionary['sentence']
            start = this_coding_dictionary['start_position']
            end = this_coding_dictionary['end_position']
            
            # find the correct character numbers
            new_start, new_end = find_string_position(sentence, paper)

            # Adjust the original response
            # TODO
    '''
    print("... fixing the response character counts")


    current_index = 0
    num_chars_to_look_backward = 70                     # since start and end are before the sentence, we need to back up a bit, I counted 68 charactersm but used 70 to be safe
    next_index = 0

    # first find the sentence
    look_for_sentence = 'sentence": "'
    next_index = response.find(look_for_sentence)                                   # find will return -1 if the sentence is not found
    while next_index >= 0:
        #print("===================================================")
        #print(f"...working sentence starting at index {next_index}")
        # skip to the actual sentence in the response
        start_of_sentence_index = next_index + len(look_for_sentence)               # this tells us where the sentence actually starts
        end_of_sentence_index = response.find('"', start_of_sentence_index)         # finds the ending "

        # extract the sentence
        sentence = response[start_of_sentence_index : end_of_sentence_index]
        #print(f"Found the sentence:\n{sentence[0:50]}")

        # find the correct start and end character counts
        real_start, real_end = find_string_position(sentence, paper)
        #print(f"=======> The correct start is {real_start}, and correct end is {real_end}")


        # replace the start and end numbers
        look_for_start = 'start_position": '
        look_for_end = 'end_position": '
        start_index = response.find(look_for_start, start_of_sentence_index - num_chars_to_look_backward) + len(look_for_start)       # 18 characters to the actual number
        start_end_index = response.find(',', start_index)
        end_index = response.find(look_for_end, start_end_index) + len(look_for_end)
        end_end_index = response.find(',', end_index)
        #print(f"The start and end positions are: {start_index} - {start_end_index}, {end_index} - {end_end_index}")
        #print(f"the original start number was: {response[start_index : start_end_index]}")
        #print(f"the original end number was: {response[end_index : end_end_index]}")
        
        response = response[:start_index] + str(real_start) + response[start_end_index : end_index] + str(real_end) + response[end_end_index :]
        #print("---------------------------------")
        #print(f"revised response is:\n{response}")

        # get ready to rinse and repeat
        next_index = response.find(look_for_sentence, end_of_sentence_index)        # set-up to look for the next sentence


    return response


# helper function to take an existing paper output file and update additional coding information
def update_Output_Data(originalContent, newContent):
    # split out just the json part

    # find the end of the old codes

    # parse out just the new codes

    # add the new codes to the old

    # put the file back together
    return


# helper function to take the qde content and pull out the code
# returns a dictionary with {key:value} like {category name : [list of code IDs]}
def get_the_codes(qde_content):

    return codes


# helper function to parse the qde file and add the Paper names, guid, and set
# information to the Project file.
def parse_paper_names_via_qde(qde_file, project, LOG_FILE_NAME):
    thePapers = []                               # list to hold the papers
    '''
    The input is expected to be a lot of entries that look like the following:
    <Sources>
        <TextSource modifyingUser="3F0A71EB-CE43-46D4-ADA2-06DA46E38FA7" plainTextPath="internal://1B9E8BA0-A4A6-4209-9F7A-FF7DCFAAD010.txt" creatingUser="3F0A71EB-CE43-46D4-ADA2-06DA46E38FA7" modifiedDateTime="2024-10-18T22:32:58Z" creationDateTime="2024-10-18T22:32:58Z" name="ICLS 2023 3-10" guid="1B9E8BA0-A4A6-4209-9F7A-FF7DCFAAD010"/>
        <TextSource modifyingUser="3F0A71EB-CE43-46D4-ADA2-06DA46E38FA7" plainTextPath="internal://9F02162D-6E68-4F51-94C7-0A4CA822F958.txt" creatingUser="3F0A71EB-CE43-46D4-ADA2-06DA46E38FA7" modifiedDateTime="2024-10-18T22:24:44Z" creationDateTime="2024-10-18T22:24:44Z" name="ICLS 2023 11-18" guid="9F02162D-6E68-4F51-94C7-0A4CA822F958"/>
        <TextSource modifyingUser="3F0A71EB-CE43-46D4-ADA2-06DA46E38FA7" plainTextPath="internal://20B4B8DA-8A2C-495E-B9CE-7C947DC1F976.txt" creatingUser="3F0A71EB-CE43-46D4-ADA2-06DA46E38FA7" modifiedDateTime="2024-10-18T22:29:40Z" creationDateTime="2024-10-18T22:29:40Z" name="ICLS 2023 19-26" guid="20B4B8DA-8A2C-495E-B9CE-7C947DC1F976"/>
        <TextSource modifyingUser="3F0A71EB-CE43-46D4-ADA2-06DA46E38FA7" plainTextPath="internal://DC97B695-3237-421D-9632-EDEB26A1EB73.txt" creatingUser="3F0A71EB-CE43-46D4-ADA2-06DA46E38FA7" modifiedDateTime="2024-10-18T21:04:45Z" creationDateTime="2024-10-18T21:04:45Z" name="ICLS 2008 8-9" guid="DC97B695-3237-421D-9632-EDEB26A1EB73"/>
        <TextSource modifyingUser="3F0A71EB-CE43-46D4-ADA2-06DA46E38FA7" plainTextPath="internal://EB6656B0-9F57-4015-8AC3-70E40F66B761.txt" creatingUser="3F0A71EB-CE43-46D4-ADA2-06DA46E38FA7" modifiedDateTime="2024-10-18T20:38:13Z" creationDateTime="2024-10-18T20:38:13Z" name="ICLS 2008 10-11" guid="EB6656B0-9F57-4015-8AC3-70E40F66B761"/>
    </Sources>
    <Sets>
        <Set name="ICLS 2023" guid="0097ADFA-F7EC-4386-ADBA-6C791BA205B5">
            <MemberSource targetGUID="1B9E8BA0-A4A6-4209-9F7A-FF7DCFAAD010"/>
            <MemberSource targetGUID="9F02162D-6E68-4F51-94C7-0A4CA822F958"/>
            <MemberSource targetGUID="20B4B8DA-8A2C-495E-B9CE-7C947DC1F976"/>
        </Set>
        <Set name="ICLS 2008" guid="2E2C3F6B-5E77-4C2E-9E3B-BFF0A8144D4E">
            <MemberSource targetGUID="DC97B695-3237-421D-9632-EDEB26A1EB73"/>
            <MemberSource targetGUID="EB6656B0-9F57-4015-8AC3-70E40F66B761"/>
        </Set>
    </Sets>
    '''

    
    with open(qde_file, encoding=getCharEncoding(qde_file)) as xml_file:
        xml_file_asString = str(xml_file.read())
        #print(f"XML_FILE is {xml_file_asString}")
    
        #print("looking at the ET")
        tree = ET.parse(qde_file)
        root = tree.getroot()
        #print("printing children of root")

        # get out the set info, create a dictionary matching guid to it's set
        setInfoDictionary = {}          # this is a paper GUID : set name
        setsDictionary = {}             # this is set guid : set name
        for child in root:
            #print(f" Tag: |{child.tag}|, attrib: |{child.attrib}|")
            if child.tag == "{urn:QDA-XML:project:1.0}Sets":
                for item in child.findall('{urn:QDA-XML:project:1.0}Set'): # Finds all elements with a specific tag
                    #print(f"All the Text Sources: {item.text}") # Prints the text content of the element
                    this_set_name = item.get('name')
                    this_set_guid = item.get('guid')
                    setsDictionary[this_set_guid] = this_set_name
                    for itm in item.findall('{urn:QDA-XML:project:1.0}MemberSource'):
                        #this_set_paper_name = itm.get('name')
                        this_set_paper_guid = itm.get('targetGUID')
                        setInfoDictionary[this_set_paper_guid] = this_set_name


        # get out the paper names and guids, and add them to the Project
        for child in root:
            #print(f" Tag: |{child.tag}|, attrib: |{child.attrib}|")
            if child.tag == "{urn:QDA-XML:project:1.0}Sources":
                #for childChild in child:
                    #print(f"        Tag: |{childChild.tag}|, attrib: |{childChild.attrib}|")
                for item in child.findall('{urn:QDA-XML:project:1.0}TextSource'): # Finds all elements with a specific tag
                    #print(f"All the Text Sources: {item.text}") # Prints the text content of the element
                    this_paper_name = item.get('name')
                    this_paper_guid = item.get('guid')
                    if this_paper_guid != '' and this_paper_name != '':
                            setName = 'set1'
                            # try to get the set name from the setInfoDictionary, if it doesn't exist, then just use the default setName above
                            try:
                                setName = setInfoDictionary[this_paper_guid]
                            except:
                                setName = 'set1'
                                pass
                            project.addSource(this_paper_guid, setName, this_paper_name)
                            print(f"...added paper from QDE file: {this_paper_guid}")
                            log_this(LOG_FILE_NAME,f"ADDING PAPER from QDE file: {this_paper_guid} : {this_paper_name}")

        '''
        for item in root.findall('TextSource'): # Finds all elements with a specific tag
                print(f"All the Text Sources: {item.text}") # Prints the text content of the element
        '''
    
    
        #pattern_sources = r"<Sources>[\s\S]+</Sources>"                    
        #theSourcesRaw = re.search(pattern_sources, str(qde_file.read()))
        #theSourcesRaw = re.search(pattern_sources, str(qde_file))
        #theSources = theSourcesRaw.group()
        
        #print(theSources)
    return




# ====================================
# start of main()
# ====================================
if __name__ == "__main__":

    # unzip the QDXP files
    print(f"Making a copy of {QDPX_NAME}")
    copy_name = copy_qdxp_file(QDPX_NAME)
    print(f"... as {copy_name}")
    print(f"... unzipping {copy_name}")
    unzip_qdxp_file(copy_name)

    # load keys and set-up the client
    # this version for Google AI Studio Gemini
    _ = load_dotenv(find_dotenv())
    client = genai.Client(
        api_key=os.environ.get('GEMINI_GOOGLE_AI_STUDIO'),
    )

    # this version for OpenRouter
    openRouterClient = OpenAI(
        base_url=BASE_URL,
        api_key=os.environ.get('OPEN_ROUTER_TEST_KEY'),
    )
    
    

    # set-up for user input
    user_desires = 0
    while user_desires != 9:

        # get user input
        print_menu()
        user_desires = int(input("Please enter your desire: "))
        print(f"...you entered {user_desires}")

        # execute the user's request
        if user_desires == 1:
            # ======================================================================================
            # Code the papers one at a time by paragraph
            # ======================================================================================
            

            # create a name for the log file
            LOG_FILE_NAME = "log_" + str(generate_timestamp()) + ".txt"

            # print a nice start message for the user
            current_datetime = datetime.now()
            current_time = current_datetime.strftime("%H:%M:%S")
            print(f"coding the papers one at a time, start time: {current_time}")

            # read in the qde content
            qde_content = qde_to_json("project.qde")
            #print(f"QDDE CONTENT...{qde_content}")

            # Read in the background paper  (not currently using this)
            #background = docx2txt.process("learning_theories.docx")

            # Read in the Codebook  (not currently using this, reading Codebook from qde)
            #df = pd.read_excel('codebook_small_3_5.xlsx')

            # Read in the paper file names
            paper_filenames = get_filenames(sources_directory_path)

            # create a dictionary with the paper unique ID as the key, and the paper text as the value
            all_the_papers = read_files_to_dict(paper_filenames, sources_directory_path)
            #print(f"All The Papers: {all_the_papers}")
            listOAllPaperIDs = get_paper_IDs(paper_filenames, sources_directory_path)
            #print(f"All the paper IDs: {listOAllPaperIDs}")

            # Start the loop.  Look at one paper at a time
            for paper_ID in listOAllPaperIDs:
                this_paper = all_the_papers[paper_ID]

                current_datetime = datetime.now()
                current_time = current_datetime.strftime("%H:%M:%S")
                print(f"...analyzing paper ID {paper_ID}, starting at {current_time}\n")
                #print(f"This Paper:\n{this_paper}")

                # seek the Oracle's wisdom on one paper
                resp = analyze_one_paper(qde_content, paper_ID, this_paper)

                if resp == None:
                    # we didn't get a response back
                    print("Sorry, no response to this paper {paper_ID}, please try this one again")
                    log_this(LOG_FILE_NAME,f"ERROR: No response from the AI for paper {paper_ID}")
                    continue

                #content = resp.choices[0].message.content     # for Gemini Pro 2.0 Experimental
                content = resp.text

                # fix the character counts, since apparently AIs can't count well
                content = fix_the_character_counts(content, this_paper)

                # get current data and time for a timestamp, used for the output file name
                current_datetime = datetime.now()
                #current_time = current_datetime.strftime("%H:%M:%S")
                current_time = current_datetime.strftime("%H%M")
                #current_date = current_datetime.strftime("%Y-%m-%d")
                current_date = current_datetime.strftime("%Y%m%d")
                timestamp_filename = "output_" + current_date + "_" + current_time + ".xml"

                print(f".......RAW OUTPUT.......{content}\n")
                print(f"...finished at {current_time}")

                makeOutputFolder(OUTPUT_FILES_PATH)
                timestamp_filename = OUTPUT_FILES_PATH + '/' + timestamp_filename

                # write the demographic data to a file
                with open(timestamp_filename, "w", encoding="utf-8") as f_temp:
                    f_temp.write(".......SAMPLE INFORMATION.......\n")
                    f_temp.write(f"Model: {openrouter_model}\n")                    # <========== change to 'chosen_model' is using open API
                    f_temp.write(f"Temperature: {temp}\n")
                    f_temp.write("\n=======================================================\n")

                    # write the raw data to a file
                write_raw_data(timestamp_filename, content)

        elif user_desires == 2:
            # ======================================================================================
            # Code the papers by coding category, one category at a time
            # ======================================================================================

            # create a name for the log file
            LOG_FILE_NAME = "log_" + str(generate_timestamp()) + ".txt"

            # print a nice start message for the user
            current_datetime = datetime.now()
            current_time = current_datetime.strftime("%H:%M:%S")
            print(f"coding the papers by coding category, start time: {current_time}")

            # read in the qde content
            qde_content = qde_to_json("project.qde")
            #print(f"QDDE CONTENT...{qde_content}")
            #exit()


            # Read in the paper file names
            paper_filenames = get_filenames(sources_directory_path)
            #print(f"Paper filenames: {paper_filenames}")

            # create a dictionary with the paper unique ID as the key, and the paper text as the value
            all_the_papers = read_files_to_dict(paper_filenames, sources_directory_path)
            #print(f"All The Papers: {all_the_papers}")
            #exit()


            listOAllPaperIDs = get_paper_IDs(paper_filenames, sources_directory_path)
            #print(f"All the paper IDs: {listOAllPaperIDs}")

            # make folder to write output files, if it doesn't already exist
            makeOutputFolder(OUTPUT_FILES_PATH)

            # start the loop by looping through each category of codes
            #raw_codes = getCodebookFromQDE(qde_content)
            # first parse the qde content as a dictionary
            json_as_dictionary = json.loads(qde_content)
            # pull out the project info
            proj = json_as_dictionary["Project"]
            # pull out the CodeBook
            codeBook = proj["CodeBook"]
            # pull out all the Codes and Code Categories
            codes = codeBook["Codes"]
            
            #keys = codes.keys()
            #print(f"Values\n{codes.values()}")

            # pull out all the Codes and Code Categories, for some reason Code is under Codes
            nextCodes = codes["Code"]
            #print(f"next codes \n{nextCodes}")

            # loop through each category of codes
            for codeCategory in nextCodes:
                #pretty_json = json.dumps(codeCategory, indent=4)
                #print(f"Item: \n{pretty_json}")
                #print(f"Code Category\n{codeCategory}")


                thisCategory = codeCategory["@name"]
                print(f"... Analyzing papers against the code category: {thisCategory}")
                log_this(LOG_FILE_NAME,f"... Analyzing papers against the code category: {thisCategory}")


                # Start the loop.  Look at one paper at a time
                for paper_ID in listOAllPaperIDs:
                    this_paper = all_the_papers[paper_ID]

                    current_datetime = datetime.now()
                    current_time = current_datetime.strftime("%H:%M:%S")
                    print(f"... Analyzing paper ID {paper_ID}, starting at {current_time}\n")
                    #print(f"This Paper:\n{this_paper}")

                    # seek the Oracle's wisdom on one paper
                    #resp = analyze_one_paper_via_code_category(qde_content, paper_ID, this_paper)
                    resp = analyze_one_paper_via_code_category(codeCategory, paper_ID, this_paper)

                    if resp == None:
                        # we didn't get a response back
                        print("Sorry, no response to this paper {paper_ID}, please try this one again")
                        log_this(LOG_FILE_NAME,f"ERROR: No response from the AI for paper {paper_ID}")
                        continue

                    #content = resp.choices[0].message.content     # for Gemini Pro 2.0 Experimental
                    content = resp.text

                    # fix the character counts, since apparently AIs can't count well
                    content = fix_the_character_counts(content, this_paper)

                    # set-up the output file name
                    current_date = current_datetime.strftime("%Y%m%d")
                    current_time_simple = current_datetime.strftime("%H%M%S")
                    timestamp_filename = "_" + current_date + "_" + current_time_simple + ".xml"

                    this_output_filename = OUTPUT_FILES_PATH + '/' + 'paperCodes_' + paper_ID + timestamp_filename

                    # original plan was to look to see if we've already logged this paper, if not, create an output file,
                    # then merge at the end, but currently, just outputting everything, and merging it
                    # when we create the project file
                    # NOTE: May have to deal with duplicate papers in the project file
                    '''
                    # look to see if we've already logged this paper, if not, create an output file
                    allTheCurrentOutputFiles = get_filenames(OUTPUT_FILES_PATH)
                    #print(f"All the current output files \n{allTheCurrentOutputFiles}")

                    if this_output_filename in allTheCurrentOutputFiles:
                        # we've already coded this paper with a previous code category
                        # if so, load the file, modify it, and save it

                        print("... updating existing output file with the results")

                        file = open(this_output_filename, "r")
                        originalContent = file.read()
                        newContent = update_Output_Data(originalContent, content)
                        write_just_raw_data(this_output_filename, newContent)

                    else:
                        # this is the first time we've coded this paper

                        print("... creating new output file with the results")

                        write_just_raw_data(this_output_filename, content)

                    '''

                    # output the reponse

                    # write out the paper unique ID, this is an emergency back-up in case the AI doesn't include it in the response
                    just_paper_id = 'Paper GUID: ' + paper_ID + '\n=======================================================\n'
                    write_just_raw_data(this_output_filename, just_paper_id)
                    # write the AI Response
                    write_just_raw_data(this_output_filename, content)

                    #exit()          # temp stop for debugging

                

        elif user_desires == 3:
            # ======================================================================================
            # Convert AI output to MaxQDA Project file (based on coding by paper)
            # ======================================================================================

            # create a name for the log file
            LOG_FILE_NAME = "log_" + str(generate_timestamp()) + ".txt"

            # 1. create a new Project
            project = Project(PROJECT_NAME, USER_NAME, EXFILES_PATH)

            # 2. Read in the list of papers and populate the sources section
            source_filenames = get_filenames(EXFILES_PATH)

            '''
            for source in source_filenames:
                # rmove the extension
                split_name = source.split(".")
                short_name = split_name[0]
                project.addSource(short_name, 'set1')                               # TODO: how do we want to handle sets?
            '''

            # 3. Read in the Codebook and populate the Codes
            print("\n==================================================================")
            if CODEBOOK_IN_QDE:
                '''
                # the codebook is in the QDE file, parse it to get the codebook info out
                codebook_content = qde_to_json(CODEBOOK_QDE_PATH)
                #print(f"...Codebook\n{codebook_content}")
                codebook_content_dictionary = parse_codebook_via_qde(codebook_content, project)
                #print(f"CODEBOOK CONTENT DICTIONARY: {codebook_content_dictionary}")
                for code in codebook_content_dictionary:
                    print(f"...THIS CODE: {code}")
                    try:
                        guid = code['guid']
                        name = code['name']
                        color = code['color']
                        project.addCode(name, "cat1", "", guid, color)            # note:  name vs description
                    except:
                        print(f"===> there was an error on this codebook_content_dictionary: {code}")
                        log_this(LOG_FILE_NAME, "===> there was an error on this codebook_content_dictionary: " + str(code))
                '''
                # get the codes from the .qde file
                all_the_codebook = parse_codebook_via_qde3(CODEBOOK_QDE_PATH, project)
                # add them to our project
                project.addAllCodesAsOnce(all_the_codebook)

                        


            else:
                # codebook is in the Excel file, parse it.  NOTE: these don't have Unique IDs
                df = pd.read_excel(CODEBOOK_EXCEL_PATH)

                # TODO
                print(f"...Codebook from Excel: \n{df}")
            # add codebook info to our project

            print("\n==================================================================")



            # 4. read in each output file
            # 4.a. first, get a list of all the output files.  NOTE: the filename is their Unique ID
            output_filenames =  get_filenames(OUTPUT_FILES_PATH)
            #print(f"list of all output file filenames: {output_filenames}")

            # 4.b. then read in each one, one at a time
            for file in output_filenames:
                if file.endswith(".xml"):               # sometimes Mac adds .ds files, we don't want those
                    # 4.c. pull out all the relevant information
                    output_json = parse_output_file(file, OUTPUT_FILES_PATH)

                    # there was no 'json' to split, so just log it and continue on with the next file
                    if output_json == 'None':
                        log_this(LOG_FILE_NAME,f"ERROR:  Missing 'json' in the response, so unable to split this response: {file}")
                        continue

                    #output_json = "[" + output_json + "]"
                    frontEnd, codings = split_out_codings(output_json)

                    # add the front_end, the article information as a new article
                    #print(f"THE FRONT END: {frontEnd}")
                    '''
                    This is all the info avail in the front end.  QUESTION:  Do we want to pass more of this on to the converter?
                    {
                    "guid": "2DF567D3-18CF-4264-BD9E-3AF0675F7D8D",
                    "plain_text_path": "internal://2DF567D3-18CF-4264-BD9E-3AF0675F7D8D.txt",
                    "name": "Critical Awareness as a Resource for Climate Change Connective and Productive Disciplinary Engagement",
                    "creating_user": "402C8B2D-A9B1-4D7F-854C-7F1E14F390ED",
                    "modifying_user": "402C8B2D-A9B1-4D7F-854C-7F1E14F390ED",
                    "modified_datetime": "2024-03-08T14:34:57Z",
                    "creation_datetime": "2024-03-08T14:34:57Z",
                    "
                    '''
                    frontEndDictionary = parse_a_json_coding(frontEnd)
                    #print(f"...FRONT END DICTIONARY {frontEndDictionary}")
                    try:
                        this_paper_guid = frontEndDictionary['guid']
                        this_paper_name = frontEndDictionary['name']
                    except:
                        print(f"----------------------------------------------------")
                        print(f"ERROR: the file {file} when converted to a dictionary did not have a 'guid' or 'name' key")
                        print(f"----------------------------------------------------")
                        log_this(LOG_FILE_NAME,f"ERROR:  the file {file} when converted to a dictionary did not have a 'guid' or 'name' key")
                        continue

                    # TODO:  get the correct short name
                    #project.addSource(short_name, 'set1', this_paper_guid)
                    project.addSource(this_paper_guid, 'set1', this_paper_name)
                    print(f"...added paper: {this_paper_guid}")
                    log_this(LOG_FILE_NAME,f"ADDING PAPER: {this_paper_guid} : {this_paper_name}")




                    
                    # then add the codings for that article
                    #codings = codings[:-4]      # remove last four characters, from ] to end
                    # next three lines remove everything before and after the [ and ]
                    just_codings = codings.split('[')
                    just_codings = just_codings[1].split(']')
                    just_codings = just_codings[0].strip()
                    #just_codings = "[\n" + just_codings + "]"

                    #the_codings = just_codings.split('},{')
                    the_codings = just_codings.split('},')
                    #print(f"THE CODINGS: {the_codings}")
                    for coding in the_codings:
                        #print(f"...THIS CODING IS: {coding}")
                        
                        this_coding_dictionary = parse_a_json_coding(coding)
                        print(f"THIS PARSE DICTIONARY: {this_coding_dictionary}")
                        log_this(LOG_FILE_NAME,f"THIS PARSE DICTIONARY: {this_coding_dictionary}")
                        #source = short_name                                             # NOTE: may want to change this to GUID
                        source = this_paper_guid

                        # need to check to see if these exist first
                        does_this_one_exist = True
                        if 'code_name' in this_coding_dictionary:
                            does_this_one_exist = True
                        else:
                            does_this_one_exist = False
                        
                        if does_this_one_exist:
                            code = this_coding_dictionary['code_name']                      # NOTE: May also need code GUID
                            start = this_coding_dictionary['start_position']
                            end = this_coding_dictionary['end_position']
                            target = this_coding_dictionary['target_guid']
                            log_this(LOG_FILE_NAME,f"...details: source: {source}, code: {code}, start: {start}, end: {end}, target: {target}")
                            #project.addSelection(source, code, start, end)
                            project.addSelectionWithKnownTargetGUID(source, target, start, end)
                    
                    #exit()
                    log_this(LOG_FILE_NAME,f"...PROJECT SELECTIONS: {project.sources.sources}")
                    
                    
                    # 5. add the information to our project

            

            # 6. create the file
            #print("\n==================================================================")
            #print(f"ALL THE CODES IN THE PROJECT: {project.codebook.categories}")
            print("\n==================================================================")
            print(f"...Project created with the following information:")
            project.createQDPX()
        
        elif user_desires == 4:
            # ======================================================================================
            # Convert AI output to MaxQDA Project file (based on coding by Category)
            # ======================================================================================

            # create a name for the log file
            LOG_FILE_NAME = "log_" + str(generate_timestamp()) + ".txt"

            # 1. create a new Project
            project = Project(PROJECT_NAME, USER_NAME, EXFILES_PATH)

            # 2. Read in the list of papers and populate the sources section
            source_filenames = get_filenames(EXFILES_PATH)

            '''
            for source in source_filenames:
                # rmove the extension
                split_name = source.split(".")
                short_name = split_name[0]
                project.addSource(short_name, 'set1')                               # TODO: how do we want to handle sets?
            '''

            # 3. Read in the Codebook and populate the Codes
            print("\n==================================================================")
            if CODEBOOK_IN_QDE:
                '''
                # the codebook is in the QDE file, parse it to get the codebook info out
                codebook_content = qde_to_json(CODEBOOK_QDE_PATH)
                #print(f"...Codebook\n{codebook_content}")
                codebook_content_dictionary = parse_codebook_via_qde(codebook_content, project)
                #print(f"CODEBOOK CONTENT DICTIONARY: {codebook_content_dictionary}")
                for code in codebook_content_dictionary:
                    print(f"...THIS CODE: {code}")
                    try:
                        guid = code['guid']
                        name = code['name']
                        color = code['color']
                        project.addCode(name, "cat1", "", guid, color)            # note:  name vs description
                    except:
                        print(f"===> there was an error on this codebook_content_dictionary: {code}")
                        log_this(LOG_FILE_NAME, "===> there was an error on this codebook_content_dictionary: " + str(code))
                '''
                # get the codes from the .qde file
                all_the_codebook = parse_codebook_via_qde3(CODEBOOK_QDE_PATH, project)
                # add them to our project
                project.addAllCodesAsOnce(all_the_codebook)

                # Add the Paper info (name, guid, set) to the Project
                parse_paper_names_via_qde(CODEBOOK_QDE_PATH, project, LOG_FILE_NAME)

                        


            else:
                # codebook is in the Excel file, parse it.  NOTE: these don't have Unique IDs
                df = pd.read_excel(CODEBOOK_EXCEL_PATH)

                # TODO
                print(f"...Codebook from Excel: \n{df}")
            # add codebook info to our project

            print("\n==================================================================")



            # 4. read in each output file
            # 4.a. first, get a list of all the output files.  NOTE: the filename is their Unique ID
            output_filenames = get_filenames(OUTPUT_FILES_PATH)
            #print(f"list of all output file filenames: {output_filenames}")

            # 4.b. then read in each one, one at a time
            # to ensure we onlt insert each paper once, let's start a list of all the paper GUIDs
            allThePapersUniqueList = []
            for file in output_filenames:
                log_this(LOG_FILE_NAME,f"DEBUG: This is the file name: {file}")
                if file.endswith(".xml") or file.endswith(".txt"):               # sometimes Mac adds .ds files, we don't want those
                    # pull out the back-up paper GUID
                    emergencyPaperGUID = parse_output_file_emergency_PaperGUID(file, OUTPUT_FILES_PATH)
                    #print(f"EMERGENCY PAPER GUID {emergencyPaperGUID}")
                    #exit()

                    # 4.c. pull out all the relevant information
                    output_json = parse_output_file(file, OUTPUT_FILES_PATH)

                    # there was no 'json' to split, so just log it and continue on with the next file
                    if output_json == 'None':
                        log_this(LOG_FILE_NAME,f"ERROR:  Missing 'json' in the response, so unable to split this response: {file}")
                        continue

                    #output_json = "[" + output_json + "]"
                    frontEnd, codings = split_out_codings(output_json)
                    if codings == None:
                        log_this(LOG_FILE_NAME,f"ERROR:  Missing codings in the response, so unable to include the response in this file: {file}")
                        continue

                    # add the front_end, the article information as a new article
                    #print(f"THE FRONT END: {frontEnd}")
                    '''
                    This is all the info avail in the front end.  QUESTION:  Do we want to pass more of this on to the converter?
                    {
                    "guid": "2DF567D3-18CF-4264-BD9E-3AF0675F7D8D",
                    "plain_text_path": "internal://2DF567D3-18CF-4264-BD9E-3AF0675F7D8D.txt",
                    "name": "Critical Awareness as a Resource for Climate Change Connective and Productive Disciplinary Engagement",
                    "creating_user": "402C8B2D-A9B1-4D7F-854C-7F1E14F390ED",
                    "modifying_user": "402C8B2D-A9B1-4D7F-854C-7F1E14F390ED",
                    "modified_datetime": "2024-03-08T14:34:57Z",
                    "creation_datetime": "2024-03-08T14:34:57Z",
                    "
                    '''
                    frontEndDictionary = parse_a_json_coding(frontEnd)
                    #print(f"...FRONT END DICTIONARY {frontEndDictionary}")
                    try:
                        this_paper_guid = frontEndDictionary['guid']
                        this_paper_name = frontEndDictionary['name']
                        print(f"THIS IS THE PAPER NAME {this_paper_name}")
                        log_this(LOG_FILE_NAME,f"THIS IS THE PAPER NAME {this_paper_name}")
                    except:
                        this_paper_guid = emergencyPaperGUID            # set to our emergency GUID
                        this_paper_name = emergencyPaperGUID            # set to our emergency GUID
                        print(f"HIT THE EXCEPTION, THIS IS THE PAPER NAME {this_paper_name}")
                        log_this(LOG_FILE_NAME,f"HIT THE EXCEPTION, THIS IS THE PAPER NAME {this_paper_name}")
                        print(f"----------------------------------------------------")
                        print(f"ERROR: the file {file} when converted to a dictionary did not have a 'guid' or 'name' key, using emergency GUID: {this_paper_guid}")
                        print(f"----------------------------------------------------")
                        log_this(LOG_FILE_NAME,f"ERROR:  the file {file} when converted to a dictionary did not have a 'guid' or 'name' key, using emergecny GUID: {this_paper_guid}")
                        continue
                        pass

                    # TODO:  get the correct short name
                    #project.addSource(short_name, 'set1', this_paper_guid)
                    # check first to ensure we haven't already added it
                    '''
                    # this is the old version
                    if file not in allThePapersUniqueList:
                        # and check to see that the name is not blank
                        if this_paper_guid != '' and this_paper_name != '':
                            project.addSource(this_paper_guid, 'set1', this_paper_name)
                            print(f"...added paper: {this_paper_guid}")
                            log_this(LOG_FILE_NAME,f"ADDING PAPER: {this_paper_guid} : {this_paper_name}")
                            allThePapersUniqueList.append(file)
                        else:
                            print(f"...this paper was not added since the guid or name was blank: |{this_paper_guid}|{this_paper_guid}|")
                            log_this(LOG_FILE_NAME,f"...this paper was not added since the guid or name was blank: |{this_paper_guid}|{this_paper_guid}|")
                            continue
                    else:
                        print(f"This paper is already included in the Project and will not be added again: {this_paper_guid}")
                        log_this(LOG_FILE_NAME,f"This paper already added, will not be added again: {this_paper_guid} : {this_paper_name}")
                    '''



                    
                    # then add the codings for that article
                    #codings = codings[:-4]      # remove last four characters, from ] to end
                    # next three lines remove everything before and after the [ and ]
                    just_codings = codings.split('[')
                    just_codings = just_codings[1].split(']')
                    just_codings = just_codings[0].strip()
                    #just_codings = "[\n" + just_codings + "]"

                    #the_codings = just_codings.split('},{')
                    the_codings = just_codings.split('},')
                    #print(f"THE CODINGS: {the_codings}")
                    for coding in the_codings:
                        #print(f"...THIS CODING IS: {coding}")
                        
                        this_coding_dictionary = parse_a_json_coding(coding)
                        print(f"THIS PARSE DICTIONARY: {this_coding_dictionary}")
                        log_this(LOG_FILE_NAME,f"THIS PARSE DICTIONARY: {this_coding_dictionary}")
                        #source = short_name                                             # NOTE: may want to change this to GUID
                        source = this_paper_guid

                        # need to check to see if these exist first
                        does_this_one_exist = True
                        if 'code_name' in this_coding_dictionary:
                            does_this_one_exist = True
                        else:
                            does_this_one_exist = False
                        
                        # add a little exception handling to this section in case the response doesn't contain one of these parts
                        code = start = end = target = ''
                        
                        if does_this_one_exist:
                            try:
                                code = this_coding_dictionary['code_name']                      # NOTE: May also need code GUID
                                start = this_coding_dictionary['start_position']
                                end = this_coding_dictionary['end_position']
                                target = this_coding_dictionary['target_guid']
                                log_this(LOG_FILE_NAME,f"...details: source: {source}, code: {code}, start: {start}, end: {end}, target: {target}")
                                #project.addSelection(source, code, start, end)
                                project.addSelectionWithKnownTargetGUID(source, target, start, end)
                            except:
                                log_this(LOG_FILE_NAME,f"...ERROR, UNABLE TO ADD THIS CODE BECAUSE SOME DETAILS WERE MISSING.  details: source: {source}, code: {code}, start: {start}, end: {end}, target: {target}")
                                pass
                    
                    #exit()
                    log_this(LOG_FILE_NAME,f"...PROJECT SELECTIONS: {project.sources.sources}")
                    
                    
                    # 5. add the information to our project

            

            # 6. create the file
            #print("\n==================================================================")
            #print(f"ALL THE CODES IN THE PROJECT: {project.codebook.categories}")
            print("\n==================================================================")
            print(f"...Project created with the following information:")
            project.createQDPX()

        elif user_desires == 5:
            # ======================================================================================
            # List the Models available
            # ======================================================================================
            listTheModels(client)

        elif user_desires == 6:
            # ======================================================================================
            # Code the papers by coding category, one category at a time using OPENROUTER
            # ======================================================================================

            # create a name for the folder to hold all our stuff, we'll just overwrite the variable in our config
            OUTPUT_FILES_PATH = "Output_" + PROJECT_NAME + "_" + str(generate_timestamp())
            # make folder to write output files, if it doesn't already exist
            makeOutputFolder(OUTPUT_FILES_PATH)
            # copy the config file
            shutil.copy2('config.py', OUTPUT_FILES_PATH)            # copy2 preserves the timestamp

            # create a name for the log file
            LOG_FILE_NAME = OUTPUT_FILES_PATH + "/" + "log_" + str(generate_timestamp()) + ".log"

            # print a nice start message for the user
            current_datetime = datetime.now()
            current_time = current_datetime.strftime("%H:%M:%S")
            print(f"coding the papers by coding category, using OpenRouter, start time: {current_time}")

            # log run description and start time
            log_this(LOG_FILE_NAME,f"RUN DESCRIPTION: {RUN_DESCRIPTION}")
            log_this(LOG_FILE_NAME,f"...start time: {current_time}")

            # read in the qde content
            qde_content = qde_to_json("project.qde")
            #print(f"QDDE CONTENT...{qde_content}")
            #exit()


            # Read in the paper file names
            paper_filenames = get_filenames(sources_directory_path)
            #print(f"Paper filenames: {paper_filenames}")

            # create a dictionary with the paper unique ID as the key, and the paper text as the value
            all_the_papers = read_files_to_dict(paper_filenames, sources_directory_path)
            #print(f"All The Papers: {all_the_papers}")
            #exit()


            listOAllPaperIDs = get_paper_IDs(paper_filenames, sources_directory_path)
            #print(f"All the paper IDs: {listOAllPaperIDs}")


            # start the loop by looping through each category of codes
            #raw_codes = getCodebookFromQDE(qde_content)
            # first parse the qde content as a dictionary
            json_as_dictionary = json.loads(qde_content)
            # pull out the project info
            proj = json_as_dictionary["Project"]
            # pull out the CodeBook
            codeBook = proj["CodeBook"]
            # pull out all the Codes and Code Categories
            codes = codeBook["Codes"]
            
            #keys = codes.keys()
            #print(f"Values\n{codes.values()}")

            # pull out all the Codes and Code Categories, for some reason Code is under Codes
            nextCodes = codes["Code"]
            #print(f"next codes \n{nextCodes}")
            

            # loop through each category of codes
            # let's just code 10 codes  <======================================== TODO: REMOVE THIS
            
            countTheCodes = 0
            for codeCategory in nextCodes:
                countTheCodes += 1
                '''
                if countTheCodes >= 10:
                    exit()
                '''
                #pretty_json = json.dumps(codeCategory, indent=4)
                #print(f"Item: \n{pretty_json}")
                #print(f"Code Category\n{codeCategory}")


                thisCategory = codeCategory["@name"]
                print(f"... Analyzing papers against the code category: {thisCategory}")
                log_this(LOG_FILE_NAME,f"... Analyzing papers against the code category: {thisCategory}")


                # Start the loop.  Look at one paper at a time
                for paper_ID in listOAllPaperIDs:
                    # **********************************************************
                    # this section added to only code one paper (or a few) and skip all the others
                    print(paper_ID)
                    codeThisPaper = False
                    if paper_ID == 'EB84B1CD-7263-4AD1-82D3-B229B7EE734A':
                        codeThisPaper = True
                    #elif paper_ID == 'DFBA1BB6-2213-427B-819D-35408645187D':
                    #    codeThisPaper = True
                    if not codeThisPaper:
                        continue

                    # **********************************************************
                    this_paper = all_the_papers[paper_ID]

                    current_datetime = datetime.now()
                    current_time = current_datetime.strftime("%H:%M:%S")
                    print(f"... Analyzing paper ID {paper_ID}, starting at {current_time}\n")
                    #print(f"This Paper:\n{this_paper}")

                    # seek the Oracle's wisdom on one paper
                    #resp = analyze_one_paper_via_code_category(qde_content, paper_ID, this_paper)
                    resp = analyze_one_paper_via_code_category_via_openai(openRouterClient, codeCategory, paper_ID, this_paper)
                    #print(f"This response is {resp}\n")


                    if resp == None:
                        # we didn't get a response back
                        print("Sorry, no response to this paper {paper_ID}, please try this one again")
                        log_this(LOG_FILE_NAME,f"ERROR: No response from the AI for paper {paper_ID}")
                        continue
                    

                    # just print the raw response for this test ================
                    # Uncomment this section out to output as csv (assuming the correct prompt is used)
                    # Also, uncomment the continue and exit below
                    #print(f"The response is: {resp}\n")
                    
                    log_this(LOG_FILE_NAME,f"{paper_ID} response is: {resp}\n")
                    csv_file_name = OUTPUT_FILES_PATH + "/" + "output_" + paper_ID + "_" + str(generate_timestamp()) + ".csv"
                    with open(csv_file_name, "a", errors="ignore", encoding="utf-8") as f_temp:
                        f_temp.write(str(resp))
                    
                    # ==========================================================

                    # added next line to stop once the csv raw response was output, so it didn't try to process it as xml
                    #exit()
                    #continue                                                   # <=== === = = === = = = *****


                    #content = resp.choices[0].message.content     # for Gemini Pro 2.0 Experimental
                    try:
                        content = resp.text
                    except:
                        # OpenRouterAI is already text
                        content = resp
                        pass

                    # fix the character counts, since apparently AIs can't count well
                    if MODEL_NAME_OPENAI != 'z-ai/glm-4.5-air:free':
                        content = fix_the_character_counts(content, this_paper)
                    # TODO I commented the line above to help glm.  Remove this comment for other models.

                    # set-up the output file name
                    current_date = current_datetime.strftime("%Y%m%d")
                    current_time_simple = current_datetime.strftime("%H%M%S")
                    timestamp_filename = "_" + current_date + "_" + current_time_simple + ".xml"

                    this_output_filename = OUTPUT_FILES_PATH + '/' + 'paperCodes_' + paper_ID + timestamp_filename

                    # original plan was to look to see if we've already logged this paper, if not, create an output file,
                    # then merge at the end, but currently, just outputting everything, and merging it
                    # when we create the project file
                    # NOTE: May have to deal with duplicate papers in the project file
                    '''
                    # look to see if we've already logged this paper, if not, create an output file
                    allTheCurrentOutputFiles = get_filenames(OUTPUT_FILES_PATH)
                    #print(f"All the current output files \n{allTheCurrentOutputFiles}")

                    if this_output_filename in allTheCurrentOutputFiles:
                        # we've already coded this paper with a previous code category
                        # if so, load the file, modify it, and save it

                        print("... updating existing output file with the results")

                        file = open(this_output_filename, "r")
                        originalContent = file.read()
                        newContent = update_Output_Data(originalContent, content)
                        write_just_raw_data(this_output_filename, newContent)

                    else:
                        # this is the first time we've coded this paper

                        print("... creating new output file with the results")

                        write_just_raw_data(this_output_filename, content)

                    '''

                    # output the reponse

                    # get the name of the paper so we can write to the output
                    this_paper_path = sources_directory_path + paper_ID + '.txt'
                    paper_name = read_in_paper_name(this_paper_path)

                    # write out the paper unique ID, this is an emergency back-up in case the AI doesn't include it in the response
                    just_paper_id = 'Paper GUID: ' + paper_ID + '\n' + \
                        'Paper Name: ' + paper_name + '\n' + \
                        'Model: ' + MODEL_NAME_OPENAI + '\n' + \
                        'Model Parameters: | MODEL_TEMPERATURE = ' + str(MODEL_TEMPERATURE) + ' | MAX_CODES_PER_UNIT = ' + str(MAX_CODES_PER_UNIT) + ' | MAX_CODES_PER_PAPER = ' + str(MAX_CODES_PER_PAPER) + ' | MIN_CONFIDENCE = ' + str(MIN_CONFIDENCE) + ' | GRANULARITY = ' + str(GRANULARITY) + '\n' + \
                        'Current Category: ' + thisCategory + '\n' + \
                        'Run Description: ' + RUN_DESCRIPTION + '\n=======================================================\njson'
                    write_just_raw_data(this_output_filename, just_paper_id)
                    # write the AI Response
                    write_just_raw_data(this_output_filename, content)

                    #exit()          # temp step for debugging
        elif user_desires == 7:
            # ======================================================================================
            # Convert AI output to MaxQDA Project file (based on coding by Category)
            # This version is based on the REVISED PROMPT, that adjusted 'Selections' to 'Codings'
            # ======================================================================================

            # create a name for the log file
            LOG_FILE_NAME = OUTPUT_FILES_PATH + "/" + "log_gen_proj_" + str(generate_timestamp()) + ".log"
            #LOG_FILE_NAME = OUTPUT_FILES_PATH + "/" + "log_" + str(generate_timestamp()) + ".log"

            # 1. create a new Project
            project = Project(PROJECT_NAME, USER_NAME, EXFILES_PATH)

            # 2. Read in the list of papers and populate the sources section
            source_filenames = get_filenames(EXFILES_PATH)

            # NOTE: including the paper names is inlcuded in line 2007 below: parse_paper_names_via_qde(CODEBOOK_QDE_PATH, project, LOG_FILE_NAME)
            # might need to add this code to the else in line 2009 (if the Codebook is not in the qde file)
            '''
            for source in source_filenames:
                # remove the extension
                split_name = source.split(".")
                short_name = split_name[0]
                project.addSource(short_name, 'set1')                               # TODO: how do we want to handle sets?
            '''

            # 3. Read in the Codebook and populate the Codes
            print("\n==================================================================")
            if CODEBOOK_IN_QDE:
                # get the codes from the .qde file
                #all_the_codebook = parse_codebook_via_qde3(CODEBOOK_QDE_PATH, project)
                # use this if the codes are in a .qdc file
                all_the_codebook = parse_codebook_via_qde3_qdc(CODEBOOK_QDE_PATH, project)      # <======
                # add them to our project
                project.addAllCodesAsOnce(all_the_codebook)
                # Add the Paper info (name, guid, set) to the Project
                parse_paper_names_via_qde(CODEBOOK_QDE_PATH, project, LOG_FILE_NAME)
            else:
                # codebook is in the Excel file, parse it.  NOTE: these don't have Unique IDs
                df = pd.read_excel(CODEBOOK_EXCEL_PATH)

                # TODO
                print(f"...Codebook from Excel: \n{df}")
            # add codebook info to our project
            print("\n==================================================================")

            # 4. read in each output file
            # 4.a. first, get a list of all the output files.  NOTE: the filename is their Unique ID
            output_filenames = get_filenames(OUTPUT_FILES_PATH)
            #print(f"list of all output file filenames: {output_filenames}")

            # 4.b. then read in each one, one at a time
            # to ensure we only insert each paper once, let's start a list of all the paper GUIDs
            allThePapersUniqueList = []
            for file in output_filenames:
                log_this(LOG_FILE_NAME,f"DEBUG: This is the file name: {file}")
                if file.endswith(".xml") or file.endswith(".txt"):               # sometimes Mac adds .ds files, we don't want those
                    # pull out the back-up paper GUID
                    try:
                        emergencyPaperGUID = parse_output_file_emergency_PaperGUID(file, OUTPUT_FILES_PATH)
                        #print(f"EMERGENCY PAPER GUID {emergencyPaperGUID}")
                    except:
                        continue

                    # 4.c. pull out all the relevant information
                    output_json = parse_output_file(file, OUTPUT_FILES_PATH)
                    #print(f"OUTPUT JSON: {output_json}")

                    # there was no 'json' to split, so just log it and continue on with the next file
                    if output_json == 'None':
                        log_this(LOG_FILE_NAME,f"ERROR:  Missing 'json' in the response, so unable to split this response: {file}")
                        continue

                    # pull out just the json
                    try:
                        just_the_json_extract = extract_pure_json(output_json)
                        #print(f"JUST THE JSON EXTRACT: {just_the_json_extract}")
                    except:
                        log_this(LOG_FILE_NAME,f"ERROR:  Unable to convert 'json' into 'just_the_json_extract'.  Likely no match for the regular expression {{'<everything>'}} for this file: {file}")
                        continue

                    # convert to a dictionary
                    try:
                        json_as_dict = json.loads(just_the_json_extract)
                        print(f"\nJSON as Dictionary: {json_as_dict}")
                        
                    except:
                        log_this(LOG_FILE_NAME,f"ERROR:  Unable to convert 'json' into 'json_as_dict' json dictionary for this file: {file}")
                        continue
                    #exit()
                    

                    '''
                    frontEnd, codings = split_out_codings(output_json)
                    if codings == None:
                        log_this(LOG_FILE_NAME,f"ERROR:  Missing codings in the response, so unable to include the response in this file: {file}")
                        continue

                    frontEndDictionary = parse_a_json_coding(frontEnd)
                    #print(f"...FRONT END DICTIONARY {frontEndDictionary}")
                    '''


                    try:
                        #this_paper_guid = frontEndDictionary['guid']
                        #this_paper_name = frontEndDictionary['name']
                        this_paper_guid = json_as_dict['guid']
                        #this_paper_name = json_as_dict['name']
                        this_paper_name = json_as_dict.get('name', 'unknown')
                        if this_paper_name == 'unknown':
                            this_paper_name = json_as_dict.get('paper_name', 'unknown')
                        print(f"THIS IS THE PAPER NAME {this_paper_name} and ID: {this_paper_guid}")
                        log_this(LOG_FILE_NAME,f"THIS IS THE PAPER NAME {this_paper_name} and ID: {this_paper_guid}")
                    except:
                        this_paper_guid = emergencyPaperGUID            # set to our emergency GUID
                        this_paper_name = emergencyPaperGUID            # set to our emergency GUID
                        print(f"HIT THE EXCEPTION, THIS IS THE PAPER NAME {this_paper_name}")
                        log_this(LOG_FILE_NAME,f"HIT THE EXCEPTION, THIS IS THE PAPER NAME {this_paper_name}")
                        print(f"----------------------------------------------------")
                        print(f"ERROR: the file {file} when converted to a dictionary did not have a 'guid' or 'name' key, using emergency GUID: {this_paper_guid}")
                        print(f"----------------------------------------------------")
                        log_this(LOG_FILE_NAME,f"ERROR:  the file {file} when converted to a dictionary did not have a 'guid' or 'name' key, using emergecny GUID: {this_paper_guid}")
                        #continue
                        #pass
                    #exit()


                    '''
                    # then add the codings for that article
                    #codings = codings[:-4]      # remove last four characters, from ] to end
                    # next three lines remove everything before and after the [ and ]
                    just_codings = codings.split('[')
                    just_codings = just_codings[1].split(']')
                    just_codings = just_codings[0].strip()
                    #just_codings = "[\n" + just_codings + "]"

                    #the_codings = just_codings.split('},{')
                    the_codings = just_codings.split('},')
                    #print(f"THE CODINGS: {the_codings}")
                    '''

                    # little debug
                    print(f"GUID: {this_paper_guid}, NAME: {this_paper_name}")
                    #exit()

                    do_we_have_codings = False
                    try:
                        #the_codings = json_as_dict['codings']
                        the_codings = json_as_dict.get('codings', 'unknown')
                        if the_codings == 'unknown':
                            print("...ERROR:  the word codings didnt work")
                            the_codings = json_as_dict.get('coding', 'unknown')
                        if the_codings == 'unknown':
                            print("...ERROR:  the word coding also didnt work")
                            the_codings = json_as_dict.get('selections', 'unknown')
                        print(f"\n THE CODINGS {the_codings}")
                    except: 
                        print(f"ERROR: There were no codings for ID: {this_paper_guid}, {this_paper_name}")
                        log_this(LOG_FILE_NAME,f"ERROR: There were no codings for ID: {this_paper_guid}, {this_paper_name}")

                        # added this next bit on 19 Feb 2026
                        '''
                        try:
                            the_codings = json_as_dict['coding']
                            log_this(LOG_FILE_NAME,f"Nice, the word (coding) worked: {this_paper_guid}, {this_paper_name}")
                        except:
                            print(f"ERROR: There were no codings for ID, (Coding) didn't work either: {this_paper_guid}, {this_paper_name}")
                            log_this(LOG_FILE_NAME,f"ERROR: There were no codings for ID, (Coding) didn't work either: {this_paper_guid}, {this_paper_name}")

                            try:
                                the_codings = json_as_dict['selections']
                                log_this(LOG_FILE_NAME,f"Nice, the word (selections) worked: {this_paper_guid}, {this_paper_name}")
                            except:
                                print(f"ERROR: There were no codings for ID, (Selections) didn't work either: {this_paper_guid}, {this_paper_name}")
                                log_this(LOG_FILE_NAME,f"ERROR: There were no codings for ID, (Selections) didn't work either: {this_paper_guid}, {this_paper_name}")

                                continue
                        '''
                    #print("just before exit")
                    #exit()

                    for coding in the_codings:
                        '''
                        A typical coding looks like this:
                        {'unit_index': 6, 
                        'text_span': 
                            {'start_char': 865, 
                            'end_char': 1067}, 
                        'evidence_quote': 'For consumers of research, evaluating the validity and reliability of data, and thus, inferring appropriate conclusions based on those data, also requires understanding the various ways that bias can come into play.', 
                        'code_ref': 
                            {'target_guid': '72E049E7-C721-4109-9A93-62686415D060', 
                            'code_name': 'THEME - Epistemic Cognition'}, 
                        'rubric': 
                            {'R1_evidence': True, 
                            'R2_alignment': True, 
                            'R3_exclusions_clear': True, 
                            'R4_specific': True}, 
                        'confidence': 0.8
                        }
                        '''
                        
                        '''
                        this_coding_dictionary = parse_a_json_coding(coding)
                        print(f"THIS PARSE DICTIONARY: {this_coding_dictionary}")
                        log_this(LOG_FILE_NAME,f"THIS PARSE DICTIONARY: {this_coding_dictionary}")
                        '''

                        print(f"...THIS CODING IS: {coding}")
                        log_this(LOG_FILE_NAME,f"Codings for paper {this_paper_guid} include: {coding}")

                        #source = short_name                                             # NOTE: may want to change this to GUID
                        source = this_paper_guid

                        '''
                        # need to check to see if these exist first
                        does_this_one_exist = True
                        if 'code_name' in this_coding_dictionary:
                            does_this_one_exist = True
                        else:
                            does_this_one_exist = False
                        
                        # add a little exception handling to this section in case the response doesn't contain one of these parts
                        code = start = end = target = ''
                        
                        if does_this_one_exist:
                            try:
                                code = this_coding_dictionary['code_name']                      # NOTE: May also need code GUID
                                start = this_coding_dictionary['start_position']
                                end = this_coding_dictionary['end_position']
                                target = this_coding_dictionary['target_guid']
                                log_this(LOG_FILE_NAME,f"...details: source: {source}, code: {code}, start: {start}, end: {end}, target: {target}")
                                #project.addSelection(source, code, start, end)
                                project.addSelectionWithKnownTargetGUID(source, target, start, end)
                            except:
                                log_this(LOG_FILE_NAME,f"...ERROR, UNABLE TO ADD THIS CODE BECAUSE SOME DETAILS WERE MISSING.  details: source: {source}, code: {code}, start: {start}, end: {end}, target: {target}")
                                pass
                        '''
                        # add a little exception handling to this section in case the response doesn't contain one of these parts
                        code = start = end = target = ''

                        try:
                            cod_ing = coding.get('coding', 'unknown')
                            ref = cod_ing.get('code_ref', 'unknown')
                            print(f"...ref is: {ref}")
                            #code = coding['code_ref']['code_name']                      # NOTE: May also need code GUID
                            #start = coding['text_span']['start_char']
                            #end = coding['text_span']['end_char']
                            #target = coding['code_ref']['target_guid']

                            code = ref.get('code_name', 'unknonw')
                            target = ref.get('target_guid', 'unknown')

                            start = ref.get('start_position', 0)
                            end = ref.get('end_position', 0)
                            
                            log_this(LOG_FILE_NAME,f"...details: source: {source}, code: {code}, start: {start}, end: {end}, target: {target}")
                            print(f"...details: source: {source}, code: {code}, start: {start}, end: {end}, target: {target}")

                            #project.addSelection(source, code, start, end)
                            project.addSelectionWithKnownTargetGUID(source, target, start, end)
                        except:
                            log_this(LOG_FILE_NAME,f"...ERROR, UNABLE TO ADD THIS CODE BECAUSE SOME DETAILS WERE MISSING.  details: source: {source}, code: {code}, start: {start}, end: {end}, target: {target}")
                            print(f"...ERROR, UNABLE TO ADD THIS CODE BECAUSE SOME DETAILS WERE MISSING.  details: source: {source}, code: {code}, start: {start}, end: {end}, target: {target}")
                            pass
                        #exit()
                    
                    log_this(LOG_FILE_NAME,f"...PROJECT SELECTIONS: {project.sources.sources}")
                    
                    
                    # 5. add the information to our project

            

            # 6. create the file
            #print("\n==================================================================")
            #print(f"ALL THE CODES IN THE PROJECT: {project.codebook.categories}")
            print("\n==================================================================")
            print(f"...Project created with the following information:")
            project.createQDPX()

    exit()


