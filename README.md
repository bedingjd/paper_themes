# paper_themes
some python scripts to facilitate AI thematic coding of academic papers, and convert those codings to a MaxQDA project

# Set-up
### First time
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

#### If you want to use with Open Routeror other online platform.  Obtain an OpenAI API key
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
> python3 main_app.py


### TO-DO
- [ ] Check dependencies and see if they are still needed
- [ ] Are the following files in use?
  - '2025-06-16_ICLS_Conf_Themes_ALL_just10.zip'

### Some reconfigurations
- changed location to: QDPX_NAME = "references/2025-06-16_ICLS_Conf_Themes_ALL_just10.qdpx"  
- changed location to: LEARNING_SCIENCES_OVERVIEW_FILENAME = 'references/00_Learning_Sciences_Overview_converted.rtf'
