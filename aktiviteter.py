from datetime import datetime, date, timedelta
import json

aktiviteterArray = []

def init():
    getJSON()

def addTo(date, label):
    aktiviteterArray.append({date: label})
    saveJSON()

def removeUnwanted():
    removed_Amount = 0
    for e in aktiviteterArray:
        if datetime.now() >= datetime.strptime(next(iter(e)), "%Y-%m-%d %H:%M"):
            aktiviteterArray.remove(e)
            removed_Amount += 1
    saveJSON()

def saveJSON():
    with open('cached/aktiviteter.json', 'w') as outfile:
        json.dump(aktiviteterArray, outfile)

def getJSON():
    with open('cached/aktiviteter.json', 'r') as infile:
        json_data = infile.read()
        if json_data != "":
            t = json.loads(json_data)
            for element in t:
                aktiviteterArray[int(element)] = t[element]