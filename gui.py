import sys, pygame
import time

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption('OMirror')
icon = pygame.image.load('images/icon.png')
pygame.display.set_icon(icon)

clock = pygame.time.Clock()

w, h = pygame.display.get_surface().get_size()
black = 0, 0, 0
white = 255, 255, 255

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

Running = True



def initialize():
    return 0

def app_loop():
    global Running
    
    initialize()
    
    while Running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
        
        screen.fill(black)
        
        # Widget Date Time
        widget_DateTime = Box_container(True, screen.get_width(), 0)
        widget_DateTime.add_surface(text_object("Måndag", "Ultralight", 60, 255))
        widget_DateTime.add_surface(text_object("September 05, 2018", "Thin", 60, 255))
        widget_DateTime.add_surface(text_object("04:20", "Ultralight", 120, 255))
        
        widget_DateTime.set_justify(Box_container.RIGHT)
        widget_DateTime.set_anchor(Box_container.NE)
        widget_DateTime.set_padding(10, 10)
        
        widget, pos = widget_DateTime.draw()
        
        screen.blit(widget, pos)
        
        # Widget South text
        widget_southtext = Box_container(True, screen.get_width() /2, screen.get_height())
        widget_southtext.add_surface(text_object("Godmorgon Nikki!", "Thin", 60, 255))
        
        widget_southtext.set_anchor(Box_container.S)
        widget_southtext.set_padding(0, 20)
        
        widget, pos = widget_southtext.draw()
        
        screen.blit(widget, pos)
        
        # Widget Weather
        widget_Weather = Box_container(False, 0, 0)
        
        ## Left part
        widget_W_Left = Box_container(True, 0, 0)
        
        ### Big Icon & Text
        widget_W_IconText = Box_container(True, 0, 0)
        try:
            widget_W_IconText.add_surface(pygame.image.load('images/weather_1.png'))
            
        except Exception:
            print("lol")
        widget_W_IconText.add_surface(text_object("Lätt Regn", "Regular", 30, 255))
        
        ### Other Days Forecast
        widget_W_otherdays = Box_container(True, 0, 0)
        
        #### Other day Widget
        widget_W_otherday_item = Box_container(False, 0, 0)
        widget_W_otherday_item.add_surface(text_object("Ons", "Thin", 28, 255))
        widget_W_otherday_item.add_surface(text_object("Icon", "Thin", 28, 255))
        widget, pos = widget_W_otherday_item.draw()
        widget_W_otherdays.add_surface(widget)
        
        widget_W_otherday_item = Box_container(False, 0, 0)
        widget_W_otherday_item.add_surface(text_object("Tors", "Thin", 28, 255))
        widget_W_otherday_item.add_surface(text_object("Icon", "Thin", 28, 255))
        widget, pos = widget_W_otherday_item.draw()
        widget_W_otherdays.add_surface(widget)
        
        widget_W_otherday_item = Box_container(False, 0, 0)
        widget_W_otherday_item.add_surface(text_object("Fre", "Thin", 28, 255))
        widget_W_otherday_item.add_surface(text_object("Icon", "Thin", 28, 255))
        widget, pos = widget_W_otherday_item.draw()
        widget_W_otherdays.add_surface(widget)
        
        widget_W_otherday_item = Box_container(False, 0, 0)
        widget_W_otherday_item.add_surface(text_object("Lör", "Thin", 28, 255))
        widget_W_otherday_item.add_surface(text_object("Icon", "Thin", 28, 255))
        widget, pos = widget_W_otherday_item.draw()
        widget_W_otherdays.add_surface(widget)
        
        
        widget, pos = widget_W_IconText.draw()
        widget_W_Left.add_surface(widget)
        widget, pos = widget_W_otherdays.draw()
        widget_W_Left.add_surface(widget)
        
        widget, pos = widget_W_Left.draw()
        widget_Weather.add_surface(widget)
        
        ## Right
        widget_W_Right = Box_container(True, 0, 0)
        widget_W_Right.add_surface(text_object("Växjö", "Ultralight", 60, 255))
        widget_W_Right.add_surface(text_object("72°", "Light", 84, 255))
        
        ### Two temp 
        widget_W_Twotemp = Box_container(False, 0 ,0)
        widget_W_Twotemp.add_surface(text_object("72", "Light", 28, 255))
        widget_W_Twotemp.add_surface(text_object("70", "Thin", 28, 255))
        widget, pos = widget_W_Twotemp.draw()
        widget_W_Right.add_surface(widget)
        
        widget_W_Twotemp = Box_container(False, 0 ,0)
        widget_W_Twotemp.add_surface(text_object("72", "Light", 28, 255))
        widget_W_Twotemp.add_surface(text_object("70", "Thin", 28, 255))
        widget, pos = widget_W_Twotemp.draw()
        widget_W_Right.add_surface(widget)
        
        widget_W_Twotemp = Box_container(False, 0 ,0)
        widget_W_Twotemp.add_surface(text_object("72", "Light", 28, 255))
        widget_W_Twotemp.add_surface(text_object("70", "Thin", 28, 255))
        widget, pos = widget_W_Twotemp.draw()
        widget_W_Right.add_surface(widget)
        
        widget_W_Twotemp = Box_container(False, 0 ,0)
        widget_W_Twotemp.add_surface(text_object("72", "Light", 28, 255))
        widget_W_Twotemp.add_surface(text_object("70", "Thin", 28, 255))
        widget, pos = widget_W_Twotemp.draw()
        widget_W_Right.add_surface(widget)
       
        widget_W_Right.set_padding(0, 300)
        widget, pos = widget_W_Right.draw()
        widget_Weather.add_surface(widget)

        widget_Weather.set_anchor(Box_container.NW)
        widget_Weather.set_padding(10, 10)
        
        widget, pos = widget_Weather.draw()
        
        screen.blit(widget, pos)
        
        # Widget Aftonbladet
        widget_Aftonbladet = Box_container(True, 0, 0)
        widget_Aftonbladet.add_surface(text_object("Aftonbladet", "Thin", 30, 255))
        
        widget_Aftonbladet_line = pygame.Surface((200, 1))
        widget_Aftonbladet_line.fill(white)
        widget_Aftonbladet.add_surface(widget_Aftonbladet_line)
        
        widget_Aftonbladet_item = Box_container(False, 0,0)
        widget_Aftonbladet_item.add_surface(text_object("Ons 04:22", "Light", 14, 255))
        widget_Aftonbladet_item.add_surface(text_object("Anklagelserna växer: Ytterligare en kvinna a...", "Thin", 14, 255))
        widget_Aftonbladet_item.set_alpha(255)
        widget, pos = widget_Aftonbladet_item.draw()
        widget_Aftonbladet.add_surface(widget_Aftonbladet_item)
        
        widget_Aftonbladet_item = Box_container(False, 0,0)
        widget_Aftonbladet_item.add_surface(text_object("Ons 04:22", "Light", 14, 255))
        widget_Aftonbladet_item.add_surface(text_object("Anklagelserna växer: Ytterligare en kvinna a...", "Thin", 14, 255))
        widget_Aftonbladet_item.set_alpha(204)
        widget, pos = widget_Aftonbladet_item.draw()
        widget_Aftonbladet.add_surface(widget_Aftonbladet_item)
        
        widget_Aftonbladet_item = Box_container(False, 0,0)
        widget_Aftonbladet_item.add_surface(text_object("Ons 04:22", "Light", 14, 255))
        widget_Aftonbladet_item.add_surface(text_object("Anklagelserna växer: Ytterligare en kvinna a...", "Thin", 14, 255))
        widget_Aftonbladet_item.set_alpha(153)
        widget, pos = widget_Aftonbladet_item.draw()
        widget_Aftonbladet.add_surface(widget_Aftonbladet_item)
        
        widget_Aftonbladet_item = Box_container(False, 0,0)
        widget_Aftonbladet_item.add_surface(text_object("Ons 04:22", "Light", 14, 255))
        widget_Aftonbladet_item.add_surface(text_object("Anklagelserna växer: Ytterligare en kvinna a...", "Thin", 14, 255))
        widget_Aftonbladet_item.set_alpha(102)
        widget, pos = widget_Aftonbladet_item.draw()
        widget_Aftonbladet.add_surface(widget_Aftonbladet_item)
        
        widget_Aftonbladet_item = Box_container(False, 0,0)
        widget_Aftonbladet_item.add_surface(text_object("Ons 04:22", "Light", 14, 255))
        widget_Aftonbladet_item.add_surface(text_object("Anklagelserna växer: Ytterligare en kvinna a...", "Thin", 14, 255))
        widget_Aftonbladet_item.set_alpha(51)
        widget, pos = widget_Aftonbladet_item.draw()
        widget_Aftonbladet.add_surface(widget_Aftonbladet_item)

        widget_Aftonbladet.set_justify(Box_container.RIGHT)
        
        # Widget Aktiviteter
        widget_Aktiviteter = Box_container(True, 0, 0)
        widget_Aktiviteter.add_surface(text_object("Aktiviteter", "Thin", 30, 255))
        
        
        widget_Aktiviteter_line = pygame.Surface((200, 1))
        widget_Aktiviteter_line.fill(white)
        widget_Aktiviteter.add_surface(widget_Aktiviteter_line)
        
        widget_Aktiviteter_item = Box_container(False, 0,0)
        widget_Aktiviteter_item.add_surface(text_object("Ons 04:22", "Light", 14, 255))
        widget_Aktiviteter_item.add_surface(text_object("Anklagelserna växer: Ytterligare en kvinna a...", "Thin", 14, 255))
        widget_Aktiviteter_item.set_alpha(255)
        widget, pos = widget_Aktiviteter_item.draw()
        widget_Aktiviteter.add_surface(widget_Aktiviteter_item)
        
        widget_Aktiviteter_item = Box_container(False, 0,0)
        widget_Aktiviteter_item.add_surface(text_object("Ons 04:22", "Light", 14, 255))
        widget_Aktiviteter_item.add_surface(text_object("Anklagelserna växer: Ytterligare en kvinna a...", "Thin", 14, 255))
        widget_Aktiviteter_item.set_alpha(204)
        widget, pos = widget_Aktiviteter_item.draw()
        widget_Aktiviteter.add_surface(widget_Aktiviteter_item)
        
        widget_Aktiviteter_item = Box_container(False, 0,0)
        widget_Aktiviteter_item.add_surface(text_object("Ons 04:22", "Light", 14, 255))
        widget_Aktiviteter_item.add_surface(text_object("Anklagelserna växer: Ytterligare en kvinna a...", "Thin", 14, 255))
        widget_Aktiviteter_item.set_alpha(153)
        widget, pos = widget_Aktiviteter_item.draw()
        widget_Aktiviteter.add_surface(widget_Aktiviteter_item)
        
        widget_Aktiviteter_item = Box_container(False, 0,0)
        widget_Aktiviteter_item.add_surface(text_object("Ons 04:22", "Light", 14, 255))
        widget_Aktiviteter_item.add_surface(text_object("Anklagelserna växer: Ytterligare en kvinna a...", "Thin", 14, 255))
        widget_Aktiviteter_item.set_alpha(102)
        widget, pos = widget_Aktiviteter_item.draw()
        widget_Aktiviteter.add_surface(widget_Aktiviteter_item)
        
        widget_Aktiviteter_item = Box_container(False, 0,0)
        widget_Aktiviteter_item.add_surface(text_object("Ons 04:22", "Light", 14, 255))
        widget_Aktiviteter_item.add_surface(text_object("Anklagelserna växer: Ytterligare en kvinna a...", "Thin", 14, 255))
        widget_Aktiviteter_item.set_alpha(51)
        widget, pos = widget_Aktiviteter_item.draw()
        widget_Aktiviteter.add_surface(widget_Aktiviteter_item)

        widget_Aktiviteter.set_justify(Box_container.RIGHT)
        
        # Widget bottom_right
        widget_bottomright = Box_container(True, screen.get_width(), screen.get_height())
        
        widget, pos = widget_Aftonbladet.draw()
        widget_bottomright.add_surface(widget_Aftonbladet)
        
        widget, pos = widget_Aktiviteter.draw()
        widget_bottomright.add_surface(widget_Aktiviteter)
        
        widget_bottomright.set_anchor(Box_container.SE)
        widget_bottomright.set_padding(10, 10)
        
        widget, pos = widget_bottomright.draw()
        
        screen.blit(widget, pos)
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    Running = False
            elif event.type == pygame.QUIT:
                Running = False
        
        clock.tick(60)
 

app_loop()
pygame.quit()
quit()