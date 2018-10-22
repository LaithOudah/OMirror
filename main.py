#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import os, time, locale
import data # Data
import rgb # RGB
import sys, pygame # GUI
import news, weather # News & Weather
import threading, socket

# variables
Running = True
internetConnection = False

name = ""
bluetooth_name = ""
wifi_pass = ""
wifi_ssid = ""
language = ""

autosleep = 0

## Init
pygame.init()
pygame.font.init()

locale.setlocale(locale.LC_TIME, "sv_SE.utf8")
  
#screen = pygame.display.set_mode((500, 500))
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

pygame.display.set_caption('OMirror')
icon = pygame.image.load('images/icon.png')
pygame.display.set_icon(icon)

clock = pygame.time.Clock()

w, h = pygame.display.get_surface().get_size()
black = 0, 0, 0
white = 255, 255, 255

# App get data thread
class app_getDataThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        while True:
            if(Running == False):
                break
            data.readData()
            
            checkData()
            
            # Check internet connection
            internetConnection = checkConnection()
            
            if internetConnection:
                news.news_Parse()
                weather.updateAll()


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
    global name,bluetooth_name, wifi_ssid, wifi_pass, autosleep, language
    
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



def initialize():
    
    rgb.init()
    
    Thread_getData.start()
    
    return 0
 
def buttonStatus():
    if(rgb.GPIO.input(rgb.GPIO_BUTTON) == False):
        rgb.RGB_on()
    else:
        screen.fill(black)
        rgb.RGB_off()

def app_loop():
    global Running
    
    # Show Loading screen
    screen.fill(black)
    
    widget_init = Box_container(True, screen.get_width() /2, screen.get_height() / 2)
    widget_init.add_surface(text_object("Laddar...", "Thin", 60, 255))
    
    widget_init.set_anchor(Box_container.C)
    widget_init.set_padding(0, 0)
    
    widget, pos = widget_init.draw()
    
    screen.blit(widget, pos)
    
    pygame.display.update()
    
    # Initialize
    initialize()
    
    while Running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
        
        screen.fill(black)
        
        # Widget Date Time
        widget_DateTime = Box_container(True, screen.get_width(), 0)
        widget_DateTime.add_surface(text_object(time.strftime("%A").capitalize(), "Ultralight", 60, 255))
        widget_DateTime.add_surface(text_object(time.strftime("%B %d, %Y").capitalize(), "Thin", 60, 255))
        widget_DateTime.add_surface(text_object(time.strftime("%H:%M"), "Ultralight", 120, 255))
        
        widget_DateTime.set_justify(Box_container.RIGHT)
        widget_DateTime.set_anchor(Box_container.NE)
        widget_DateTime.set_padding(10, 10)
        
        widget, pos = widget_DateTime.draw()
        
        screen.blit(widget, pos)
        
        # Prettiest of them all
        widget_pota = Box_container(True, screen.get_width() /2, screen.get_height() / 2)
        widget_pota.add_surface(text_object("Nikki", "Thin", 82, 255))
        
        widget_pota.set_anchor(Box_container.C)
        widget_pota.set_padding(0, 0)
        
        widget, pos = widget_pota.draw()
        
        screen.blit(widget, pos)
        
        # Widget South text
        widget_southtext = Box_container(True, screen.get_width() /2, screen.get_height())
        widget_southtext.add_surface(text_object("GODMORGON ÅMI", "Thin", 60, 255))
        
        widget_southtext.set_anchor(Box_container.S)
        widget_southtext.set_padding(0, 20)
        
        widget, pos = widget_southtext.draw()
        
        screen.blit(widget, pos)
            
        # BUTTON status
        buttonStatus()
        
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