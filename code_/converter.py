from objects import *
from xml.dom.minidom import parseString

# codebook1 = Codebook()
# codebook1.addCode("code1", "cat1", "desc1")
# codebook1.addCode("code2", "cat1")
# codebook1.addCode("code3", "cat1")
# codebook1.addCode("code4", "cat1", "desc2")
# codebook1.addCode("code1", "cat2")
# codebook1.addCode("code2", "cat2")
# codebook1.addCode("code3", "cat2")
# codebook1.addCode("code4", "cat2")
# codebook1.toString()

# sets = ["set1", "set2", "set3"]
# source1 = Source()
# source1.addSource("art1", "set1")
# source1.addSource("art2", "set1")
# source1.addSource("art3", "set2")
# source1.addSource("art4", "set2")

'''
source1.addCoding("art1" "code1", 30, 45)
source1.addCoding("art3" "code2", 23, 42)
'''

project = Project("Project3", "jwmcelde", "ExFiles")   # was "/home/jomac/projects/Donaldson/ExFiles"

project.addCode("code1", "cat1", "description1")
#project.addCode("code2", "cat1")
#project.addCode("code3", "cat1")
#project.addCode("code4", "cat1")
#project.addCode("code5", "cat2")
#project.addCode("code6", "cat2")
#project.addCode("code7", "cat2")
#project.addCode("code8", "cat2")

project.addSource("art1", "set1")
#project.addSource("art2", "set1")
#project.addSource("art3", "set2")
#project.addSource("art4", "set2")

# project.addSelection("art1", "code1", 30, 45)

project.createQDPX()
