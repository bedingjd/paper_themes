# paper_themes
some python scripts to facilitate AI thematic coding of academic papers, and convert those codings to a MaxQDA project

### To run each time (after set-up is complete)
a. Start LM Studio, and the Model (in server mode)
  - Set the context window to 25,000 (or >18,000)
  - re-load model
b. Open config.py and ensure the settings are correct:
  - Project name
  - Model name
  - other config items as needed
c. If not already active, activate the virtual environment with:
 - Mac:
    > source venv/bin/activate
  - Windows:
    > venv\scripts\activate.bat
- Then run the code with:
> python main_app.py


## First time Set-up
- This assumes the CodeBook and papers have been entered into MaxDQA, and exported
as a .qdpx file.  This file should be placed in the same folder as the main_app.py

1. Install git for windows: https://git-scm.com/install/windows
  -	take all the default options. there are a lot of them
2. Install LM Studio: https://lmstudio.ai/
3. Install python3 for windows: https://www.python.org/downloads/windows/
  - under 'Stable Releases', I selected the latest, Python 3.13.13, and downloaded the 64bit windows installer
  - IMPORTANT: select 'add to path option' at the bottom
	- I just picked 'install now'
  - now we can open a command prompt (search for cmd, or Windows-R then type 'cmd', then press enter) and type 'python' to use python.  e.g. 'python --version'
4. download this git repo: git clone https://github.com/bedingjd/paper_themes.git
5. Open LM Studio and install a model
  - set up configuration as desired
  - set context window
6. Create python environment and install python dependncies
  - open a Command Window.  WINDOWSKEY-R, type in 'cmd', then hit enter
  - navigate to paper_themes folder (git repo)
 - If not already created, create a virtual environemnt with:
> python -m venv venv
  - Note: depending on the install, for this command, and all other commands, python3 might be needed instead of python, so this command might be:
    > python3 -m venv venv
- Activate the virtual environemnt with:
  - Mac:
    > source venv/bin/activate
  - Windows:
    > venv\scripts\activate.bat
- If any python libraries are missing, they can be installed with:
  - a pip update might be required / desired:
    > python.exe -m pip install --upgrade pip
  - via the requirements file provided
    > python -m pip install -r requirements.txt
  - or one at a time via:
> python -m pip install <library_name>
  - The following libraries are required:
    - config
    - os
    - xml.etree.ElementTree
    - docx2txt
    - pandas
    - OpenAI
    - dotenv
    - xmltodict
    - json
    - pydantic
    - from google import genai
    - xml.dom
    - datetime
    - uuid
    - requests
    - openai
    - zipfile
7. Check Python configuration 
  - open a Command Window.  WINDOWSKEY-R, type in 'cmd', then hit enter
  - navigate to paper_themes folder (git repo)
  - Open config.py in editor of choice
  - Check to ensure configuration items are correct
    - Name of project
    - IP address of LMStudio server
    - Name of model
8. Other Notes on the Configuration settings:
  - The prompt being used is in config.py as function: createThePrompt20260216()
  - For Option #6: sending the prompt to the AI:
    - CodeBook for option # 6 is: project.qde (make sure these have the latest codes)
  - For Option #7, formatting the AI responses into MaxQDA XML:
    - List of papers for option #7 is in the config.py variable: EXFILES_PATH
    - List of paper GUIDs for option #7 is in the config.py variable: CODEBOOK_QDE_PATH 
    - CodeBook for option#7 is in config.py variable: CODEBOOK_QDE_PATH
    - 


--------------------------------------------------------------------------------------------
#### If you want to use with Open Router or other online platform.  Obtain an OpenAI API key
Follow the instructions in the QuickStart instructions here: [https://platform.openai.com/docs/quickstart?language-preference=python&quickstart-example=completions](https://platform.openai.com/docs/quickstart?language-preference=python&quickstart-example=completions)
- Create an API Key
  - I do not recommend exporting the key as an environmental variable as described in the QuickStart

#### Set-up environment and install dependencies
- Place the API Key in a file called `.env`
  - Inside that file there should a line for each key:
> `GEMINI_GOOGLE_AI_STUDIO = "your_key_between_quotes"`


- Additionally, the `config.py` file should be checked to ensure all the settings
are as desired.
- If not already created, create a virtual environemnt with:
> python3 -m venv venv
- Activate the virtual environemnt with:
> source venv/bin/activate
- If any python libraries are missing, they can be installed with:
  - via the requirements file provided
    > python3 -m pip install -r requirements.txt
  - or one at a time via:
> python3 -m pip install <library_name>
  - The following libraries are required:
    - config
    - os
    - xml.etree.ElementTree
    - docx2txt
    - pandas
    - OpenAI
    - dotenv
    - xmltodict
    - json
    - pydantic
    - from google import genai
    - xml.dom
    - datetime
    - uuid
    - requests
    - openai
    - zipfile

#### Set-up the MaxQDA Files
- Unzip the qdxp file
- Place the .qde file in the same folder as main_app.py
- Place the contents of the qdxp /sources folder (the papers) in the /sources folder located in the same directory as main_app.py

### Each time, Run the code with:
- If not already active, activate the virtual environment with:
> source venv/bin/activate
- Then run the code with:
> python main_app.py
---------------------------------------------------------------------------------------------------------------------------------


### TO-DO
- [ ] Check python import dependencies and see if they are still needed
- [ ] Are the following files in use?
  - '2025-06-16_ICLS_Conf_Themes_ALL_just10.zip'
- [ ] Remove the restriction to just code one paper in lines 1952-1958
- [ ] Ensure option #7 can run right after option #6
  - The code needs to remember the variable: OUTPUT_FILES_PATH = 'Output_Proj_gemma_4_31_20060509a_20260509_1652'

### Some reconfigurations
- In order to clean up the file structure, I adjusted the location of serveral files
  - changed location to: QDPX_NAME = "references/2025-06-16_ICLS_Conf_Themes_ALL_just10.qdpx"  
  - changed location to: LEARNING_SCIENCES_OVERVIEW_FILENAME = 'references/00_Learning_Sciences_Overview_converted.rtf'
  - changed location to: CODEBOOK_QDE_PATH = 'references/project_with_generated_codes.qde'
- to fix encoding errors: 
  - in main_app.py, line 655: with open(filename, "a", errors="ignore") as f_temp: 
    - we're ignoring any encoding errors
    - same with line 1982: with open(csv_file_name, "a", errors="ignore") as f_temp:
  - Set all writes to utf-8 encoding
    - encoding="utf-8"
    - Line 552: with open(timestamp_filename, "a", encoding="utf-8") as f_temp:
    - Line 560: with open(timestamp_filename, "a", encoding="utf-8") as f_temp:
    - Line 655:  with open(filename, "a", errors="ignore", encoding="utf-8") as f_temp: 
    - Line 1332: with open(timestamp_filename, "w", encoding="utf-8") as f_temp:
    - Line 1982:  with open(csv_file_name, "a", errors="ignore", encoding="utf-8") as f_temp:
    - In objects3.py, Line 41:  with open(f"./{self.name}/project.qde", "w", encoding="utf-8") as qdpxFile:
    - In source2.py, Line 81: with open(f"./{self.projectName}/sources/{source[1]}.txt", "w", encoding="utf-8") as sourceFile:
- NOTE:  creating the MaxQDA Project file requires: 'project_with_generated_codes.qde'
  - [ ] I think I created this file so a Unique ID was assigned to every paper, that matched the one expeceted my MaxQDA.  Do I need to modify this file to support all the papers?
- [ ] Need to fix code so that after you run Option #6, you don't need to modify the config file to run Option #7
  - The code needs to remember the variable: OUTPUT_FILES_PATH = 'Output_Proj_gemma_4_31_20060509a_20260509_1652'
- [x] TO-FIX: coding for paper 'B7A' start and end character positions are incorrect.  They aren't even numbers
  - 1F4 has commas instead of numbers
  - main_app.py Lines 2321, 2322 gets the character counts from the 'code-ref' when sometimes the character counts are in the main 'coding'
    - FIX THIS by adding a check to see if the character counts are in the top level, or if not, look for them in the lower level.
      - Might also be able to fix this with structured responses from the AI, to ensure the coding always comes back in the same spot/location in the xml
      - Or might be able to fix this when we correct the coding, to make sure the character counts are placed in the correct spot/location in the xml
- [ ] TO-FIX: source2.py line 39, 40.  'source' is not found in 'all_sources' so we should probably add it to sources instead of just throwing an error
  - Perhaps also log that we did this?
  - When we throw an exception here it returns to main_app.py line 2329 and begins to run the thrown exception.
  - Also, why was this paper not included in the original list of papers?  Is it not in the project.qde file?
  - Finally, how can we continue on to log the other codes?
- [ ] TODO: create a new project.qde file ensuring both the latest CodeBook and all papers are in there
- 


