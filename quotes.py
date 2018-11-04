import requests
import json
import random
from datetime import datetime, timedelta

# rss link
count_max = 10

api = "https://andruxnet-random-famous-quotes.p.mashape.com/?cat=famous&count=%i" % count_max

quoteArray = {}
date = None

def get_randomQuote():
    try:
        return quoteArray[random.randint(0, len(quoteAray)-1)]
    except Exception:
        return {"author": "-", "quote": "-", "date": "-"}

def get_Data():
    global quoteArray
    
    # check json
    getJSON()
    
    # Grab data only when 1 day has passed
    if date != None:
        if date + timedelta(hours=24) > datetime.now():
            return
    
    payload = {}
    
    headers2 = { "X-Mashape-Key": "GXdpPKkvT2msh6o4cTOkReQ3k2pGp1apsMbjsnFxVchoSW3IMz",
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json"}
    
    r = requests.post(api, data=payload, headers=headers2)
    
    data = {}
    
    data["date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    data["content"] = r.json()
    
    saveJSON(data)
    
def get_Date():
    return date

def saveJSON(data):
    with open('cached/quotes.json', 'w') as outfile:
        json.dump(data, outfile)

def getJSON():
    global date, quoteArray
    with open('cached/quotes.json') as infile:
        json_data = infile.read()
        if json_data != "":
            t = json.loads(json_data)
            for element in t:
                if element == "date":
                    date = datetime.strptime(t[element], "%Y-%m-%d %H:%M")
                else:
                    for i in range (0, count_max-1):
                        quoteArray[i] = t[element][i]