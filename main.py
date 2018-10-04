import tkinter as tk
from tkinter import font
from tkinter import Canvas
import threading
import datetime
import locale
import time
import feedparser
import pygame

# Configurations
locale.setlocale(locale.LC_ALL, "sv_SE")


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

win = Gtk.Window()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()

'''
# Bluetooth and Wifi settings
bluetooth_connected = None
wifi_connected = None



# Canvas
canvas = None



#Widgets
## Date & Time
thread_time = None
datetime_day = None
datetime_date = None
datetime_time = None

## Weather

thread_weather = None

## Aftonbladet
aftonbladet_rss = "https://www.aftonbladet.se/nyheter/rss.xml"
aftonbladet_max_news = 10
thread_aftonbladet = None

## Aktiviteter


## Centered text
centered_text = 0

# APPLICATION
class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.widget_datetime()
        self.widget_centeredtext()
        
    def widget_datetime(self):
        global canvas, datetime_day, datetime_date, datetime_time
        canvas = tk.Canvas(self, bg="black", highlightthickness=0, 
                                width=self.winfo_screenwidth(), height=self.winfo_screenheight())
        canvas.pack()

        datetime_day = canvas.create_text(self.winfo_screenwidth() - 10, 10, 
                                          anchor = tk.NE, fill="white",font=("SF Pro Display UltraLight", 36, "normal"), 
                                          text=("%s" % "Laddar..."))
        datetime_date = canvas.create_text(self.winfo_screenwidth() - 10, (36 + 10) * 1 + 10, 
                                          anchor = tk.NE, fill="white",font=("SF UI Display", 48, "normal"))
        datetime_time = canvas.create_text(self.winfo_screenwidth() - 10, (36 + 10) * 1 + (48 + 10) + 10, 
                                          anchor = tk.NE, fill="white",font=("SF UI Display", 64, "normal"))
        #w.itemconfig(self.text_id, text=("%d" % text_id.winfo_width()))

    def widget_centeredtext(self):
        global canvas, centered_text
        centered_text = canvas.create_text(self.winfo_screenwidth()/2, self.winfo_screenheight() - 25, 
                                          anchor = tk.S, fill="white",font=("SF UI Display", 26, "normal"), 
                                          text="Godmorgon Omar!", justify=tk.CENTER)



# Thread Time update
class Thread_updatetime(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.event = threading.Event() # An event object.
        
    def stop(self):
        self.event.set()
        
    def run(self):
        global canvas, datetime_day, datetime_date, datetime_time, centered_text
        while not self.event.isSet():
            # Update time
            date = datetime.datetime.now()
            canvas.itemconfig(datetime_day, text=("%s" % date.strftime("%A").title()))
            canvas.itemconfig(datetime_date, text=("%s" % date.strftime("%B %d, %Y").title()))
            canvas.itemconfig(datetime_time, text=("%s" % date.strftime("%H:%M")))
            
            time_hours = int(date.strftime("%H"))
            time_minutes = int(date.strftime("%M"))
            
            # Check if a centered text should be written
            file = open("data/centered_text.txt", "r") 
            for line in file: 
                lines = line.split(" ", 2)
                time1 = lines[0].split(":")
                time1_h = int(time1[0])
                time1_m = int(time1[1])
                time2 = lines[1].split(":")
                time2_h = int(time2[0])
                time2_m = int(time2[1])
                message = lines[2]
                if (time_hours >= time1_h) and (time_minutes >= time1_m) and (time_hours <= time2_h):
                    if time_hours == time2_h and time_minutes > time2_m:
                        continue
                    canvas.itemconfig(centered_text, text=message)
                    break
            file.close()
            
            time.sleep(1)

# Thread Aftonbladet
class Thread_aftonbladet(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.event = threading.Event() # An event object.
        
    def stop(self):
        self.event.set()
        
    def run(self):
        global canvas, aftonbladet_rss, aftonbladet_max_news
        while not self.event.isSet():
            rss = feedparser.parse(aftonbladet_rss)
            # Get 10 RSS Feeds
            for i in range(aftonbladet_max_news):
                title = rss['items'][i]['title']
                date = rss['items'][i]['published'].rsplit(":", 1)[0]
                
                # Save feed in data file
                
            time.sleep(1)

# Thread Weather
class Thread_weather(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.event = threading.Event() # An event object.
        
    def stop(self):
        self.event.set()
        
    def run(self):
        global canvas
        while not self.event.isSet():

            time.sleep(1)


# MAIN
def USER_HAS_CLOSED_WINDOW():
        print ("Ending threads")
        thread_time.stop()
        thread_aftonbladet.stop()
        thread_weather.stop()
        root.destroy()

        
root = tk.Tk()
root.attributes("-fullscreen", True)
root.protocol("WM_DELETE_WINDOW", USER_HAS_CLOSED_WINDOW)


app = Application(master=root)


# Start threads
thread_time = Thread_updatetime()
thread_time.start()

thread_aftonbladet = Thread_aftonbladet()
thread_aftonbladet.start()

thread_weather = Thread_weather()
thread_weather.start()

thread_bluetooth = Thread_bluetooth()
thread_bluetooth.start()

thread_wifi = Thread_wifi()
thread_wifi.start()

thread_gpio = Thread_gpio()
thread_gpio.start()

# Start application
app.mainloop()
'''