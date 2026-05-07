# paper_themes
some python scripts to facilitate AI thematic coding of academic papers, and convert those codings to a MaxQDA project

# Set-up
### First time
- This assumes the CodeBook and papers have been entered into MaxDQA, and exported
as a .qdpx file.  This file should be placed in the same folder as the main_app.py

#### Obtain an OpenAI API key
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
