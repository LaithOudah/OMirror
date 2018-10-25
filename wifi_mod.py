from wifi import Cell, Scheme

def Connect(ssid, key):
    cell = list(Cell.all('wlan0'))[0]
    print(cell)
    
    scheme = Scheme.for_cell('wlan0', 'main', cell, key)
    scheme.save()
    scheme.activate()
    
    scheme = Scheme.find('wlan0', 'main')
    scheme.activate()

print("connecting")
Connect("TN_24GHz_B89617", "A3TK965GLH")
print("Failed")