from datetime import datetime, timezone
import uuid
import random

def getDateTime():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")

usedColors = []

def getHexColor():
    color = f"{random.randint(0, 0xFFFFFF):06X}".lower()

    while(color in usedColors):
        color = f"{random.randint(0, 0xFFFFFF):06X}".lower()

    usedColors.append(color)
    return color

usedGuids = []
def getGuid():
    guid = str(uuid.uuid4()).upper()

    while(guid in usedGuids):
        guid = str(uuid.uuid4()).upper()

    usedGuids.append(guid)
    return guid
