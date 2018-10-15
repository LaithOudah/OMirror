import datetime
import pyowm

# set API
owm = pyowm.OWM("681a848abbfde6c9da084c5e86d2a6f2")

# Set location, default Stockholm, SE
observation = owm.three_hours_forecast("Stockholm,SE")

# Get forecast
observationArray = {}
forecastArray = {}

def setObservation(obs):
    global observation
    observation = owm.three_hours_forecast(obs)

def getObservation():
    today_1 = datetime.datetime.now()
    
    # forecast always at 14.00 on the next days
    today_2 = (today_1 + datetime.timedelta(days=1)).replace(minute=0, hour=14, second=0)
    
    # 4 for today
    # 4 for day 1,2,3,4
    for i in range (4, 9):
        if i >= 0 and i < 4:
            observationArray[0] = observation.get_weather_at(today_1)
            today_1 += datetime.timedelta(hours=3) # 3 hour difference between todays forecast
        else:
            today_2 += datetime.timedelta(days=1)
            observationArray[i] = observation.get_weather_at(today_2)


# Create aray for weather variables
def getForecast():
    for i in range (0, 5):
        temp = observationArray[i].get_temperature('celsius')
        
        forecast[i] = { "status": observationArray[i].get_status(),
                        "temp": temp["temp"],
                        "temp_max": temp["temp_max"],
                        "temp_min": temp["temp_min"]
                        }

def updateAll():
    getObservation()

updateAll()