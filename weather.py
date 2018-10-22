from pyowm.utils import timeformatutils
from datetime import datetime, date, timedelta
import pyowm

# set API
owm = pyowm.OWM("681a848abbfde6c9da084c5e86d2a6f2")

# Set location, default Växjö, SE
observation = owm.three_hours_forecast("Växjö,SE")

cord_x = 0
cord_y = 0
api = "681a848abbfde6c9da084c5e86d2a6f2"

# Get forecast
observationArray = {}
forecastArray = {}

def setApi(api):
    global owm
    owm = pyowm.OWM(api)

def setObservation(obs):
    global observation
    observation = owm.three_hours_forecast(obs)

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

# Create aray for weather variables
def getForecast():
    for i in range (0, 8):
        temp = observationArray[i].get_temperature('celsius')
        
        forecastArray[i] = { "status": observationArray[i].get_status(),
                            "temp": temp["temp"],
                            "temp_max": temp["temp_max"],
                            "temp_min": temp["temp_min"]
                            }


def updateAll():
    getObservation()
    getForecast()