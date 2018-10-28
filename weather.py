from pyowm.utils import timeformatutils
from datetime import datetime, date, timedelta
import pyowm
import json

# set API
owm = None

# Set location, default Växjö, SE
loc = "Växjö,SE";

observation = None

owmSET = False

cord_x = 0
cord_y = 0
api = "681a848abbfde6c9da084c5e86d2a6f2"

# Get forecast
observationArray = {}
forecastArray = {}

# up
updated = False

def init():
    global owm, observation
    try:
        owm = pyowm.OWM(api)
        
        observation = owm.three_hours_forecast(loc)
        
        owmSET = True
    except Exception:
        owmSET = False

def setApi(api):
    global owm
    owm = pyowm.OWM(api)

def setObservation(obs):
    global observation
    observation = owm.three_hours_forecast(obs)

def getCityName():
    return loc.split(",")[0]

def getObservation():
    today = datetime.now() + timedelta(hours=1) # Prevent bug from happening
    today_2 = today
    
    # 4 for today
    # 4 for day 1,2,3,4
    for i in range (0, 8):
        if i == 0:
            observationArray[i] = observation.get_weather_at(today)
        elif i > 0 and i < 4:
            observationArray[i] = observation.get_weather_at(today + timedelta(hours=(i-1)*3))
        else:
            today_3 = today_2 + timedelta(days=abs(3-i))
            observationArray[i] = observation.get_weather_at(datetime(today_3.year, today_3.month, today_3.day, 14, 0, 0))

#Convert status to swedish
def convertSwedish(status):
    if status == "Clear sky".capitalize():
        return "Klar himmel"
    elif status == "few clouds".capitalize():
        return "Några moln"
    elif status == "scattered clouds".capitalize():
        return "Spridda moln"
    elif status == "broken clouds".capitalize() or status == "clouds".capitalize():
        return "Molnigt"
    elif status == "shower rain".capitalize():
        return "Regnigt"
    elif status == "rain":
        return "Duggregn"
    elif status == "thunderstorm".capitalize():
        return "Storm"
    elif status == "snow".capitalize():
        return "Snöigt"
    elif status == "mist".capitalize():
        return "Dimmigt"
    else:
        return status

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
    if status == "Clear sky".capitalize():
        if big == 1:
            if isNight():
                return "weather_1_big_night"
            else:
                return "weather_1_big"
        else:
            return "weather_1_small"
    elif status == "few clouds".capitalize():
        if big == 1:
            if isNight():
                return "weather_2_big_night"
            else:
                return "weather_2_big"
        else:
            return "weather_2_small"
    elif status == "scattered clouds".capitalize():
        if big == 1:
            if isNight():
                return "weather_3_big_night"
            else:
                return "weather_3_big"
        else:
            return "weather_3_small"
    elif status == "broken clouds".capitalize() or status == "clouds".capitalize():
        if big == 1:
            return "weather_4_big"
        else:
            return "weather_4_small"
    elif status == "shower rain".capitalize():
        if big == 1:
            return "weather_8_big"
        else:
            return "weather_8_small"
    elif status == "rain".capitalize():
        if big == 1:
            return "weather_7_big"
        else:
            return "weather_7_small"
    elif status == "thunderstorm".capitalize():
        if big == 1:
            return "weather_9_big"
        else:
            return "weather_9_small"
    elif status == "snow".capitalize():
        if big == 1:
            return "weather_5_big"
        else:
            return "weather_5_small"
    elif status == "mist".capitalize():
        if big == 1:
            return "weather_6_big"
        else:
            return "weather_6_small"

# Create aray for weather variables
def getForecast():
    global updated
    for i in range (0, 8):
        temp = observationArray[i].get_temperature('celsius')
        
        sunrise = observationArray[i].get_sunrise_time('iso')
        sunset = observationArray[i].get_sunset_time('iso')
        
        day = observationArray[i].get_reference_time(timeformat='date').strftime("%A").capitalize()
        
        newData = { "status": observationArray[i].get_status().capitalize(),
                            "temp": temp["temp"],
                            "temp_max": temp["temp_max"],
                            "temp_min": temp["temp_min"],
                             "sunrise": sunrise,
                             "sunset": sunset,
                             "day": day,
                             "id": i
                            }
        if forecastArray[i] != newData:
            updated = True
        
        forecastArray[i] = newData
    # saved cached version
    saveJSON()

def saveJSON():
    with open('cached/weather.json', 'w') as outfile:
        json.dump(forecastArray, outfile)

def getJSON():
    global forecastArray
    
    with open('cached/weather.json', 'r') as infile:
        json_data = infile.read()
        if json_data != "":
            t = json.loads(json_data)
            i = 0
            for element in t:
                forecastArray[i] = t
                print(t)
                i += 1
            
            #sort
            forecastArray = forecastArray[0]
            forecastArray_new = sorted(forecastArray, key=lambda k: int(k["id"]))

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