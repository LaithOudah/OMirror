# The Pins. Use Broadcom numbers.
GPIO_R = 17
GPIO_G = 27
GPIO_B = 22

GPIO_BUTTON = 18
GPIO_BUTTON_2 = 23

GPIO_WIFI_R = 5
GPIO_WIFI_G = 6
GPIO_WIFI_B = 13

GPIO_BLUETOOTH = 26

# Imports
import RPi.GPIO as GPIO
import os
import sys
import time

# initialize pigpiod


import pigpio
import threading

bright = 255

pi = None

def init():
    global pi
    os.system("sudo pigpiod")
    time.sleep(2) # sleep 2 seconds before executing rest of program, let pigpiod initialize
    
    pi = pigpio.pi()
    
    GPIO.setmode(GPIO.BCM)
    
    GPIO.setwarnings(False)

    GPIO.setup(GPIO_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
    GPIO.setup(GPIO_BLUETOOTH, GPIO.OUT)
    GPIO.setup(GPIO_WIFI_R, GPIO.OUT)
    GPIO.setup(GPIO_WIFI_G, GPIO.OUT)
    GPIO.setup(GPIO_WIFI_B, GPIO.OUT)
    GPIO.setup(GPIO_BUTTON_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)



## Mode 0 = One color
## Mode 1 = Flash
## Mode 2 = Cycle
mode = 2

# Preset values
colour = (255, 0, 0)

flash_sequence = ((255, 255,255), (255, 0, 0), (0, 255, 0), (0,0,255))
flash_step = 0
flash_delay = 1000 ## in ms
flash_active = False
cycle_active = False
rgb_active = False

app_active = True

def setLights(pin, brightness):
	realBrightness = int(int(brightness) * (float(bright) / 255.0))
	pi.set_PWM_dutycycle(pin, realBrightness)

# RGB Single
def RGB_Single():
    setLights(GPIO_R, colour[0])
    setLights(GPIO_G, colour[1])
    setLights(GPIO_B, colour[2])

# RGB Cycle thread
class RGB_Cycle (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        global cycle_active
        # Loop to 255
        startColour = list((255, 0, 0))
        
        cycle_active = True
        for decColour in range (0, 3):
            if not rgb_active:
                break
            if not cycle_active:
                break
            
            if decColour == 2:
                incColour = 0
            else:
                incColour = decColour + 1

            for i in range(0, 255):
                if not rgb_active:
                    break
                if not cycle_active:
                    break
                
                startColour[decColour] -= 1
                startColour[incColour] += 1
                
                setLights(GPIO_R, startColour[0])
                setLights(GPIO_G, startColour[1])
                setLights(GPIO_B, startColour[2])
                
                time.sleep(0.02)
        cycle_active = False

Thread_RGB_Cycle = RGB_Cycle()

# RGB Flash thread
class RGB_Flash (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        global flash_active, flash_sequence, flash_step
        flash_active = True
        while True:
            if not rgb_active:
                break
            if not flash_active:
                break
            for colour in flash_sequence:
                if not rgb_active:
                    break
                if not flash_active:
                    break
                setLights(GPIO_R, colour[0])
                setLights(GPIO_G, colour[1])
                setLights(GPIO_B, colour[2])
                
                time.sleep(flash_delay/1000)           
        flash_active = False
        

Thread_RGB_Flash = RGB_Flash()

# RGB Off state
def RGB_off():
    global rgb_active, cycle_active, flash_active
    rgb_active = False
    cycle_active = False
    flash_active = False
    
    setLights(GPIO_R, 0)
    setLights(GPIO_G, 0)
    setLights(GPIO_B, 0)

def BUTTON_status():
    return GPIO.input(GPIO_BUTTON)


# RGB ON, check mode
def RGB_on():
    global rgb_active, cycle_active, flash_active, Thread_RGB_Flash, Thread_RGB_Cycle
    rgb_active = True
    if mode == 0:
        cycle_active = False
        flash_active = False
        RGB_Single()
    elif mode == 1:
        time.sleep(0.01)
        cycle_active = False
        try:
            Thread_RGB_Flash.start()
        except RuntimeError:
            if not flash_active:
                Thread_RGB_Flash = RGB_Flash()
                Thread_RGB_Flash.start()
    elif mode == 2:
        time.sleep(0.01)
        flash_active = False
        try:
            Thread_RGB_Cycle.start()
        except Exception:
            if not cycle_active:
                Thread_RGB_Cycle= RGB_Cycle()
                Thread_RGB_Cycle.start()

def bluetooth_led(val):
    GPIO.output(GPIO_BLUETOOTH, val)

def wifi_led(val):
    if val:
        GPIO.output(GPIO_WIFI_R, 0)
        GPIO.output(GPIO_WIFI_G, 1)
        GPIO.output(GPIO_WIFI_B, 0)
    else:
        GPIO.output(GPIO_WIFI_R, 1)
        GPIO.output(GPIO_WIFI_G, 0)
        GPIO.output(GPIO_WIFI_B, 0)