import RPi.GPIO as GPIO

channel = 23
channel2 = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(channel2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def alert(ev=None):
    print("Tilt 1")

def alert2(ev=None):
    print("Tilt 2")

def loop():
    GPIO.add_event_detect(channel, GPIO.FALLING, callback=alert, bouncetime=1000)
    GPIO.add_event_detect(channel2, GPIO.FALLING, callback=alert2, bouncetime=1000)
    while True:
        pass

if  __name__ == '__main__':
    try:
        loop()
    except KeyboardInterrupt:
        print("interrupt")
        GPIO.cleanup()