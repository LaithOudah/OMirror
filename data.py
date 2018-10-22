dataArray = {}

fileName = "settings/config.txt"

def readData():
    file = open(fileName, "r")
    
    for line in file:
        if line is not "":
            line = line.split("=")
            
            dataArray[line[0]] = line[1].replace("\n", "")
    file.close()

def setData(key, value):
    try:
        dataArray[key] = value
        return 1
    except IndexError:
        return 0

def addNewData(key, value):
    dataArray[key] = value

def writeData():
    file = open(fileName, "w")
    
    for k, v in dataArray.iteritems():
        string = "%s=%s\n" % (k, v)
        file.write(string)

    file.close()

def getData(key):
    return dataArray[key]