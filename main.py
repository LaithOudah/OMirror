#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import os, time, locale
import data # Data
import rgb # RGB
import sys, pygame # GUI
import news, weather # News & Weather
import threading, socket
import glob
import quotes
# import gifimages

# variables
Running = True
internetConnection = False

name = ""
bluetooth_name = ""
wifi_pass = ""
wifi_ssid = ""
language = ""
rotation = 0
rotated = False

rotation_buttonpressed = True

autosleep = 0
autosleeping = True

## Init
pygame.init()
pygame.font.init()

cached_Images = {}

def cache_Images():
    print("Loaded images:")
    for item in glob.glob('images/*.png'):
        name = item.split('/', 1)[1]
        name = name.split('.', 1)[0]
        cached_Images[name] = pygame.image.load(item)
        print(item)
    '''
    for item in glob.glob('images/*.gif'):
        name = item.split('/', 1)[1]
        name = name.split('.', 1)[0]
        cached_Images[name] = gifimages.GIFImage(item)
        print(item)
    '''

locale.setlocale(locale.LC_TIME, "sv_SE.utf8")
  
screen = pygame.display.set_mode((1200, 1000))
# screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

pygame.display.set_caption('OMirror')
icon = pygame.image.load('images/icon.png').convert()
pygame.display.set_icon(icon)

clock = pygame.time.Clock()

w, h = pygame.display.get_surface().get_size()
black = 0, 0, 0
white = 255, 255, 255

#split every n
def splitString(string, n):
    return [string[i:i + n] for i in range(0, len(string), n)]

# App get data thread
class app_getDataThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        global internetConnection
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


class app_getInfoThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        while True:
            if(Running == False):
                break
            
            if internetConnection:
                try:
                    quotes.get_Data()
                    news.news_Parse()
                    weather.updateAll()
                except Exception:
                    # Ignore all exceptions
                    pass
            else:
                # load from cache
                news.getJSON()
                weather.getJSON()
                quotes.getJSON()
            
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
    global name,bluetooth_name, wifi_ssid, wifi_pass, autosleep, language, rotation
    
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
    
    rotation = int(data.getData("rotation"))
    
    weather.cord_x = float(data.getData("weather_cord_x"))
    weather.cord_y = float(data.getData("weather_cord_y"))
    weather.api = data.getData("weather_api")
    
    news.setRSS(data.getData("news_rss"))
    news.setMax(int(data.getData("news_max")))
    
    name = data.getData("name")

    wifi_ssid = data.getData("wifi_ssid")
    wifi_pass = data.getData("wifi_pass")
    
    autosleep = int(data.getData("autosleep"))
    language = data.getData("language")

Thread_getData = app_getDataThread()
Thread_getInfo = app_getInfoThread()

# text OBJECT
def text_object(text, weight, size, alpha):
    def text_objects(text, font):
        textSurface = font.render(text, True, (255,255,255))
        return textSurface, textSurface.get_rect()
    
    font_weight = ""
    
    if weight == "Ultralight":
        font_weight = 'font/sf_ultrathin.ttf'
    elif weight == "Light":
        font_weight = 'font/sf_light.ttf'
    elif weight == "Thin":
            font_weight = 'font/sf_thin.ttf'
    elif weight == "Semibold":
            font_weight = 'font/sf_semibold.ttf'
    elif weight == "Medium":
            font_weight = 'font/sf_medium.ttf'
    elif weight == "Heavy":
            font_weight = 'font/sf_heavy.ttf'
    elif weight == "Bold":
            font_weight = 'font/sf_bold.ttf'
    elif weight == "Black":
            font_weight = 'font/sf_black.ttf'
    else:
        font_weight = 'font/sf_regular.ttf'
    
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
                    self.surface.blit(surf, (self.width - surf.get_width() + surf.get_width()/2, height, 0, 0))
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
def buttonStatus():
    global rotation_buttonpressed, rotation, rotated
    
    if(rgb.GPIO.input(rgb.GPIO_BUTTON) == False):
        rgb.RGB_on()
    else:
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
    surface = 0
    rotation = 0
    
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
        self.surface = pygame.transform.rotate(self.surface, self.rotation*90)
    def get_surface(self):
        return self.surface

class weather_Object(widget):
    def __init__(self, alpha):
        widget.__init__(self, alpha)
    def update(self):
        self.surface = pygame.Surface((700,480))
        
        weather_status = text_object("Molnigt", "Regular", 30, 255)
        self.surface.blit(weather_status, (100, 230, 0, 0))
        
        weather_status_image = cached_Images['weather_1_big']
        self.surface.blit(weather_status_image, (0,0,0,0))
        
        weather_location_image = cached_Images['location']
        self.surface.blit(weather_location_image, (250,0,0,0))
        
        weather_location = text_object("Växjö", "Ultralight", 60, 255)
        self.surface.blit(weather_location, (295, -5,0,0))
        
        weather_location = text_object("72°", "Light", 84, 255)
        self.surface.blit(weather_location, (295, 60 ,0,0))
        
        ## NOW + 0, +3, +6 ,+ 9
        # One item
        weather_max_0 = text_object("72", "Light", 28, 255)
        self.surface.blit(weather_max_0, (255, 145 ,0,0))
        weather_min_0 = text_object("65", "Thin", 28, 255)
        self.surface.blit(weather_min_0, (255, 176 ,0,0))
        weather_splitter = cached_Images['divider_1']
        
        width = 0
        gap = 10
        if weather_max_0.get_width() > weather_min_0.get_width():
            width = weather_max_0.get_width()
        else:
            width = weather_min_0.get_width()
        
        self.surface.blit(weather_splitter, (255 + width + gap, 145, 0, 0))
        width += gap*2
        
        # One item
        weather_max_1 = text_object("72", "Light", 28, 255)
        self.surface.blit(weather_max_1, (255 + width, 145 ,0,0))
        weather_min_1 = text_object("65", "Thin", 28, 255)
        self.surface.blit(weather_min_1, (255 + width, 176,0,0))
        weather_splitter = cached_Images['divider_1']
        
        if weather_max_1.get_width() > weather_min_1.get_width():
            width += weather_max_1.get_width()
        else:
            width += weather_min_1.get_width()
        
        self.surface.blit(weather_splitter, (255 + width + gap, 145, 0, 0))
        width += gap*2
        
        # One item
        weather_max_1 = text_object("72", "Light", 28, 255)
        self.surface.blit(weather_max_1, (255 + width, 145 ,0,0))
        weather_min_1 = text_object("65", "Thin", 28, 255)
        self.surface.blit(weather_min_1, (255 + width, 176,0,0))
        weather_splitter = cached_Images['divider_1']
        
        if weather_max_1.get_width() > weather_min_1.get_width():
            width += weather_max_1.get_width()
        else:
            width += weather_min_1.get_width()
        
        self.surface.blit(weather_splitter, (255 + width + gap, 145, 0, 0))
        width += gap*2
        
        # One item
        weather_max_1 = text_object("72", "Light", 28, 255)
        self.surface.blit(weather_max_1, (255 + width, 145 ,0,0))
        weather_min_1 = text_object("65", "Thin", 28, 255)
        self.surface.blit(weather_min_1, (255 + width, 176,0,0))
        
        # Sun rise & Sun down
        img = cached_Images["sunrise"]
        self.surface.blit(img, (248, 215))
        
        weather_sunrise = text_object("06:00", "Light", 26, 255)
        self.surface.blit(weather_sunrise, (248 + 32, 215))
        
        img = cached_Images["sunset"]
        self.surface.blit(img, (248 + 70 +32, 215))
        
        weather_sunrise = text_object("19:32", "Light", 26, 255)
        self.surface.blit(weather_sunrise, (248 + 70 + 64, 215))
        
        ## Other days
        # One item
        height = 250 + weather_status.get_height()
        
        weather_day = text_object("Mån", "Regular", 28, 255)
        self.surface.blit(weather_day, (0, height,0,0))
        
        img = cached_Images["weather_1_small"]
        self.surface.blit(img, (250 / 2 - img.get_width() / 2 , height))

        weather_min_0 = text_object("65", "Thin", 28, 255)
        self.surface.blit(weather_min_0, (250 - weather_min_0.get_width(), height + 1,0,0))
        
        weather_max_0 = text_object("72", "Light", 28, 255)
        self.surface.blit(weather_max_0, (250 - weather_min_0.get_width() - weather_max_0.get_width() - 4, height,0,0))
        
        height += weather_day.get_height() + 3
        
        img = cached_Images["line_2"]
        self.surface.blit(img, (0, height))
        height += 3
        
        #One item
        weather_day = text_object("Tis", "Regular", 28, 255)
        self.surface.blit(weather_day, (0, height,0,0))
        
        img = cached_Images["weather_1_small"]
        self.surface.blit(img, (250 / 2 - img.get_width() / 2 , height))

        weather_min_0 = text_object("65", "Thin", 28, 255)
        self.surface.blit(weather_min_0, (250 - weather_min_0.get_width(), height + 1,0,0))
        
        weather_max_0 = text_object("72", "Light", 28, 255)
        self.surface.blit(weather_max_0, (250 - weather_min_0.get_width() - weather_max_0.get_width() - 4, height,0,0))
        
        height += weather_day.get_height() + 3
        
        img = cached_Images["line_2"]
        self.surface.blit(img, (0, height))
        height += 3
        
        #One item
        weather_day = text_object("Ons", "Regular", 28, 255)
        self.surface.blit(weather_day, (0, height,0,0))
        
        img = cached_Images["weather_1_small"]
        self.surface.blit(img, (250 / 2 - img.get_width() / 2 , height))

        weather_min_0 = text_object("65", "Thin", 28, 255)
        self.surface.blit(weather_min_0, (250 - weather_min_0.get_width(), height + 1,0,0))
        
        weather_max_0 = text_object("72", "Light", 28, 255)
        self.surface.blit(weather_max_0, (250 - weather_min_0.get_width() - weather_max_0.get_width() - 4, height,0,0))
        
        height += weather_day.get_height() + 3
        
        img = cached_Images["line_2"]
        self.surface.blit(img, (0, height))
        height += 3
        
        #One item
        weather_day = text_object("Tors", "Regular", 28, 255)
        self.surface.blit(weather_day, (0, height,0,0))
        
        img = cached_Images["weather_1_small"]
        self.surface.blit(img, (250 / 2 - img.get_width() / 2 , height))

        weather_min_0 = text_object("65", "Thin", 28, 255)
        self.surface.blit(weather_min_0, (250 - weather_min_0.get_width(), height + 1,0,0))
        
        weather_max_0 = text_object("72", "Light", 28, 255)
        self.surface.blit(weather_max_0, (250 - weather_min_0.get_width() - weather_max_0.get_width() - 4, height,0,0))
        
        
        self.surface.set_alpha(self.alpha)
        
        # rotate
        widget.rotate(self)

class southtext_Object(widget):
    pos = None
    
    def __init__(self,alpha):
        widget.__init__(self, alpha)
    def update(self):
        self.surface = Box_container(True, screen.get_width() /2, screen.get_height())
        
        string = splitString("bla blab lab lab labl abl alb labla blab lab labl abla", 30)
        
        for item in string:
            self.surface.add_surface(text_object(item, "Thin", 60, 255))
        
        self.surface.set_anchor(Box_container.S)
        self.surface.set_padding(0, 25)

        ww, pos = self.surface.draw()
        self.surface = ww
        
        self.surface.set_alpha(self.alpha)
        
        self.pos = pos
        
        # rotate
        widget.rotate(self)
    def get_pos(self):
        return self.pos

class pota_Object(widget):
    pos = None
    
    def __init__(self,alpha):
        widget.__init__(self, alpha)
    def update(self):
        self.surface = Box_container(True, screen.get_width() /2, screen.get_height() / 2)
        self.surface.add_surface(text_object(name, "Thin", 82, 255))
        
        self.surface.set_anchor(Box_container.C)
        self.surface.set_padding(0, 0)

        ww, pos = self.surface.draw()
        self.surface = ww
        
        self.surface.set_alpha(self.alpha)
        
        
        self.pos = pos
        
        # rotate
        widget.rotate(self)
    def get_pos(self):
        return self.pos

class quote_Object(widget):
    pos = None
    
    def __init__(self,alpha):
        widget.__init__(self, alpha)
    def update(self):
        self.surface = Box_container(True, screen.get_width() /2, screen.get_height() / 2)
        
        string = splitString("bla blab lab lab labl abl alb labla blab lab labl abla", 35)
        
        for item in string:
            self.surface.add_surface(text_object(item, "Thin", 42, 255))
 
        self.surface.add_surface(text_object("- Omar Hindawi", "Light", 24, 175))
        
        self.surface.set_anchor(Box_container.C)
        self.surface.set_padding(0, 0)

        ww, pos = self.surface.draw()
        self.surface = ww
        
        self.surface.set_alpha(self.alpha)
                
        self.pos = pos
        
        # rotate
        widget.rotate(self)
    def get_pos(self):
        return self.pos

class dateTime_Object(widget):
    def __init__(self,alpha):
        widget.__init__(self, alpha)
    def update(self):
        self.surface = pygame.Surface((450, 300))
        
        text_1 = text_object(time.strftime("%A").capitalize(), "Ultralight", 60, 255)
        width = self.surface.get_width() - text_1.get_width()
        height = 0
        self.surface.blit(text_1, (width,height))
        height += text_1.get_height()
        
        text_2 = text_object(time.strftime("%B %d, %Y").capitalize(), "Thin", 60, 255)
        width = self.surface.get_width() - text_2.get_width()
        self.surface.blit(text_2, (width, height))
        height += text_2.get_height()
        
        text_3 = text_object(time.strftime("%S"), "Ultralight", 52, 180)
        width = self.surface.get_width() - text_3.get_width()
        self.surface.blit(text_3, (width, height))
        
        text_4 = text_object(time.strftime("%H:%M"), "Ultralight", 95, 255)
        width = self.surface.get_width() - text_1.get_width() - 127
        
        self.surface.blit(text_4,(width, height - 10))
        
        

        
        self.surface.set_alpha(self.alpha)

        # rotate
        widget.rotate(self)

class loading_Object(widget):
    pos = None
    
    def __init__(self,alpha):
        widget.__init__(self, alpha)
    def update(self):
        self.surface = Box_container(True, screen.get_width() /2, screen.get_height() / 2)
        self.surface.add_surface(text_object("Laddar...", "Thin", 60, 255))
        
        self.surface.set_anchor(Box_container.C)
        self.surface.set_padding(0, 0)

        ww, pos = self.surface.draw()
        self.surface = ww
        
        self.surface.set_alpha(self.alpha)

        self.pos = pos
        
        # rotate
        widget.rotate(self)
    def get_pos(self):
        return self.pos

class nyheter_Object(widget):
    def __init__(self,alpha):
        widget.__init__(self,alpha)
    def update(self):
        self.surface = pygame.Surface((250, 160))
        
        header = text_object("Nyheter", "Thin", 32, 255)
        self.surface.blit(header, (self.surface.get_width() - header.get_width(), 0, 0 ,0))
        self.surface.blit(cached_Images['line'],(0, header.get_height() + 3, 0 ,0))
        height = header.get_height() + 6
        
        self.surface.blit(text_object("1m sen", "Thin", 16, 240), (0, height, 0, 0))
        t = "Bla bl abla bla bla blev skjuten igår natt omg vilken fucking skandal"
        text = text_object((t[:32] + '..') if len(t) > 32 else t, "Light", 16, 255)
        self.surface.blit(text, (self.surface.get_width() - text.get_width(), height, 0, 0))
        height += text.get_height() + 3
        
        self.surface.blit(text_object("1m sen", "Thin", 16, 190), (0, height, 0, 0))
        t = "Bla bl abla bla bla blev skjuten igår natt omg vilken fucking skandal"
        text = text_object((t[:32] + '..') if len(t) > 32 else t, "Light", 16, 200)
        self.surface.blit(text, (self.surface.get_width() - text.get_width(), height, 0, 0))
        height += text.get_height() +3
        
        self.surface.blit(text_object("1m sen", "Thin", 16, 140), (0, height, 0, 0))
        t = "Bla bl abla bla bla blev skjuten igår natt omg vilken fucking skandal"
        text = text_object((t[:32] + '..') if len(t) > 32 else t, "Light", 16, 150)
        self.surface.blit(text, (self.surface.get_width() - text.get_width(), height, 0, 0))
        height += text.get_height() + 3
        
        self.surface.blit(text_object("1m sen", "Thin", 16, 90), (0, height, 0, 0))
        t = "Bla bl abla bla bla blev skjuten igår natt omg vilken fucking skandal"
        text = text_object((t[:32] + '..') if len(t) > 32 else t, "Light", 16, 100)
        self.surface.blit(text, (self.surface.get_width() - text.get_width(), height, 0, 0))
        height += text.get_height() + 3
        
        self.surface.blit(text_object("1m sen", "Thin", 16, 40), (0, height, 0, 0))
        t = "Bla bl abla bla bla blev skjuten igår natt omg vilken fucking skandal"
        text = text_object((t[:32] + '..') if len(t) > 32 else t, "Light", 16, 50)
        self.surface.blit(text, (self.surface.get_width() - text.get_width(), height, 0, 0))
        
        self.surface.set_alpha(self.alpha)

        # rotate
        widget.rotate(self)

class aktiviteter_Object(widget):
    def __init__(self,alpha):
        widget.__init__(self,alpha)
    def update(self):
        self.surface = pygame.Surface((250, 160))
        
        header = text_object("Aktiviteter", "Thin", 32, 255)
        self.surface.blit(header, (self.surface.get_width() - header.get_width(), 0, 0 ,0))
        self.surface.blit(cached_Images['line'],(0, header.get_height() + 3, 0 ,0))
        height = header.get_height() + 6
        
        self.surface.blit(text_object("Nu", "Thin", 16, 240), (0, height, 0, 0))
        t = "Bla bl abla bla bla blev skjuten igår natt omg vilken fucking skandal"
        text = text_object((t[:32] + '..') if len(t) > 32 else t, "Light", 16, 255)
        self.surface.blit(text, (self.surface.get_width() - text.get_width(), height, 0, 0))
        height += text.get_height() + 3
        
        self.surface.blit(text_object("Om 15m", "Thin", 16, 190), (0, height, 0, 0))
        t = "Bla bl abla bla bla blev skjuten igår natt omg vilken fucking skandal"
        text = text_object((t[:32] + '..') if len(t) > 32 else t, "Light", 16, 200)
        self.surface.blit(text, (self.surface.get_width() - text.get_width(), height, 0, 0))
        height += text.get_height() +3
        
        self.surface.blit(text_object("Om 1v", "Thin", 16, 140), (0, height, 0, 0))
        t = "Bla bl abla bla bla blev skjuten igår natt omg vilken fucking skandal"
        text = text_object((t[:32] + '..') if len(t) > 32 else t, "Light", 16, 150)
        self.surface.blit(text, (self.surface.get_width() - text.get_width(), height, 0, 0))
        height += text.get_height() + 3
        
        self.surface.blit(text_object("Om 3v", "Thin", 16, 90), (0, height, 0, 0))
        t = "Bla bl abla bla bla blev skjuten igår natt omg vilken fucking skandal"
        text = text_object((t[:32] + '..') if len(t) > 32 else t, "Light", 16, 100)
        self.surface.blit(text, (self.surface.get_width() - text.get_width(), height, 0, 0))
        height += text.get_height() + 3
        
        self.surface.blit(text_object("Om 1år", "Thin", 16, 40), (0, height, 0, 0))
        t = "Bla bl abla bla bla blev skjuten igår natt omg vilken fucking skandal"
        text = text_object((t[:32] + '..') if len(t) > 32 else t, "Light", 16, 50)
        self.surface.blit(text, (self.surface.get_width() - text.get_width(), height, 0, 0))
        
        self.surface.set_alpha(self.alpha)

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
    
    # set Objects
    fader.add(0, weather_object, 25, None)
    fader.add(0, southtext_object, 25, None)
    # fader.add(0, pota_object, 25, None)
    fader.add(0, dateTime_object, 25, None)
    fader.add(0, nyheter_object, 25, None)
    # fader.add(0, quote_object, 25, None)
    fader.add(0, aktiviteter_object, 25, None)
    
    screen.fill(black)
    
    while Running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
        
        # rotatetd
        if rotated:
            screen.fill(black)
            rotated = False
        
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
            screen.blit(weather_object.get_surface(), (25, 25, 0 , 0))
            screen.blit(dateTime_object.get_surface(), (screen.get_width() - dateTime_object.get_surface().get_width() - 25, 25, 0 , 0))
            screen.blit(pota_object.get_surface(), pota_object.get_pos())
            screen.blit(quote_object.get_surface(), quote_object.get_pos())
            screen.blit(southtext_object.get_surface(), southtext_object.get_pos())
            
            screen.blit(nyheter_object.get_surface(), (screen.get_width() - nyheter_object.get_surface().get_width() - 25, screen.get_height() - nyheter_object.get_surface().get_height() - 25))
            screen.blit(aktiviteter_object.get_surface(), (screen.get_width() - aktiviteter_object.get_surface().get_width() - 25, screen.get_height() - nyheter_object.get_surface().get_height() - aktiviteter_object.get_surface().get_height() - 25))
        elif rotation == 1:
            screen.blit(weather_object.get_surface(), (25, screen.get_height() - weather_object.get_surface().get_height() - 25, 0 , 0))
            screen.blit(dateTime_object.get_surface(), (25, 25, 0, 0))
            screen.blit(pota_object.get_surface(), (screen.get_width() / 2 - pota_object.get_surface().get_width() / 2, screen.get_height() / 2 - pota_object.get_surface().get_height() / 2, 0 ,0))
            screen.blit(quote_object.get_surface(), (screen.get_width() / 2 - quote_object.get_surface().get_width(), screen.get_height() / 2 - quote_object.get_surface().get_height() / 2, 0 ,0))
            screen.blit(southtext_object.get_surface(), (screen.get_width() - southtext_object.get_surface().get_width(), screen.get_height() / 2 - southtext_object.get_surface().get_height() / 2))
            
            screen.blit(nyheter_object.get_surface(), (screen.get_width() - nyheter_object.get_surface().get_width() - 25, 25))
            screen.blit(aktiviteter_object.get_surface(), (screen.get_width() - nyheter_object.get_surface().get_width() - aktiviteter_object.get_surface().get_width() - 25, 25))
        elif rotation == 2:
            screen.blit(weather_object.get_surface(), (screen.get_width() - weather_object.get_surface().get_width() - 25, screen.get_height() - weather_object.get_surface().get_height() - 25, 0 , 0))
            screen.blit(dateTime_object.get_surface(), (25, screen.get_height() - dateTime_object.get_surface().get_height() - 25, 0 , 0))
            screen.blit(pota_object.get_surface(), pota_object.get_pos())
            screen.blit(quote_object.get_surface(), quote_object.get_pos())
            screen.blit(southtext_object.get_surface(), (screen.get_width()/2 - southtext_object.get_surface().get_width() / 2, southtext_object.get_surface().get_height() / 2))
            
            screen.blit(nyheter_object.get_surface(), (25, 25))
            screen.blit(aktiviteter_object.get_surface(), (25, 25 + nyheter_object.get_surface().get_height()))
        elif rotation == 3:
            screen.blit(weather_object.get_surface(), (screen.get_width() - weather_object.get_surface().get_width() - 25, 25, 0 , 0))
            screen.blit(dateTime_object.get_surface(), (screen.get_width() - dateTime_object.get_surface().get_width() - 25, screen.get_height() - dateTime_object.get_surface().get_height() - 25, 0 , 0))
            screen.blit(pota_object.get_surface(), (screen.get_width() / 2 - pota_object.get_surface().get_width() / 2, screen.get_height() / 2 - pota_object.get_surface().get_height() / 2, 0 ,0))
            screen.blit(quote_object.get_surface(), (screen.get_width() / 2 - quote_object.get_surface().get_width() / 2, screen.get_height() / 2 - quote_object.get_surface().get_height() / 2, 0 ,0))
            screen.blit(southtext_object.get_surface(), (southtext_object.get_surface().get_width(), screen.get_height() / 2 - southtext_object.get_surface().get_height() / 2))
            
            screen.blit(nyheter_object.get_surface(), (25, screen.get_height() - 25 - nyheter_object.get_surface().get_height()))
            screen.blit(aktiviteter_object.get_surface(), (25 + nyheter_object.get_surface().get_width(), screen.get_height() - 25 - aktiviteter_object.get_surface().get_height()))
        
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