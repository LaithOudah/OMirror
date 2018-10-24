from datetime import datetime, date, timedelta
import json

centeredArray = []

def init():
    getJSON()

def addTo(timeStart, timeEnd, text):
    centeredArray.append({'text': label, 'timeStart': timeStart, 'timeEnd': timeEnd})
    saveJSON()

def removeFrom(id):
    centeredArray.pop(id)

def getFromTime():
    timeNow = dateTime.now().strftime("%H:%M")
    
    for e in aktiviteterArray:
        timeStart = datetime.strptime(e['timeStart']), "%H:%M")
        timeEnd = datetime.strptime(e['timeEnd']), "%H:%M")
        if timeNow >= timeStart && timeNow <= timeEnd:
            return e['text']
    return 0

def saveJSON():
    with open('cached/centered_text.json', 'w') as outfile:
        json.dump(centeredArray, outfile)

def getJSON():
    with open('cached/centered_text.json', 'r') as infile:
        json_data = infile.read()
        if json_data != "":
            t = json.loads(json_data)
            for element in t:
                centeredArray[int(element)] = t[element]