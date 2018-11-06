from __future__ import print_function
import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service
import RPi.GPIO as GPIO

import array
try:
  from gi.repository import GObject
except ImportError:
  import gobject as GObject
import advertising
import gatt_server
import argparse

GPIO_BLUETOOTH = 26

def main():
    GPIO.setmode(GPIO.BCM)
    
    GPIO.setwarnings(False)
    GPIO.setup(GPIO_BLUETOOTH, GPIO.OUT)
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--adapter-name', type=str, help='Adapter name', default='')
    args = parser.parse_args()
    adapter_name = args.adapter_name

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    mainloop = GObject.MainLoop()

    advertising.advertising_main(mainloop, bus, adapter_name)
    gatt_server.gatt_server_main(mainloop, bus, adapter_name)
    # turn on led
    GPIO.output(GPIO_BLUETOOTH, 1)
    
    mainloop.run()

if __name__ == '__main__':
    main()
    GPIO.output(GPIO_BLUETOOTH, 0)
