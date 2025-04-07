import machine
import time

led = machine.Pin('LED', machine.Pin.OUT)

def blink_onboard_led(num_blinks,freq=.2):    
    for i in range(num_blinks):
        led.on()
        time.sleep(freq)
        led.off()
        time.sleep(freq)

def toggle_onboard_led():
    led.toggle()
