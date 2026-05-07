#from objects import text_source_to_string
from code_.utils import *

class Selection:
    def __init__(self, codeRef, start, end, userGuid):
        self.codeRef = codeRef
        self.start = start
        self.end = end
        self.userGuid = userGuid

    def toString(self):
        return selectionToString(self.userGuid, getGuid(), self.end, self.start, self.codeRef)

class Source:
    def __init__(self, textSourcePath, projectName):
        self.sources = {}
        self.textSourcePath = textSourcePath
        self.projectName = projectName

    def addSource(self, name, set, guid=getGuid()):                 # NOTE: modified to allow guid as parameter, or set as default by calling getGuid() like before
        if set not in self.sources:
            self.sources[set] = [(name, guid, [])]
        else:
            #                                                       NOTE: add check to see if the paper has already been added to this set
            notIncludedYet = True
            for (thisName, thisguid, thissources) in self.sources[set]:
                #print(f"THIS NAME {thisName}, GUID {guid} in self.sources[set]: {self.sources[set]}")
                if thisName == name:
                    notIncludedYet = False
            if notIncludedYet:
                 self.sources[set].append((name, guid, []))
            '''
            if name not in self.sources[set]:
                self.sources[set].append((name, guid, []))
            '''

    def addSelection(self, source, code, start, end, userGuid):
        all_sources = [name for sources in self.sources.values() for name, _, _ in sources]
        if source not in all_sources:
            raise ValueError(f"Source for {code} {start} {end} not found")

        for key, sources in self.sources.items():
            for i, (name, guid, selections) in enumerate(sources):
                if name == source:
                    self.sources[key][i][2].append(Selection(code, start, end, userGuid))

                    for item in self.sources[key][i][2]:
                        print(f"======>...self.sources[key][i][2] item = {item.toString()}")
                    
                    return


    def toString(self, userGuid):
        result = ""
        for set in self.sources:
            for source in self.sources[set]:
                if source[2] == []:
                    result += self.text_source_to_string(getDateTime(), source[0], userGuid, source[1], f"internal://{source[1]}.txt") + "/>"
                    # NOTE: Added the following when I didn't see the targetUID in the TextSource
                    '''
                    for selection in source[2]:
                        result += selection.toString()
                    result += "</TextSource>"
                    '''

                else:
                    result += self.text_source_to_string(getDateTime(), source[0], userGuid, source[1], f"internal://{source[1]}.txt") + ">"
                    for selection in source[2]:
                        result += selection.toString()
                    result += "</TextSource>"

        return result

    def createSourceFiles(self):

        all_sources = [(name, guid) for sources in self.sources.values() for name, guid, _ in sources]
        for source in all_sources:
            with open(f"{self.textSourcePath}/{source[0]}.txt", "r", encoding="utf-8") as file:
                fileContents = file.read()

            with open(f"./{self.projectName}/sources/{source[1]}.txt", "w") as sourceFile:
                sourceFile.write(fileContents)

    def text_source_to_string(self, time, name, user, guid, plain_text_path):
        return (f'<TextSource creationDateTime="{time}" '
            f'name="{guid}" '                                           # NOTE: was name
            f'modifiedDateTime="{time}" '
            f'modifyingUser="{user}" '
            f'guid="{name}" '                                           # NOTE: Was guid
            f'creatingUser="{user}" '
            f'plainTextPath="{plain_text_path}"')

    def setsToString(self):
        result = ""
        for set in self.sources:
            result += f"""<Set guid="{getGuid()}" name="{set}">"""
            for source in self.sources[set]:
                result += f"""<MemberSource targetGUID="{source[1]}" />"""
            result += "</Set>"
        return result

def selectionToString(user, guid, end_position, start_position, code_ref_target_guid):
    return f"""<PlainTextSelection creatingUser="{user}" modifiedDateTime="{getDateTime()}" guid="{guid}" modifyingUser="{user}" endPosition="{end_position}" startPosition="{start_position}" creationDateTime="{getDateTime()}" name="{start_position},{end_position}"><Coding creatingUser="{user}" guid="{getGuid()}" creationDateTime="{getDateTime()}"><CodeRef targetGUID="{code_ref_target_guid}" /></Coding></PlainTextSelection>"""

