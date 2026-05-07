'''
Reads in the .qde file, uses the codes from that file, the article coding from
the output files
'''


from objects3 import *
import json                                         # used in qde_to_json to convert .qde to json
import xmltodict                                    # used in qde_to_json to convert .qde to json
import os                                           # used for file info
import pandas as pd                                 # used to read-in Excel into Pandas Dataframe
import xml.etree.ElementTree as ET
import re                                           # for regular expressions
from datetime import datetime                   # so we can capture the current time for a timestamp
# to install any of these packages:  python3 -m pip install xyz
# this code also requires:
#   openpyxl                                        # used to read-in Excel cookbook
# NOTE: 
# 1. need to activate the virtual environment before running the code as it contains all the pre-reqs
#       source venv/bin/activate
# 2. Then run with:
#       python3 convertOutput.py
#
# QUESTIONS:
# a. for each artcile do we want name as it is right now (the file name), and another xml tag for the real name
#   of the article
# b.  Is there more info we want from the front_end?  Like save date or author guid?
# c. Do we need the ability to change some info items later?  Like change the value of the guid?
# d. Perhaps we should use the Article GUID instead of the Article name? Although file name may be the same.
# e. Do we need Code name and Code GUID?

PROJECT_NAME = 'Project9'
USER_NAME = 'jwmcelde'
EXFILES_PATH = 'ExFiles'                            # was "/home/jomac/projects/Donaldson/ExFiles"
OUTPUT_FILES_PATH = 'output_files'                  # folder is in the same directory.  
                                                    #    This is where the files from the AI are stored
# this section for Codebook information
CODEBOOK_IN_QDE = True                              # set to false if codebook is in Excel file
CODEBOOK_QDE_PATH = 'small_3_5/project.qde'         # path to qde file, with Codebook included.  Was Project5bb/project.qde 'resources/project.qde'
CODEBOOK_EXCEL_PATH = 'resources/codebook_small_3_5.xlsx'     # path to Excel file

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
    with open(filename, "a") as f_temp:
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
            filenames.append(filename)
    return filenames


# function to parse the output file, to just get the json part out of it
def parse_output_file(filename, path):
    with open(path+"/"+filename) as thisFile:
        text = thisFile.read()
        json_parts = str(text).split('json', 1)         # 'json' is the delimiter, 1 is the max number of splits
        #data_dict = xmltodict.parse(xml_file.read())
        
        #print(f"JUST THE JSON = {json_parts[1]}")
        #print('\n')
    return json_parts[1].strip()


# parses the project.qde file to json.  Using this to get the codebook info
def qde_to_json(filepath):
    # Read XML file
    with open(filepath) as xml_file:
        data_dict = xmltodict.parse(xml_file.read())

    # Convert to JSON
    json_data = json.dumps(data_dict)

    return json_data

def split_out_codings(the_json):
    parts = the_json.split('selections', 1)
    front_end = parts[0]
    codings = parts[1]
    return front_end, codings

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
            value = int(value)
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
def parse_codebook_via_qde3(codebook_file, project):
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
    with open(codebook_file) as xml_file:
        #print("\n=======================================================\n")
        #print(f"...THE XML FILE: {str(xml_file.read())}")
        # to pull out just the codes
        #pattern = "<CodeBook>.+</CodeBook>"
        pattern = r"<CodeBook>[\s\S]+</CodeBook>"                    
        theCodesRaw = re.search(pattern, str(xml_file.read()))
        theCodes = theCodesRaw.group()
        #print(f"...theCodes: {theCodes}")


    return theCodes



if __name__ == "__main__":
    # create a name for the log file
    LOG_FILE_NAME = "log_" + str(generate_timestamp()) + ".txt"

    # 1. create a new Project
    project = Project(PROJECT_NAME, USER_NAME, EXFILES_PATH)

    # 2. Read in the list of papers and populate the sources section
    source_filenames = get_filenames(EXFILES_PATH)
    for source in source_filenames:
        # rmove the extension
        split_name = source.split(".")
        short_name = split_name[0]
        project.addSource(short_name, 'set1')                               # TODO: how do we want to handle sets?

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
        # 4.c. pull out all the relevant information
        output_json = parse_output_file(file, OUTPUT_FILES_PATH)
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
        this_paper_guid = frontEndDictionary['guid']
        project.addSource(short_name, 'set1', this_paper_guid)
        print(f"...added paper: {this_paper_guid}")




        
        # then add the codings for that article
        #codings = codings[:-4]      # remove last four characters, from ] to end
        # next three lines remove everything before and after the [ and ]
        just_codings = codings.split('[')
        just_codings = just_codings[1].split(']')
        just_codings = just_codings[0].strip()
        #just_codings = "[\n" + just_codings + "]"
        #print(f"CODINGS: {just_codings}")
        the_codings = just_codings.split('},{')
        #print(f"THE CODINGS: {the_codings}")
        for coding in the_codings:
            #print(f"...THIS CODING IS: {coding}")
            this_coding_dictionary = parse_a_json_coding(coding)
            print(f"THIS PARSE DICTIONARY: {this_coding_dictionary}")
            log_this(LOG_FILE_NAME,f"THIS PARSE DICTIONARY: {this_coding_dictionary}")
            source = short_name                                             # NOTE: may want to change this to GUID
            code = this_coding_dictionary['code_name']                      # NOTE: May also need code GUID
            start = this_coding_dictionary['start_position']
            end = this_coding_dictionary['end_position']
            target = this_coding_dictionary['target_guid']
            log_this(LOG_FILE_NAME,f"..details: source: {source}, code: {target}, start: {start}, end: {end}, target: {target}")
            #project.addSelection(source, code, start, end)
            project.addSelectionWithKnownTargetGUID(source, target, start, end)
        log_this(LOG_FILE_NAME,f"...PROJECT SELECTIONS: {project.sources.sources}")
        
        # use ET to convert XML
        #tree = ET.fromstring(output_json)
        #root = tree.getroot()

        '''
        split_codings = just_codings.split('{')
        #print(f"SPLIT CODINGS: {split_codings}")
        all_codings_individually = []
        for coding in split_codings:
            #print(f"A CODING: {coding}")
            # parse the coding and add to the list
            this_coding = parse_a_json_coding(coding)
            #print(f"THIS PARSE DICTIONARY: {this_coding}")
            all_codings_individually.append(this_coding)
        '''

        '''
        # convert from string to dictionary
        json_parse = []
        #with open('output_json', 'r') as file:
        for line in output_json:
            print(f"This line: {line}")
            json_parse.append(json.loads(line))
        print(f"JSON PARSE: {json_parse}")
        output_json_dictionary = json.loads(output_json)
        # convert to pandas dataframe. We need to normalize the data since it's nested
        output_json_df = pd.DataFrame.from_dict(pd.json_normalize(output_json), orient='columns')
        print(f"pandas df of the cookbook: {output_json_df}")
        '''
        # 5. add the information to our project

    # 6. create the file
    #print("\n==================================================================")
    #print(f"ALL THE CODES IN THE PROJECT: {project.codebook.categories}")
    print("\n==================================================================")
    print(f"...Project created with the following information:")
    project.createQDPX()

