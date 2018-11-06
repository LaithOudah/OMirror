#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import os, time, locale, datetime, faulthandler
os.environ['SDL_AUDIODRIVER'] = 'dsp'
faulthandler.enable()
import re
import data # Data
import rgb # RGB
import sys, pygame # GUI
import news, weather # News & Weather
import threading, socket
import glob
import quotes, aktiviteter
import centered_text as centeredt

# variables
Running = True
internetConnection = False

name = ""

quote_delay = 15
pota_delay = 8

rotation = 0
rotated = False
rotation_buttonpressed = True

autosleep = 0
autoslept = False
autosleeping = False

pota_timestamp = None
quote_timestamp = None

## Init
pygame.init()
pygame.font.init()

cached_Images = {}

locale.setlocale(locale.LC_TIME, "sv_SE.utf8")
  
screen = pygame.display.set_mode((1200, 1000))
#screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

pygame.display.set_caption('OMirror')
pygame.mouse.set_visible(False)
icon = pygame.image.load('/home/pi/Desktop/OMirror/images/icon.png').convert()
pygame.display.set_icon(icon)

clock = pygame.time.Clock()

w, h = pygame.display.get_surface().get_size()
black = 0, 0, 0
white = 255, 255, 255

def cache_Images():
    print("Loaded images:")
    for item in glob.glob('/home/pi/Desktop/OMirror/images/*.png'):
        name = item.split('/')[-1]
        name = name.split('.', 1)[0]
        cached_Images[name] = pygame.image.load(item).convert()
        print(item)
    

#split every n
def splitString(string, n):
    allspaces = [x.start() for x in re.finditer(' ', string)]
    allspaces_mod = [divmod(x, n)[0] for x in allspaces]
    splitat = [0]
    
    for i in range(len(allspaces)):
        if allspaces_mod[i] == 0:
            continue
        else:
            i_hol = allspaces_mod[i]
            for j in range(len(allspaces_mod)):
                if allspaces_mod[j] == i_hol:
                    allspaces_mod[j] = 0
            splitat.append(allspaces[i])
    
    if len(splitat) == 1:
        return [string]
    else:
        return [string[i:j].lstrip() for i,j in zip(splitat, splitat[1:]+[None])]

# In ... time
def inTime(date):
    datenow = datetime.datetime.now()
    deltatime = date - datenow
    
    seconds = int(deltatime.total_seconds()) 
    minutes = int(divmod(deltatime.total_seconds(), 60)[0])
    hours = int(divmod(deltatime.total_seconds(), 60*60)[0])
    days = int(divmod(deltatime.total_seconds(), 60*60*24)[0])
    weeks = int(divmod(deltatime.total_seconds(), 60*60*24*7)[0])
    months = int(divmod(deltatime.total_seconds(), 60*60*24*30)[0])
    years = int(divmod(deltatime.total_seconds(), 60*60*24*30*12)[0])
    
    if years > 0:
        return ("Om %iy" % years)
    elif months > 0:
        return ("Om %iM" % months)
    elif weeks > 0:
        return ("Om %iv" % weeks)
    elif days > 0:
        return ("Om %id" % days)
    elif hours > 0:
        return ("Om %ih" % hours)
    elif minutes > 0:
        return ("Om %im" % minutes)
    elif seconds > 0:
        return ("Om %is" % seconds)
    else:
        return "Nu"

# For ... time
def forTime(date):
    datenow = datetime.datetime.now()
    deltatime = datenow - date
    
    seconds = int(deltatime.total_seconds()) 
    minutes = int(divmod(deltatime.total_seconds(), 60)[0])
    hours = int(divmod(deltatime.total_seconds(), 60*60)[0])
    days = int(divmod(deltatime.total_seconds(), 60*60*24)[0])
    weeks = int(divmod(deltatime.total_seconds(), 60*60*24*7)[0])
    months = int(divmod(deltatime.total_seconds(), 60*60*24*30)[0])
    years = int(divmod(deltatime.total_seconds(), 60*60*24*30*12)[0])
    
    if years > 0:
        return ("%iy sen" % years)
    elif months > 0:
        return ("%iM sen" % months)
    elif weeks > 0:
        return ("%iv sen" % weeks)
    elif days > 0:
        return ("%id sen" % days)
    elif hours > 0:
        return ("%ih sen" % hours)
    elif minutes > 0:
        return ("%im sen" % minutes)
    elif seconds > 0:
        return ("%is sen" % seconds)
    else:
        return "Nu"
    
# App get data thread
class app_getDataThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        global internetConnection, pota_timestamp, quote_timestamp
        while True:
            if(Running == False):
                break
            data.readData()
            
            checkData()
            
            # Check internet connection
            internetConnection = checkConnection()
            
            if internetConnection:
                rgb.wifi_led(1)
                if not weather.owmSET:
                    weather.init()
            else:
                rgb.wifi_led(0)
            
            
            #southtext
            if centeredt.getFromTime() != 0:
                if not southtext_object.checkString(centeredt.getFromTime()):
                    if(fader.fadeing(southtext_object)):
                        continue
                    else:
                        try:
                            if(southtext_object.get_surface().get_alpha() >= 255):
                                fader.add(1, southtext_object, 50, None)
                            else:
                                southtext_object.setString()
                                fader.add(0, southtext_object, 50, None)
                        except Exception:
                            pass
            else:
                try:
                    if(southtext_object.get_surface().get_alpha() >= 255):
                        fader.add(1, southtext_object, 50, None)
                except Exception:
                            pass
            #quote and pota timestamps
            if quote_timestamp != None:
                if datetime.datetime.now() > quote_timestamp:
                    quote_timestamp = None
                    fader.add(1, quote_object, 50, None)
            
            if pota_timestamp != None:
                if datetime.datetime.now() > pota_timestamp:
                    pota_timestamp = None
                    fader.add(1, pota_object, 50, None)
            

def show_quote():
    global quote_timestamp
    quote_object.setString()
    
    quote_timestamp = datetime.datetime.now() + datetime.timedelta(seconds=quote_delay)
    
    fader.add(0, quote_object, 50, None)
    
    

def showQuote():
    try:
        if(quote_object.get_surface().get_alpha() == 0):
            if(pota_object.get_surface().get_alpha() >= 255 or fader.fadeing(pota_object)):
                fader.stop(pota_object)
                fader.add(1, pota_object, 50, show_quote)
            else:
                show_quote()
    except Exception:
        pass
        
def show_pota():
    global pota_timestamp
    pota_object.getInfo()
    fader.add(0, pota_object, 50, None)
    
    pota_timestamp = datetime.datetime.now() + datetime.timedelta(seconds=pota_delay)

def showPota():
    try:
        if(pota_object.get_surface().get_alpha() == 0):
            if(quote_object.get_surface().get_alpha() >= 255 or fader.fadeing(quote_object)):
                fader.stop(quote_object)
                fader.add(1, quote_object, 50, show_pota)
            else:
                show_pota()
    except Exception:
        pass

class app_getInfoThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        while True:
            if(Running == False):
                break
            
            if not weather.owmSET:
                weather.init()
            
            if internetConnection:
                try:
                    quotes.get_Data()
                except Exception:
                    pass
                try:
                    news.news_Parse()
                except Exception:
                    pass
                try:
                    weather.updateAll()
                except Exception:
                    # Ignore all exceptions
                    pass
            else:
                # load from cache
                news.getJSON()
                weather.getJSON()
            aktiviteter.getJSON()
            quotes.getJSON()
            
            centeredt.getJSON()
            
            weather_object.getInfo()
            nyheter_object.getInfo()
            aktiviteter_object.getInfo()
            aktiviteter.removeUnwanted()
            
            time.sleep(1)

# check connection
def checkConnection():
    try:
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        pass
    return False

# Check data
def checkData():
    global name,language, rotation, autoslept, autosleeping, quote_delay, pota_delay,pota_quote_show
    
    cc = data.getData("rgb_single").split(",")
    rgb.colour = (int(cc[0]), int(cc[1]), int(cc[2]))
    
    fs = data.getData("rgb_flash_sequence").split(":")
    for k, v in enumerate(fs):
        v = v.split(",")
        for k2, v2 in enumerate(v):
            v[k2] = int(v2)
        fs[k] = v
    
    rgb.flash_sequence = fs
    rgb.flash_delay = float(data.getData("rgb_flash_delay"))
    rgb.mode = int(data.getData("rgb_mode"))
    rgb.fade_delay = int(data.getData("rgb_fade_delay"))
    
    rotation = int(data.getData("rotation"))
    if weather.city != data.getData("weather_city"):
        weather.city = data.getData("weather_city")
        weather.setObservation()
        weather.updateAll()
    weather.api = data.getData("weather_api")
    
    name = data.getData("name")
    
    pota_delay = int(data.getData("pota_delay"))
    quote_delay = int(data.getData("quote_delay"))
    pota_quote_show = int(data.getData("pota_quote_show"))
    if pota_quote_show == 2:
        showPota()
        data.setData("pota_quote_show", 0)
    elif pota_quote_show == 1:
        showQuote()
        data.setData("pota_quote_show", 0)
    
    autosleep = int(data.getData("autosleep"))
    
    if autosleep == 0:
        autosleeping = False
        autoslept = False
    else:
        time = data.getData("autosleep_time").split(",")
        time1 = time[0].split(":")
        time1[0] = int(time1[0])
        time1[1] = int(time1[1])
        time2 = time[1].split(":")
        time2[0] = int(time2[0])
        time2[1] = int(time2[1])
        timeNow = datetime.datetime.now()
        
        if timeNow.hour >= time1[0] and timeNow.hour <= time2[0]:
            if timeNow.hour == time1[0] and timeNow.minute < time1[1]:
                autoslept = False
                autosleeping = False
            elif timeNow.hour == time2[0] and timeNow.minute > time2[1]:
                autoslept = False
                autosleeping = False
            else:
                if autoslept == False:
                    autosleeping = True
                    autoslept = True
        elif time1[0] > time2[0]:
            if timeNow.hour <= time2[0]:
                if timeNow.hour + 24 >= time1[0]:
                    if timeNow.hour == time1[0] and timeNow.minute < time1[1]:
                        autoslept = False
                        autosleeping = False
                    elif timeNow.hour == time2[0] and timeNow.minute > time2[1]:
                        autoslept = False
                        autosleeping = False
                    else:
                        if autoslept == False:
                            autosleeping = True
                            autoslept = True

Thread_getData = app_getDataThread()
Thread_getInfo = app_getInfoThread()

# text OBJECT
def text_object(text, weight, size, alpha):
    def text_objects(text, font):
        textSurface = font.render(text, True, (255,255,255))
        return textSurface, textSurface.get_rect()
    
    font_weight = ""
    
    if weight == "Ultralight":
        font_weight = '/home/pi/Desktop/OMirror/font/sf_ultrathin.ttf'
    elif weight == "Light":
        font_weight = '/home/pi/Desktop/OMirror/font/sf_light.ttf'
    elif weight == "Thin":
            font_weight = '/home/pi/Desktop/OMirror/font/sf_thin.ttf'
    elif weight == "Semibold":
            font_weight = '/home/pi/Desktop/OMirror/font/sf_semibold.ttf'
    elif weight == "Medium":
            font_weight = '/home/pi/Desktop/OMirror/font/sf_medium.ttf'
    elif weight == "Heavy":
            font_weight = '/home/pi/Desktop/OMirror/font/sf_heavy.ttf'
    elif weight == "Bold":
            font_weight = '/home/pi/Desktop/OMirror/font/sf_bold.ttf'
    elif weight == "Black":
            font_weight = '/home/pi/Desktop/OMirror/font/sf_black.ttf'
    else:
        font_weight = '/home/pi/Desktop/OMirror/font/sf_regular.ttf'
    
    largeText = pygame.font.Font(font_weight, size)
    TextSurf, TextRect = text_objects(text, largeText)
    TextRect.center = (w - TextSurf.get_width()/2 - 10, 0 + TextSurf.get_height()/2)

    surface=pygame.Surface((TextSurf.get_width(), TextSurf.get_height()))
    surface.fill(black)
    surface.blit(TextSurf, pygame.Rect(0, 0, 0,0))
    surface.set_alpha(alpha)
    return surface

## Box container
class Box_container():
    LEFT = 0
    CENTER = 1
    RIGHT = 2
    
    NW = 0
    N = 1
    NE = 2
    W = 3
    C = 4
    E = 5
    SW = 6
    S = 7
    SE = 8
    
    def __init__(self, vert, x, y):
        self.list = list()
        self.x = x
        self.y = y
        self.surface = pygame.Surface((0, 0))
        self.vert = vert
        self.height = 0
        self.width = 0
        self.justify = self.LEFT
        self.anchor = self.NW
        self.alpha = 255
        self.padding_x = 0
        self.padding_y = 0
    def add_surface(self, surface):
        self.list.append(surface)
    def change_cord(self, x, y):
        self.x = x
        self.y = y
    def set_justify(self, justify):
        self.justify = justify
    def set_anchor(self, anchor):
        self.anchor = anchor
    def set_alpha(self, alpha):
        self.alpha = alpha
    def get_alpha(self):
        return self.alpha
    def set_padding(self, x, y):
        self.padding_x = x
        self.padding_y = y
    def draw(self):
        # Create new Surface
        self.height = 0
        self.width = 0
        
        for surf in self.list:
            if isinstance(surf, Box_container):
                s, p = surf.draw()
                surf = s
            
            if self.vert:
                self.height += surf.get_height()
                self.width = max(self.width, surf.get_width())
            else:
                self.width += surf.get_width()
                self.height = max(self.height, surf.get_height())
        
        self.surface = pygame.Surface((self.width, self.height))
        
        # Add objects to surface
        height = 0;
        width = 0;
        
        for surf in self.list:
            if isinstance(surf, Box_container):
                s, p = surf.draw()
                surf = s
        
            if self.vert:
                if(self.justify == self.LEFT):
                    self.surface.blit(surf, (width, height, 0, 0))
                elif(self.justify == self.CENTER):
                    self.surface.blit(surf, (self.width/2 - surf.get_width()/2, height, 0, 0))
                else:
                    self.surface.blit(surf, (self.width - surf.get_width(), height, 0, 0))
            else:
                self.surface.blit(surf, (width, height, 0, 0))

            if self.vert:
                height += surf.get_height()
                self.width = max(self.width, surf.get_width())
            else:
                width += surf.get_width()
                self.height = max(self.height, surf.get_height())
        
        # Return surface
        posx = 0
        posy = 0
        if self.anchor == self.N or self.anchor == self.NW or self.anchor == self.NE:
            posy = self.y + self.padding_y
        if self.anchor == self.W or self.anchor == self.C or self.anchor == self.E:
            posy = self.y - self.height/2
        if self.anchor == self.SW or self.anchor == self.S or self.anchor == self.SE:
            posy = self.y - self.height - self.padding_y
        
        if self.anchor == self.NW or self.anchor == self.W or self.anchor == self.SW:
            posx = self.x + self.padding_x
        if self.anchor == self.N or self.anchor == self.C or self.anchor == self.S:
            posx = self.x - self.width/2
        if self.anchor == self.NE or self.anchor == self.E or self.anchor == self.SE:
            posx = self.x - self.width - + self.padding_x
        
        self.surface.set_alpha(self.alpha)
        
        return self.surface, (posx, posy, 0, 0)



## INIT
def initialize():
    cache_Images()
    
    weather.init()
    rgb.init()
    
    Thread_getData.start()
    Thread_getInfo.start()
    
    return 0

## CHECK BUTTON STATUS
buttonPressed = False

def buttonStatus():
    global rotation_buttonpressed, rotation, rotated, buttonPressed, autosleeping
    
    if(rgb.GPIO.input(rgb.GPIO_BUTTON) == False):
        if buttonPressed == True:
            autosleeping = False
            buttonPressed = False
        if autosleeping:
            rgb.RGB_off()
        else:
            rgb.RGB_on()
    else:
        if buttonPressed == False:
            autosleeping = False
            buttonPressed = True
        screen.fill(black)
        rgb.RGB_off()
    
    if not (rgb.GPIO.input(rgb.GPIO_BUTTON_2)):
        if not rotation_buttonpressed:
            rotation_buttonpressed = True
            if rotation == 3:
                rotation = 0
            else:
                rotation += 1
            data.setData("rotation", rotation)
            rotated = True
    else:
        rotation_buttonpressed = False

## Fade in / Fade out
class fade():
    fadeArray = []
    
    def update(self):
        for item in self.fadeArray:
            object = item["object"]
            if item["dir"]:
                # fade in
                object.set_alpha(object.get_alpha() + item["speed"])
                
                if object.get_alpha() >= 255:
                    self.stop(object)
                    
                    fnc = item["fnc"]
                    if fnc is not None:
                        fnc()
            else:
                object.set_alpha(object.get_alpha() - item["speed"])
                if object.get_alpha() <= 0:
                    self.stop(object)
                    
                    fnc = item["fnc"]
                    if fnc is not None:
                        fnc()
    def add(self, inout, object, speed, fnc = None):
        fadeIn = True
        if inout != 0:
            fadeIn = False
        
        if not self.fadeing(object):
            dict = {"object": object, "speed": speed, "fnc": fnc, "dir": fadeIn}
            self.fadeArray.append(dict)
        
    def stop(self, object):
        iobj = None
        for item in self.fadeArray:
            if item["object"] == object:
                iobj = item
                break
        if iobj is not None:
            self.fadeArray.remove(iobj)
    def fadeing(self, object):
        fadeing_v = False
        for item in self.fadeArray:
            if item["object"] == object:
                fadeing_v = True
                break
        return fadeing_v

fader = fade()

#### WIDGETS 
class widget():
    alpha = 0
    base_surface = 0
    rotation = 0
    active_surface = 0
    
    def __init__(self, alpha):
        self.alpha = alpha
    def set_alpha(self, alpha):
        self.alpha = alpha
    def get_alpha(self):
        return self.alpha
    def update(self):
        return
    def fadeIn(self):
        return
    def fadeOut(self):
        return
    def set_rotation(self, rotation):
        self.rotation = rotation
    def rotate(self):
        self.active_surface = pygame.transform.rotate(self.base_surface, self.rotation*90)
    def get_surface(self):
        return self.active_surface

class weather_Object(widget):    
    def __init__(self, alpha):
        widget.__init__(self, alpha)
    def getInfo(self):
        if(len(weather.sortedArray) > 0):
            self.weather_status_image = cached_Images[weather.getImage(1, weather.forecastArray[0]["status"])]
            self.weather_status = text_object(weather.convertSwedish(weather.forecastArray[0]["status"]), "Regular", 30, 255)
            
            self.weather_location = text_object(weather.loc.split(",")[0], "Ultralight", 60, 255)
            self.weather_temp = text_object("%.1f°" % weather.forecastArray[0]["temp"], "Light", 74, 255)
            
            self.weather_max_0 = text_object("%.1f°" % weather.forecastArray[0]["temp_max"], "Light", 28, 255)
            self.weather_min_0 = text_object("%.1f°" % weather.forecastArray[0]["temp_min"], "Thin", 28, 255)
            
            self.weather_max_1 = text_object("%.1f°" % weather.forecastArray[1]["temp_max"], "Light", 28, 255)
            self.weather_min_1 = text_object("%.1f°" % weather.forecastArray[1]["temp_min"], "Thin", 28, 255)
            
            self.weather_max_2 = text_object("%.1f°" % weather.forecastArray[2]["temp_max"], "Light", 28, 255)
            self.weather_min_2 = text_object("%.1f°" % weather.forecastArray[2]["temp_min"], "Thin", 28, 255)
            
            self.weather_max_3 = text_object("%.1f°" % weather.forecastArray[3]["temp_max"], "Light", 28, 255)
            self.weather_min_3 = text_object("%.1f°" % weather.forecastArray[3]["temp_min"], "Thin", 28, 255)
            
            self.weather_splitter = cached_Images['divider_1']
            self.line2_img = cached_Images['line_2']
            
            '''
            self.sunrise_img = cached_Images["sunrise"]
            self.weather_sunrise = text_object("06:00", "Light", 26, 255)
            self.sunset_img = cached_Images["sunset"]
            self.weather_sunrise = text_object("19:32", "Light", 26, 255)
            '''
            self.weather_day1 = text_object(weather.forecastArray[4]["day"][:3], "Regular", 28, 255)
            self.weather_day1_img = cached_Images[weather.getImage(0, weather.forecastArray[4]["status"])]
            self.weather_day1_max = text_object("%.1f°" % weather.forecastArray[4]["temp_max"], "Light", 28, 255)
            
            self.weather_day2 = text_object(weather.forecastArray[5]["day"][:3], "Regular", 28, 255)
            self.weather_day2_img = cached_Images[weather.getImage(0, weather.forecastArray[5]["status"])]
            self.weather_day2_max = text_object("%.1f°" % weather.forecastArray[5]["temp_max"], "Light", 28, 255)
            
            self.weather_day3 = text_object(weather.forecastArray[6]["day"][:3], "Regular", 28, 255)
            self.weather_day3_img = cached_Images[weather.getImage(0, weather.forecastArray[6]["status"])]
            self.weather_day3_max = text_object("%.1f°" % weather.forecastArray[6]["temp_max"], "Light", 28, 255)
            
            self.weather_day4 = text_object(weather.forecastArray[7]["day"][:3], "Regular", 28, 255)
            self.weather_day4_img = cached_Images[weather.getImage(0, weather.forecastArray[7]["status"])]
            self.weather_day4_max = text_object("%.1f°" % weather.forecastArray[7]["temp_max"], "Light", 28, 255)
        else:
            self.weather_status_image = pygame.Surface((0,0))
            self.weather_status = text_object("-", "Regular", 30, 255)
            
            self.weather_location = text_object("-", "Ultralight", 60, 255)
            self.weather_temp = text_object("-", "Light", 74, 255)
            
            self.weather_max_0 = text_object("-", "Light", 28, 255)
            self.weather_min_0 = text_object("-", "Thin", 28, 255)
            
            self.weather_max_1 = text_object("-", "Light", 28, 255)
            self.weather_min_1 = text_object("-", "Thin", 28, 255)
            
            self.weather_max_2 = text_object("-", "Light", 28, 255)
            self.weather_min_2 = text_object("-", "Thin", 28, 255)
            
            self.weather_max_3 = text_object("-", "Light", 28, 255)
            self.weather_min_3 = text_object("-", "Thin", 28, 255)
            
            self.weather_splitter = cached_Images['divider_1']
            self.line2_img = cached_Images['line_2']
            
            '''
            self.sunrise_img = cached_Images["sunrise"]
            self.weather_sunrise = text_object("-", "Light", 26, 255)
            self.sunset_img = cached_Images["sunset"]
            self.weather_sunrise = text_object("-", "Light", 26, 255)
            '''
            
            self.weather_day1 = text_object("-", "Regular", 28, 255)
            self.weather_day1_img = pygame.Surface((0,0))
            self.weather_day1_max = text_object("-", "Light", 28, 255)
            
            self.weather_day2 = text_object("-", "Regular", 28, 255)
            self.weather_day2_img = pygame.Surface((0,0))
            self.weather_day2_max = text_object("-", "Light", 28, 255)
            
            self.weather_day3 = text_object("-", "Regular", 28, 255)
            self.weather_day3_img = pygame.Surface((0,0))
            self.weather_day3_max = text_object("-", "Light", 28, 255)
            
            self.weather_day4 = text_object("-","Regular", 28, 255)
            self.weather_day4_img = pygame.Surface((0,0))
            self.weather_day4_max = text_object("-", "Light", 28, 255)
    def update(self):
        self.base_surface = pygame.Surface((600,480))
        
        self.base_surface.blit(self.weather_status_image, (0,0,0,0))
        
        
        self.base_surface.blit(self.weather_status, (250/2 - self.weather_status.get_width()/2, 235, 0, 0))
    
        
        ## NOW + 0, +3, +6 ,+ 9
        # One item
        
        self.base_surface.blit(self.weather_max_0, (255, 145 ,0,0))
        
        self.base_surface.blit(self.weather_min_0, (255, 176 ,0,0))
        
        width = 0
        gap = 10
        if self.weather_max_0.get_width() > self.weather_min_0.get_width():
            width = self.weather_max_0.get_width()
        else:
            width = self.weather_min_0.get_width()
        
        self.base_surface.blit(self.weather_splitter, (255 + width + gap, 145, 0, 0))
        width += gap*2
        
        # One item
        
        self.base_surface.blit(self.weather_max_1, (255 + width, 145 ,0,0))
        
        self.base_surface.blit(self.weather_min_1, (255 + width, 176,0,0))
        
        if self.weather_max_1.get_width() > self.weather_min_1.get_width():
            width += self.weather_max_1.get_width()
        else:
            width += self.weather_min_1.get_width()
        
        self.base_surface.blit(self.weather_splitter, (255 + width + gap, 145, 0, 0))
        width += gap*2
        
        # One item
        
        self.base_surface.blit(self.weather_max_2, (255 + width, 145 ,0,0))
        
        self.base_surface.blit(self.weather_min_2, (255 + width, 176,0,0))
        
        if self.weather_max_2.get_width() > self.weather_min_2.get_width():
            width += self.weather_max_2.get_width()
        else:
            width += self.weather_min_2.get_width()
        
        self.base_surface.blit(self.weather_splitter, (255 + width + gap, 145, 0, 0))
        width += gap*2
        
        # One item
        self.base_surface.blit(self.weather_max_3, (255 + width, 145 ,0,0))
        self.base_surface.blit(self.weather_min_3, (255 + width, 176,0,0))
        
        width += self.weather_max_3.get_width()
        
        self.base_surface.blit(self.weather_temp, (250 + width/2 - self.weather_temp.get_width()/2, 60 ,0,0))
        
        self.base_surface.blit(self.weather_location, (250 + (width)/2 - self.weather_location.get_width() / 2, -5,0,0))
        
        # Sun rise & Sun down
        '''
        self.base_surface.blit(self.sunrise_img, (248, 215))
        self.base_surface.blit(self.weather_sunrise, (248 + 32, 215))
        self.base_surface.blit(self.sunset_img, (248 + 70 +32, 215))
        self.base_surface.blit(self.weather_sunrise, (248 + 70 + 64, 215))
        '''
        
        ## Other days
        # One item
        height = 250 + self.weather_status.get_height()
        
        
        self.base_surface.blit(self.weather_day1, (0, height,0,0))

        self.base_surface.blit(self.weather_day1_img, (300 / 2 - self.weather_day1_img.get_width() / 2 , height))

        self.base_surface.blit(self.weather_day1_max, (300 - self.weather_day1_max.get_width(), height,0,0))
        
        height += self.weather_day1.get_height() + 3
        
        self.base_surface.blit(self.line2_img, (0, height))
        height += 3
        
        #One item
        self.base_surface.blit(self.weather_day2, (0, height,0,0))
        self.base_surface.blit(self.weather_day2_img, (300 / 2 - self.weather_day2_img.get_width() / 2 , height))
        
        self.base_surface.blit(self.weather_day2_max, (300 - self.weather_day2_max.get_width(), height,0,0))
        
        height += self.weather_day2.get_height() + 3
        self.base_surface.blit(self.line2_img, (0, height))
        height += 3
        
        #One item
        self.base_surface.blit(self.weather_day3, (0, height,0,0))
        self.base_surface.blit(self.weather_day3_img, (300 / 2 - self.weather_day3_img.get_width() / 2 , height))
        
        self.base_surface.blit(self.weather_day3_max, (300 - self.weather_day3_max.get_width(), height,0,0))
        height += self.weather_day3.get_height() + 3
        self.base_surface.blit(self.line2_img, (0, height))
        height += 3
        
        #One item
        self.base_surface.blit(self.weather_day4, (0, height,0,0))
        self.base_surface.blit(self.weather_day4_img, (300 / 2 - self.weather_day4_img.get_width() / 2 , height))
        self.base_surface.blit(self.weather_day4_max, (300 - self.weather_day4_max.get_width(), height,0,0))
        self.base_surface.set_alpha(self.alpha)
        
        # rotate
        widget.rotate(self)

class southtext_Object(widget):
    pos = None
    string = ""
    listString = []
    
    def __init__(self,alpha):
        widget.__init__(self, alpha)
        
        self.base_surface = Box_container(True, screen.get_width() /2, screen.get_height())
        
        ww, pos = self.base_surface.draw()
        
        self.base_surface = ww
        self.base_surface.set_alpha(alpha)
    def setString(self):
        self.string = centeredt.getFromTime() if centeredt.getFromTime() != 0 else ""
        
        self.listString = []
        for e in splitString(self.string, 20):
            self.listString.append(text_object(e, "Thin", 60, 255))
    def checkString(self, string):
        return self.string == string
    def update(self):
        self.base_surface = Box_container(True, screen.get_width() /2, screen.get_height())
        
        for item in self.listString:
            self.base_surface.add_surface(item)
        
        self.base_surface.set_anchor(Box_container.S)
        self.base_surface.set_padding(0, 25)
        self.base_surface.set_justify(Box_container.CENTER)

        ww, pos = self.base_surface.draw()
        self.base_surface = ww
        
        self.base_surface.set_alpha(self.alpha)
        
        self.pos = pos
        
        # rotate
        widget.rotate(self)
    def get_pos(self):
        return self.pos

class pota_Object(widget):
    pos = None
    
    def __init__(self,alpha):
        widget.__init__(self, alpha)
        self.base_surface = Box_container(True, screen.get_width() /2, screen.get_height() / 2)
        ww, pos = self.base_surface.draw()
        
        self.base_surface = ww
        self.base_surface.set_alpha(alpha)
    def getInfo(self):
        if name == "":
            self.name = text_object("-", "Thin", 82, 255)
        else:
            self.name = text_object(name, "Thin", 82, 255)
    def update(self):
        self.base_surface = Box_container(True, screen.get_width() /2, screen.get_height() / 2)
        self.base_surface.add_surface(self.name)
        
        self.base_surface.set_anchor(Box_container.C)
        self.base_surface.set_padding(0, 0)

        ww, pos = self.base_surface.draw()
        self.base_surface = ww
        
        self.base_surface.set_alpha(self.alpha)
        
        
        self.pos = pos
        
        # rotate
        widget.rotate(self)
    def get_pos(self):
        return self.pos

class quote_Object(widget):
    pos = None
    string = ""
    listString = []
    
    def __init__(self,alpha):
        widget.__init__(self, alpha)
        self.base_surface = Box_container(True, screen.get_width() /2, screen.get_height() / 2)
        ww, pos = self.base_surface.draw()
        
        self.base_surface = ww
        self.base_surface.set_alpha(alpha)
    def setString(self):
        quote = quotes.get_randomQuote()
        self.string = quote["quote"]
        
        self.listString = []
        for e in splitString(self.string, 30):
            self.listString.append(text_object(e, "Thin", 35, 255))
        self.listString.append(text_object("- " + quote["author"], "Light", 24, 175))
    def checkString(self, quote):
        return self.string == quote["quote"]
    def update(self):
        self.base_surface = Box_container(True, screen.get_width() /2, screen.get_height() / 2)
        
        for item in self.listString:
            self.base_surface.add_surface(item)
        
        self.base_surface.set_anchor(Box_container.C)
        self.base_surface.set_padding(0, 0)
        self.base_surface.set_justify(Box_container.CENTER)

        ww, pos = self.base_surface.draw()
        self.base_surface = ww
        
        self.base_surface.set_alpha(self.alpha)
                
        self.pos = pos
        
        # rotate
        widget.rotate(self)
    def get_pos(self):
        return self.pos

class dateTime_Object(widget):
    def __init__(self,alpha):
        widget.__init__(self, alpha)
    def update(self):
        self.base_surface = pygame.Surface((550, 300))
        
        text_1 = text_object(time.strftime("%A").capitalize(), "Ultralight", 60, 255)
        width = self.base_surface.get_width() - text_1.get_width()
        height = 0
        self.base_surface.blit(text_1, (width,height))
        height += text_1.get_height()
        
        text_2 = text_object(time.strftime("%B").capitalize()[:3] + time.strftime(" %d, %Y"), "Thin", 60, 255)
        width = self.base_surface.get_width() - text_2.get_width()
        self.base_surface.blit(text_2, (width, height))
        height += text_2.get_height()
        
        text_3 = text_object(time.strftime("%S"), "Ultralight", 52, 180)
        width = self.base_surface.get_width() - text_3.get_width()
        self.base_surface.blit(text_3, (width, height))
        
        text_4 = text_object(time.strftime("%H:%M"), "Ultralight", 95, 255)
        width = self.base_surface.get_width() - 58 - text_4.get_width()
        
        self.base_surface.blit(text_4,(width, height - 10))
        
        self.base_surface.set_alpha(self.alpha)

        # rotate
        widget.rotate(self)

class loading_Object(widget):
    pos = None
    string = "Initialiserar..."
    
    def __init__(self,alpha):
        widget.__init__(self, alpha)
        
        self.img = pygame.image.load("/home/pi/Desktop/OMirror/images/logo.png").convert()
    def setString(self, string):
        self.string = string
    def update(self):
        self.base_surface = Box_container(True, screen.get_width() /2, screen.get_height() / 2)
        self.base_surface.add_surface(self.img)
        self.base_surface.add_surface(text_object(self.string,  "Thin", 36, 255))
        
        self.base_surface.set_anchor(Box_container.C)
        self.base_surface.set_padding(0, 0)
        self.base_surface.set_justify(Box_container.CENTER)

        ww, pos = self.base_surface.draw()
        self.base_surface = ww
        
        self.base_surface.set_alpha(self.alpha)

        self.pos = pos
        
        # rotate
        widget.rotate(self)
    def get_pos(self):
        return self.pos

def dateFix(month):
    if month == "May":
        return "Maj"
    elif month == "Oct":
        return "Okt"
    else:
        return month

def getDateObj(string):
    date = string.split(" ", 1)[1]
    date = date.rsplit(" ", 1)[0]
    date = date.split(" ")
    date = date[0] + " " + dateFix(date[1]) + " " + date[2] + " " + date[3]
    
    return datetime.datetime.strptime(date, "%d %b %Y %H:%M:%S")

class nyheter_Object(widget):
    def __init__(self,alpha):
        widget.__init__(self,alpha)
        
        self.base_surface = pygame.Surface((250, 160))
        self.item_holder = pygame.Surface((250, 160))
        
    def getInfo(self):
        self.header = text_object("Nyheter", "Thin", 32, 255)
        
        if len(news.sortedArray) > 0:
            self.item_1_time = text_object(forTime(getDateObj(news.sortedArray[0]["date"])), "Thin", 16, 240)
            t = news.sortedArray[0]["title"]
            self.item_1_text = text_object((t[:35] + '..') if len(t) > 35 else t, "Light", 16, 255)
        else:
            self.item_1_time = text_object("-", "Thin", 16, 240)
            self.item_1_text = text_object("-", "Light", 16, 255)
            
        if len(news.sortedArray) > 1:
            self.item_2_time = text_object(forTime(getDateObj(news.sortedArray[1]["date"])), "Thin", 16, 190)
            t = news.sortedArray[1]["title"]
            self.item_2_text = text_object((t[:35] + '..') if len(t) > 35 else t, "Light", 16, 200)
        else:
            self.item_2_time = text_object("-", "Thin", 16, 190)
            self.item_2_text = text_object("-", "Light", 16, 200)
            
        if len(news.sortedArray) > 2:
            self.item_3_time = text_object(forTime(getDateObj(news.sortedArray[2]["date"])), "Thin", 16, 140)
            t = news.sortedArray[2]["title"]
            self.item_3_text = text_object((t[:35] + '..') if len(t) > 35 else t, "Light", 16, 150)
        else:
            self.item_3_time = text_object("-", "Thin", 16, 140)
            self.item_3_text = text_object("-", "Light", 16, 150)
            
        if len(news.sortedArray) > 3:
            self.item_4_time = text_object(forTime(getDateObj(news.sortedArray[3]["date"])), "Thin", 16, 90)
            t = news.sortedArray[3]["title"]
            self.item_4_text = text_object((t[:35] + '..') if len(t) > 35 else t, "Light", 16, 100)
        else:
            self.item_4_time = text_object("-", "Thin", 16, 90)
            self.item_4_text = text_object("-", "Light", 16, 100)
            
        if len(news.sortedArray) > 4:
            self.item_5_time = text_object(forTime(getDateObj(news.sortedArray[4]["date"])), "Thin", 16, 40)
            t = news.sortedArray[4]["title"]
            self.item_5_text = text_object((t[:35] + '..') if len(t) > 35 else t, "Light", 16, 50)
        else:
            self.item_5_time = text_object("-", "Thin", 16, 40)
            self.item_5_text = text_object("-", "Light", 16, 50)
    def update(self):
        self.base_surface = pygame.Surface((250, 160))
        
        self.base_surface.blit(self.header, (self.base_surface.get_width() - self.header.get_width(), 0, 0 ,0))
        
        self.base_surface.blit(cached_Images['line'],(0, self.header.get_height() + 3, 0 ,0))
        height = self.header.get_height() + 6
        
        self.base_surface.blit(self.item_holder, (0, height))
        
        self.item_holder.fill(black)
        
        height = 0
        self.item_holder.blit(self.item_1_time, (0, height))
        width = self.base_surface.get_width() - self.item_1_text.get_width() if self.item_1_text.get_width() < 250 - 75 else 75
        self.item_holder.blit(self.item_1_text, (width, height, 0, 0))
        height += self.item_1_text.get_height() + 3
        
        self.item_holder.blit(self.item_2_time, (0, height))
        width = self.base_surface.get_width() - self.item_2_text.get_width() if self.item_2_text.get_width() < 250 - 75 else 75
        self.item_holder.blit(self.item_2_text, (width, height, 0, 0))
        height += self.item_2_text.get_height() + 3
        
        self.item_holder.blit(self.item_3_time, (0, height))
        width = self.base_surface.get_width() - self.item_3_text.get_width() if self.item_3_text.get_width() < 250 - 75 else 75
        self.item_holder.blit(self.item_3_text, (width, height, 0, 0))
        height += self.item_3_text.get_height() + 3
        
        self.item_holder.blit(self.item_4_time, (0, height))
        width = self.base_surface.get_width() - self.item_4_text.get_width() if self.item_4_text.get_width() < 250 - 75 else 75
        self.item_holder.blit(self.item_4_text, (width, height, 0, 0))
        height += self.item_4_text.get_height() + 3
        
        self.item_holder.blit(self.item_5_time, (0, height))
        width = self.base_surface.get_width() - self.item_5_text.get_width() if self.item_5_text.get_width() < 250 - 75 else 75
        self.item_holder.blit(self.item_5_text, (width, height, 0, 0))
        
        self.base_surface.set_alpha(self.alpha)

        # rotate
        widget.rotate(self)

class aktiviteter_Object(widget):
    item_holder = pygame.Surface((0,0))
    
    def __init__(self,alpha):
        widget.__init__(self,alpha)
        
        self.base_surface = pygame.Surface((250, 160))
        self.item_holder = pygame.Surface((250, 160))
    def getInfo(self):
        self.header = text_object("Aktiviteter", "Thin", 32, 255)
        
        if len(aktiviteter.sortedArray) > 0:
            self.item_1_time = text_object(inTime(datetime.datetime.strptime(aktiviteter.sortedArray[0]["date"], "%Y-%m-%d %H:%M")), "Thin", 16, 240)
            t = aktiviteter.sortedArray[0]["text"]
            self.item_1_text = text_object((t[:35] + '..') if len(t) > 35 else t, "Light", 16, 255)
        else:
            self.item_1_time = text_object("-", "Thin", 16, 240)
            self.item_1_text = text_object("-", "Light", 16, 255)
            
        if len(aktiviteter.sortedArray) > 1:
            self.item_2_time = text_object(inTime(datetime.datetime.strptime(aktiviteter.sortedArray[1]["date"], "%Y-%m-%d %H:%M")), "Thin", 16, 190)
            t = aktiviteter.sortedArray[1]["text"]
            self.item_2_text = text_object((t[:35] + '..') if len(t) > 35 else t, "Light", 16, 200)
        else:
            self.item_2_time = text_object("-", "Thin", 16, 190)
            self.item_2_text = text_object("-", "Light", 16, 200)
        
        if len(aktiviteter.sortedArray) > 2:
            self.item_3_time = text_object(inTime(datetime.datetime.strptime(aktiviteter.sortedArray[2]["date"], "%Y-%m-%d %H:%M")), "Thin", 16, 140)
            t = aktiviteter.sortedArray[2]["text"]
            self.item_3_text = text_object((t[:35] + '..') if len(t) > 35 else t, "Light", 16, 150)
        else:
            self.item_3_time = text_object("-", "Thin", 16, 140)
            self.item_3_text = text_object("-", "Light", 16, 150)
        
        if len(aktiviteter.sortedArray) > 3:
            self.item_4_time = text_object(inTime(datetime.datetime.strptime(aktiviteter.sortedArray[3]["date"], "%Y-%m-%d %H:%M")), "Thin", 16, 90)
            t = aktiviteter.sortedArray[3]["text"]
            self.item_4_text = text_object((t[:35] + '..') if len(t) > 35 else t, "Light", 16, 100)
        else:
            self.item_4_time = text_object("-", "Thin", 16, 90)
            self.item_4_text = text_object("-", "Light", 16, 100)
            
        if len(aktiviteter.sortedArray) > 4:
            self.item_5_time = text_object(inTime(datetime.datetime.strptime(aktiviteter.sortedArray[4]["date"], "%Y-%m-%d %H:%M")), "Thin", 16, 40)
            t = aktiviteter.sortedArray[4]["text"]
            self.item_5_text = text_object((t[:35] + '..') if len(t) > 35 else t, "Light", 16, 50)
        else:
            self.item_5_time = text_object("-", "Thin", 16, 40)
            self.item_5_text = text_object("-", "Light", 16, 50)
    def update(self):
        self.base_surface = pygame.Surface((250, 160))
        
        self.base_surface.blit(self.header, (self.base_surface.get_width() - self.header.get_width(), 0, 0 ,0))
        
        self.base_surface.blit(cached_Images['line'],(0, self.header.get_height() + 3, 0 ,0))
        height = self.header.get_height() + 6
        
        self.base_surface.blit(self.item_holder, (0, height))
        
        
        self.item_holder.fill(black)
        
        height = 0
        self.item_holder.blit(self.item_1_time, (0, height))
        width = self.base_surface.get_width() - self.item_1_text.get_width() if self.item_1_text.get_width() < 250 - 75 else 75
        self.item_holder.blit(self.item_1_text, (width, height, 0, 0))
        height += self.item_1_text.get_height() + 3
        
        self.item_holder.blit(self.item_2_time, (0, height))
        width = self.base_surface.get_width() - self.item_2_text.get_width() if self.item_2_text.get_width() < 250 - 75 else 75
        self.item_holder.blit(self.item_2_text, (width, height, 0, 0))
        height += self.item_2_text.get_height() + 3
        
        self.item_holder.blit(self.item_3_time, (0, height))
        width = self.base_surface.get_width() - self.item_3_text.get_width() if self.item_3_text.get_width() < 250 - 75 else 75
        self.item_holder.blit(self.item_3_text, (width, height, 0, 0))
        height += self.item_3_text.get_height() + 3
        
        self.item_holder.blit(self.item_4_time, (0, height))
        width = self.base_surface.get_width() - self.item_4_text.get_width() if self.item_4_text.get_width() < 250 - 75 else 75
        self.item_holder.blit(self.item_4_text, (width, height, 0, 0))
        height += self.item_4_text.get_height() + 3
        
        self.item_holder.blit(self.item_5_time, (0, height))
        width = self.base_surface.get_width() - self.item_5_text.get_width() if self.item_5_text.get_width() < 250 - 75 else 75
        self.item_holder.blit(self.item_5_text, (width, height, 0, 0))
        
        self.base_surface.set_alpha(self.alpha)

        # rotate
        widget.rotate(self)

weather_object = weather_Object(0)
southtext_object = southtext_Object(0)
pota_object = pota_Object(0)
dateTime_object = dateTime_Object(0)
quote_object = quote_Object(0)
nyheter_object = nyheter_Object(0)
aktiviteter_object = aktiviteter_Object(0)
loading_object = loading_Object(255)

def app_loop():
    global Running, rotated
    
    # Show Loading screen
    screen.fill(black)
    loading_object.update()
    screen.blit(loading_object.get_surface(), loading_object.get_pos())
    pygame.display.update()
    
    # Initialize
    initialize()
    
    # Show Loading screen
    screen.fill(black)
    loading_object.setString("Laddar in data...")
    loading_object.update()
    screen.blit(loading_object.get_surface(), loading_object.get_pos())
    pygame.display.update()
    
    # set Objects
    fader.add(0, weather_object, 25, None)
    fader.add(0, southtext_object, 25, None)
    fader.add(0, dateTime_object, 25, None)
    fader.add(0, nyheter_object, 25, None)
    fader.add(0, aktiviteter_object, 25, None)
    
    
    # Init
    weather.getJSON()
    news.getJSON()
    aktiviteter.getJSON()
    centeredt.getJSON()
    quotes.getJSON()
    
    weather_object.getInfo()
    nyheter_object.getInfo()
    aktiviteter_object.getInfo()
    pota_object.getInfo()
    quote_object.setString()
    
    screen.fill(black)
    
    while Running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
        
        # rotatetd
        if rotated:
            screen.fill(black)
            rotated = False
        
        screen.fill(black)
        
        # Widget Date Time
        dateTime_object.set_rotation(rotation)
        dateTime_object.update()
        
        # Prettiest of them all
        pota_object.set_rotation(rotation)
        pota_object.update()
        
        
        # Daily famous quotes
        quote_object.set_rotation(rotation)
        quote_object.update()
        
        # Widget South text
        southtext_object.set_rotation(rotation)
        southtext_object.update()
        
        # Weather
        weather_object.set_rotation(rotation)
        weather_object.update()
        
        # Nyheter
        nyheter_object.set_rotation(rotation)
        nyheter_object.update()
        
        # Aktiviteter
        aktiviteter_object.set_rotation(rotation)
        aktiviteter_object.update()
        
        # Draw
        if rotation == 0:
            
            screen.blit(dateTime_object.get_surface(), (screen.get_width() - dateTime_object.get_surface().get_width() - 25, 25, 0 , 0))
            screen.blit(weather_object.get_surface(), (25, 25, 0 , 0))
            
            screen.blit(pota_object.get_surface(), pota_object.get_pos())
            screen.blit(quote_object.get_surface(), quote_object.get_pos())
            screen.blit(southtext_object.get_surface(), southtext_object.get_pos())
            
            
            screen.blit(nyheter_object.get_surface(), (screen.get_width() - nyheter_object.get_surface().get_width() - 25, screen.get_height() - nyheter_object.get_surface().get_height() - 25))
            screen.blit(aktiviteter_object.get_surface(), (screen.get_width() - aktiviteter_object.get_surface().get_width() - 25, screen.get_height() - nyheter_object.get_surface().get_height() - aktiviteter_object.get_surface().get_height() - 25))
        elif rotation == 1:
            
            screen.blit(dateTime_object.get_surface(), (25, 25, 0, 0))
            screen.blit(weather_object.get_surface(), (25, screen.get_height() - weather_object.get_surface().get_height() - 25, 0 , 0))
            
            screen.blit(pota_object.get_surface(), (screen.get_width() / 2 - pota_object.get_surface().get_width() / 2, screen.get_height() / 2 - pota_object.get_surface().get_height() / 2, 0 ,0))
            screen.blit(quote_object.get_surface(), (screen.get_width() / 2 - quote_object.get_surface().get_width(), screen.get_height() / 2 - quote_object.get_surface().get_height() / 2, 0 ,0))
            screen.blit(southtext_object.get_surface(), (screen.get_width() - southtext_object.get_surface().get_width(), screen.get_height() / 2 - southtext_object.get_surface().get_height() / 2))
            
            
            screen.blit(nyheter_object.get_surface(), (screen.get_width() - nyheter_object.get_surface().get_width() - 25, 25))
            screen.blit(aktiviteter_object.get_surface(), (screen.get_width() - nyheter_object.get_surface().get_width() - aktiviteter_object.get_surface().get_width() - 25, 25))
        elif rotation == 2:
            
            screen.blit(dateTime_object.get_surface(), (25, screen.get_height() - dateTime_object.get_surface().get_height() - 25, 0 , 0))
            screen.blit(weather_object.get_surface(), (screen.get_width() - weather_object.get_surface().get_width() - 25, screen.get_height() - weather_object.get_surface().get_height() - 25, 0 , 0))
            
            screen.blit(pota_object.get_surface(), pota_object.get_pos())
            screen.blit(quote_object.get_surface(), quote_object.get_pos())
            screen.blit(southtext_object.get_surface(), (screen.get_width()/2 - southtext_object.get_surface().get_width() / 2, southtext_object.get_surface().get_height() / 2))
            
            
            screen.blit(nyheter_object.get_surface(), (25, 25))
            screen.blit(aktiviteter_object.get_surface(), (25, 25 + nyheter_object.get_surface().get_height()))
        elif rotation == 3:
            
            screen.blit(dateTime_object.get_surface(), (screen.get_width() - dateTime_object.get_surface().get_width() - 25, screen.get_height() - dateTime_object.get_surface().get_height() - 25, 0 , 0))
            screen.blit(weather_object.get_surface(), (screen.get_width() - weather_object.get_surface().get_width() - 25, 25, 0 , 0))
            
            screen.blit(pota_object.get_surface(), (screen.get_width() / 2 - pota_object.get_surface().get_width() / 2, screen.get_height() / 2 - pota_object.get_surface().get_height() / 2, 0 ,0))
            screen.blit(quote_object.get_surface(), (screen.get_width() / 2 - quote_object.get_surface().get_width() / 2, screen.get_height() / 2 - quote_object.get_surface().get_height() / 2, 0 ,0))
            screen.blit(southtext_object.get_surface(), (southtext_object.get_surface().get_width(), screen.get_height() / 2 - southtext_object.get_surface().get_height() / 2))
            
            
            screen.blit(nyheter_object.get_surface(), (25, screen.get_height() - 25 - nyheter_object.get_surface().get_height()))
            screen.blit(aktiviteter_object.get_surface(), (25 + nyheter_object.get_surface().get_width(), screen.get_height() - 25 - aktiviteter_object.get_surface().get_height()))
        
        # autosleeping
        if autosleeping:
            screen.fill(black)
        
        # BUTTON status
        buttonStatus()
        
        # update fader
        fader.update()
        
        pygame.display.update()
        
        # End gui - DEBUGMODE
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    Running = False
            elif event.type == pygame.QUIT:
                Running = False
        
        clock.tick(60)
 

# start app
app_loop()

# Reset GPIO inputs
rgb.RGB_off()
rgb.GPIO.cleanup()

# End PI 
rgb.pi.stop()
pygame.quit()
quit()