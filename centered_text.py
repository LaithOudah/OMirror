from datetime import datetime, date, timedelta
import json

centeredArray = []

def init():
    getJSON()

def addTo(timeStart, timeEnd, text):
    centeredArray.append({'text': text, 'timeStart': timeStart, 'timeEnd': timeEnd})
    saveJSON()

def removeFrom(id):
    centeredArray.pop(id)
    saveJSON()

def getFromTime():
    timeNow = datetime.now()
    
    for e in centeredArray:
        timeStart = datetime.strptime(e['timeStart'], "%H:%M")
        timeEnd = datetime.strptime(e['timeEnd'], "%H:%M")
        if timeNow.hour >= timeStart.hour and timeNow.hour <= timeEnd.hour:
            if timeNow.hour == timeStart.hour and timeNow.minute < timeStart.minute:
                return 0
            elif timeNow.hour == timeEnd.hour and timeNow.minute > timeEnd.minute:
                return 0
            return e['text']
        elif timeStart.hour > timeEnd.hour:
            if timeNow.hour >= timeStart.hour:
                if timeNow.hour == timeStart.hour and timeNow.minute < timeStart.minute:
                    return 0
                return e['text']
            elif timeNow.hour <= timeEnd.hour:
                if timeNow.hour == timeEnd.hour and timeNow.minute > timeEnd.minute:
                    return 0
                return e['text']
    return 0

def saveJSON():
    with open('/home/pi/Desktop/OMirror/cached/centered_text.json', 'w') as outfile:
        json.dump(centeredArray, outfile)

def getJSON():
    global centeredArray
    with open('/home/pi/Desktop/OMirror/cached/centered_text.json', 'r') as infile:
        json_data = infile.read()
        if json_data != "":
            t = json.loads(json_data)
            # EMpty list
            centeredArray = []
            
            for element in t:
                centeredArray.append(element)