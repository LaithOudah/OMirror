from wifi import Cell, Scheme

def Connect(ssid, key):
    scheme = Scheme.for_cell('wlan0', 'main', cell, key)
    scheme.save()
    scheme.activate()
    
    scheme = Scheme.find('wlan0', 'main')
    scheme.activate()