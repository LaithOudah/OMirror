from pyowm.utils import timeformatutils
from datetime import datetime, date, timedelta
import pyowm
import json
import data

# set API
owm = None

# Set location, default Växjö, SE
loc = "Växjö,SE";

observation = None

owmSET = False

api = "681a848abbfde6c9da084c5e86d2a6f2"

city = ""

# Get forecast
observationArray = []
forecastArray = []
sortedArray = []

# up
updated = False

def init():
    global owm, observation, owmSET, updated
    try:
        owm = pyowm.OWM(api)
        
        setObservation()
        updated = True
        
        print("OWM Initialised")
        owmSET = True
    except Exception:
        owmSET = False

def setApi(api):
    global owm
    owm = pyowm.OWM(api)

def setObservation():
    global observation, loc, city
    data.readData()
    city = data.getData("weather_city")
    loc = city + ",SE"
    
    observation = owm.three_hours_forecast(loc)

def getCityName():
    return loc.split(",")[0]

def getObservation():
    global observationArray
    today = datetime.now() # Prevent bug from happening
    
    i = 0
    found = False
    while True:
        try:
            if i >= 4:
                return
            found = True
            observation.get_weather_at(today) 
            break
        except Exception:
            today -= timedelta(hours=1)
            i+=1
    if not found:
        while True:
            try:
                if i >= 8:
                    return
                observation.get_weather_at(today)
                break
            except Exception:
                today += timedelta(hours=1)
                i+=1
        
    today_2 = today
    
    # 4 for todayz
    # 4 for day 1,2,3,4
    observationArray = []
    for i in range (0, 8):
        if i == 0:
            observationArray.append(observation.get_weather_at(today))
        elif i > 0 and i < 4:
            observationArray.append(observation.get_weather_at(today + timedelta(hours=i*3)))
        else:
            today_3 = today_2 + timedelta(days=abs(3-i))
            observationArray.append(observation.get_weather_at(datetime(today_3.year, today_3.month, today_3.day, 14, 0, 0)))

#Convert status to swedish
def convertSwedish(status):
    if status == 800:
        return "Klar himmel"
    elif status == 801:
        return "Några moln"
    elif status == 802:
        return "Spridda moln"
    elif status == 803 or status == 804:
        return "Molnigt"
    elif status >= 300 and status <= 321:
        return "Duggregn"
    elif status >= 500 and status <= 502:
        return "Lätt regn"
    elif status >= 503 and status <= 531:
        return "Regn"
    elif status >= 200 and status <= 202:
        return "Storm med regn"
    elif status >= 210 and status <= 221:
        return "Storm"
    elif status >= 222 and status <= 232:
        return "Storm med duggregn"
    elif status >= 600 and status <= 622:
        return "Snöigt"
    elif status >= 701 and status <= 781:
        return "Dimmigt"
    else:
        return "Okänt"

def isNight():
    datenow = datetime.now()
    datetime_night1 = datetime(datenow.year, datenow.month, datenow.day, 19, 0, 0)
    datetime_night2 = datetime(datenow.year, datenow.month, datenow.day, 23, 59, 59)
    
    datetime_night1_2 = datetime(datenow.year, datenow.month, datenow.day, 0, 0, 0)
    datetime_night2_2 = datetime(datenow.year, datenow.month, datenow.day, 4, 0, 0)
    
    if (datenow >= datetime_night1 and datenow <= datetime_night2) or (datenow >= datetime_night1_2 and datenow <= datetime_night2_2):
        return True
    else:
        return False

def getImage(big, status):
    if status == 800:
        if big == 1:
            if isNight():
                return "weather_1_big_night"
            else:
                return "weather_1_big"
        else:
            return "weather_1_small"
    elif status == 801:
        if big == 1:
            if isNight():
                return "weather_2_big_night"
            else:
                return "weather_2_big"
        else:
            return "weather_2_small"
    elif status == 802:
        if big == 1:
            if isNight():
                return "weather_3_big_night"
            else:
                return "weather_3_big"
        else:
            return "weather_3_small"
    elif status == 803 or status == 804:
        if big == 1:
            return "weather_4_big"
        else:
            return "weather_4_small"
    elif status >= 300 and status <= 502:
        if big == 1:
            return "weather_8_big"
        else:
            return "weather_8_small"
    elif status >= 503 and status <= 531:
        if big == 1:
            return "weather_7_big"
        else:
            return "weather_7_small"
    elif status >= 200 and status <= 232:
        if big == 1:
            return "weather_9_big"
        else:
            return "weather_9_small"
    elif status >= 600 and status <= 622:
        if big == 1:
            return "weather_5_big"
        else:
            return "weather_5_small"
    elif status >= 701 and status <= 781:
        if big == 1:
            return "weather_6_big"
        else:
            return "weather_6_small"
    else:
        if big == 1:
            return "weather_1_big"
        else:
            return "weather_1_small"

# Create aray for weather variables
def getForecast():
    global updated, forecastArray, sortedArray
    
    placeHolder = []
    
    if len(observationArray) == 0:
        return
    
    for i in range (0, 8):
        temp = observationArray[i].get_temperature('celsius')
        
        sunrise = observationArray[i].get_sunrise_time('iso')
        sunset = observationArray[i].get_sunset_time('iso')
        
        day = observationArray[i].get_reference_time(timeformat='date').strftime("%A").capitalize()
        
        newData = { "status": observationArray[i].get_weather_code(),
                            "temp": temp["temp"],
                            "temp_max": temp["temp_max"],
                            "temp_min": temp["temp_min"],
                             "sunrise": sunrise,
                             "sunset": sunset,
                             "day": day,
                             "id": i
                            }
        try:
            if forecastArray[i] != newData:
                updated = True
        except Exception:
            pass
        
        placeHolder.append(newData)
    # saved cached version
    forecastArray = placeHolder
    sortedArray = forecastArray
    
    saveJSON()

def saveJSON():
    with open('cached/weather.json', 'w') as outfile:
        json.dump(forecastArray, outfile)

def getJSON():
    global forecastArray, sortedArray
    
    with open('cached/weather.json', 'r') as infile:
        json_data = infile.read()
        if json_data != "":
            t = json.loads(json_data)
            i = 0
            
            # EMpty list
            forecastArray = []
            sortedArray = []
            
            for element in t:
                forecastArray.append(element)
                i += 1
            
            # Sort list
            sortedArray = sorted(forecastArray, key=lambda k: k['id'])

def Updated():
    global updated
    if updated:
        updated = False
        return True
    else:
        return False

def updateAll():
    getObservation()
    getForecast()

init()
updateAll()