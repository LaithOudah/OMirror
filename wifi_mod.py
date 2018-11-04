from wifi import Cell, Scheme

cells = None

def Scan():
    global cells
    cells = Cell.all('wlan0')


def Connect(name, key):
    cell = None
    for c in cells:
        if c.ssid == name:
            cell = c
            break
    
    if cell is not None:
        scheme = Scheme.for_cell('wlan0', 'home', cell, key)
        scheme.delete()
        scheme.save()
        scheme.activate()


Scan()
Connect("TN_24GHz_B89617", "A3TK976GLH")