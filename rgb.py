#!/usr/bin/python
# -*- coding: utf-8 -*-

#
 # -----------------------------------------------------
 # File        fading.py
 # Authors     David Ordnung
 # License     GPLv3
 # Web         http://dordnung.de/raspberrypi-ledstrip/
 # -----------------------------------------------------
 # 
 # Copyright (C) 2014-2017 David Ordnung
 # 
 # This program is free software: you can redistribute it and/or modify
 # it under the terms of the GNU General Public License as published by
 # the Free Software Foundation, either version 3 of the License, or
 # any later version.
 #  
 # This program is distributed in the hope that it will be useful,
 # but WITHOUT ANY WARRANTY; without even the implied warranty of
 # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 # GNU General Public License for more details.
 # 
 # You should have received a copy of the GNU General Public License
 # along with this program. If not, see <http://www.gnu.org/licenses/>
#


# This script needs running pigpio (http://abyz.co.uk/rpi/pigpio/)


###### CONFIGURE THIS ######

# The Pins. Use Broadcom numbers.
GPIO_R = 17
GPIO_G = 27
GPIO_B = 22
GPIO_BUTTON = 18
GPIO_SENSOR_1 = 23
GPIO_SENSOR_2 = 24

# Number of color changes per step (more is faster, less is slower).
# You also can use 0.X floats.
STEPS     = 1

###### END ######



import RPi.GPIO as GPIO
import os
import sys
import time
import pigpio
import thread

bright = 255
r = 255.0
g = 0.0
b = 0.0



pi = pigpio.pi()

def setLights(pin, brightness):
	realBrightness = int(int(brightness) * (float(bright) / 255.0))
	pi.set_PWM_dutycycle(pin, realBrightness)

GPIO.setmode(GPIO.BCM)

GPIO.setup(GPIO_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
## GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)

colour = (255, 255, 255)

fade_sequence = ((255, 255,255), (255, 0, 0), (0, 255, 0), (0,0,255))
fade_step = 0
fade_delay = 1000 ## in ms
fade_active = False
rgb_active = True

def RGB_Cycle():
    return 0

def RGB_Single():
    setLights(GPIO_R, colour[0])
    setLights(GPIO_G, colour[1])
    setLights(GPIO_B, colour[2])

def RGB_Flash(threadName, delay):
    global fade_step, fade_sequence, fade_active
    fade_active = True
    while mode == 1 and rgb_active:
        for colour in fade_sequence:
            if mode != 0 and not rgb_active:
                break
            setLights(GPIO_R, colour[0])
            setLights(GPIO_G, colour[1])
            setLights(GPIO_B, colour[2])
            time.sleep(0.2)
            
    fade_active = False

def RGB_off():
    global rgb_active
    rgb_active = False
    setLights(GPIO_R, 0)
    setLights(GPIO_G, 0)
    setLights(GPIO_B, 0)

## Mode 0 = One color
## Mode 1 = Flash
## Mode 2 = Cycle



mode = 0

while True:
    if(GPIO.input(GPIO_BUTTON) == False):
        '''
        rgb_active = True
        if mode == 0:
            RGB_Single()
        elif mode == 1:
            if not fade_active:
                thread.start_new_thread(RGB_Flash, ("fade", 0))
        elif mode == 2:
            RGB_Cycle()
        '''
    else:
        RGB_off()

pi.stop()