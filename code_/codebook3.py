from code_.utils import *
import random

class Code:
    def __init__(self, name, description = "", color = "", isCodable = True, guid = ""):
        self.name = name
        self.description = description
        self.color = color if color != "" else getHexColor()
        self.isCodable = isCodable
        self.guid = guid if guid != "" else getGuid()

    def setColor(self, color):
        self.color = color

    def toString(self):
        result = f"""<Code isCodable="true\" name="{self.name}" color="#{self.color}\" guid="{self.guid}\"   """

        if self.description == "":
            result += "> </Code>"                                  # NOTE: was '/>', Adjusted closing '>" and added closing </Code>

        else:
            result += f"><Description>{self.description}</Description></Code>"

        return result


class Codebook:
    def __init__(self):
        self.categories = {}
        self.bypassIndividualCodes = False
        self.allTheCodesInMass = ""

    #def addCategory(self, name):
        #if name not in categories: 
            #self.categories[name] = []

    def addCode(self, name, category, description = "", guid=getGuid(), color=""):
        #adds a new category, if the category hasn't been used
        if category not in self.categories: 
            self.categories[category] = [Code(name, description, color, guid)]

        #adds a category to the codes
        else:
            self.categories[category].append(Code(name, description, color, guid))

    def getCodeGuid(self, name):
        for codes in self.categories.values():  # Iterate through all code lists
            for code in codes:  # Iterate through each Code object
                if code.name == name:
                    return code.guid
        return None  # Return None if no match is found

    def catString(self, cat):
        #return f"""<Code guid="{getGuid()}" name="{cat}" color="#{getHexColor()}" isCodable="true"> </Code>"""          # NOTE: added closed </Code>
        return f"""<Code isCodable="true" name="{cat}" color="#{getHexColor()}" guid="{getGuid()}"> <Description>Unkown since this is a catagory</Description> </Code>"""          # NOTE: added closed </Code> and reordered

    # def codeString(self, cat, color):
    #     return f"""<Code isCodable="true" guid="{str(uuid.uuid4()).upper()}" name="{cat}" color="#{color}"/>"""

    def toString(self):
        # check to see if we've added the codes individually, or in mass
        if self.bypassIndividualCodes:
            return self.toStringInMass()
        else:
            result = ""  
            
            for cat in self.categories:
                #result += self.catString(cat)              # NOTE: removed the cat
                color = getHexColor()
                
                result += """<CodeBook><Codes>"""
                for code in self.categories[cat]:
                    code.setColor(color)
                    result += code.toString()
                    
                #     if code[1] != "":
                #         result += '\t\t' + f"<Description>{code[1]}</Description>\n"  
                
                #result += "</Code>"                                        # NOTE: Commented this line out
            result += """</Codes></CodeBook>"""
            return result
    

    # the following two functions are used to add all the codes at once, in mass
    # NOTE: this bypasses the categories data structure, so it may not be what we want
    # we may want to parse all the codes here
    def addAllCodesAtOnce(self, codes):
        self.bypassIndividualCodes = True
        self.allTheCodesInMass = codes

    def toStringInMass(self):
        return f""" {str(self.allTheCodesInMass)} """



