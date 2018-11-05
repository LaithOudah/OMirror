from scan import Cell
import SchemeWPA

cells = None

def Scan():
    global cells
    cells = Cell.all('wlan0')
    print(cells)


def Connect(name, key):
    cell = None
    for c in cells:
        if c.ssid == name:
            cell = c
            break
    
    if cell is not None:
        scheme = SchemeWPA.SchemeWPA('wlan0', cell.ssid,{"ssid": cell.ssid,"psk": key})
        scheme.delete()
        scheme.save()
        scheme.activate()


Scan()
Connect("TN_24GHz_B89617", "A3TK976GLH")