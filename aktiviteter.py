from datetime import datetime, date, timedelta
import json

aktiviteterArray = []
sortedArray = []

updated = False

def init():
    getJSON()

def addTo(id, date, text):
    global updated
    
    date = date.strftime("%Y-%m-%d %H:%M")
    
    try:
        # exists update
        if aktiviteterArray[id]:
            aktiviteterArray[id] = {"date": date, "text": text}
    except IndexError:
        aktiviteterArray.append({"date": date, "text": text})
        
    updated = True
    saveJSON()
    getJSON()

def removeFrom(id):
    try:
        aktiviteterArray.pop(id)
        saveJSON()
        getJSON()
    except Exception:
        pass

def removeUnwanted():
    global updated
    removed_Amount = 0
    for e in aktiviteterArray:
        if datetime.now() >= datetime.strptime(e["date"], "%Y-%m-%d %H:%M"):
            aktiviteterArray.remove(e)
            removed_Amount += 1
    if removed_Amount > 0:
        updated = True
        saveJSON()
        getJSON()

def saveJSON():
    with open('/home/pi/Desktop/OMirror/cached/aktiviteter.json', 'w') as outfile:
        json.dump(aktiviteterArray, outfile)

def getJSON():
    global aktiviteterArray, sortedArray
    with open('/home/pi/Desktop/OMirror/cached/aktiviteter.json', 'r') as infile:
        json_data = infile.read()
        if json_data != "":
            t = json.loads(json_data)
            
            # Empty list
            aktiviteterArray = []
            sortedArray = []
            
            for element in t:
                aktiviteterArray.append(element)
            
            sortedArray = sorted(aktiviteterArray, key=lambda k: datetime.strptime(k["date"], "%Y-%m-%d %H:%M"))

def isUpdated():
    global updated
    if updated:
        updated = False
        return True
    else:
        return False