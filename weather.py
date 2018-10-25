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
    if status == "Clear sky":
        return "Klar himmel"
    elif status == "few clouds":
        return "Några moln"
    elif status == "scattered clouds":
        return "Spridda moln"
    elif status == "broken clouds":
        return "Molnigt"
    elif status == "shower rain":
        return "Regnigt"
    elif status == "rain":
        return "Duggregn"
    elif status == "thunderstorm":
        return "Storm"
    elif status == "snow":
        return "Snöigt"
    elif status == "mist":
        return "Dimmigt"
    else:
        return status

# Create aray for weather variables
def getForecast():
    for i in range (0, 8):
        temp = observationArray[i].get_temperature('celsius')
        
        day = observationArray[i].get_reference_time(timeformat='date').strftime("%A").capitalize()
        
        forecastArray[i] = { "status": convertSwedish(observationArray[i].get_status()),
                            "temp": temp["temp"],
                            "temp_max": temp["temp_max"],
                            "temp_min": temp["temp_min"],
                             "day": day
                            }
    # saved cached version
    saveJSON()

def saveJSON():
    with open('cached/weather.json', 'w') as outfile:
        json.dump(forecastArray, outfile)

def getJSON():
    with open('cached/weather.json', 'r') as infile:
        json_data = infile.read()
        if json_data != "":
            t = json.loads(json_data)
            for element in t:
                forecastArray[int(element)] = t[element]

def updateAll():
    getObservation()
    getForecast()