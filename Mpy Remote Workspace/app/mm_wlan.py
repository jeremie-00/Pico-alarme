#import uasyncio as asyncio
import network, time

from utils.led_pico import blink_onboard_led


def get_wlan():
    wlan = network.WLAN(network.STA_IF)
    return wlan

def connect_to_network(ssid, password, retries=10, verbose=True):  
    wlan = get_wlan()  
    wlan.active(True)
    wlan.config(pm = 0xa11140)  # Disable power-save mode
    wlan.connect(ssid, password) 
    
    if verbose: print('Connecting to ' + ssid, end=' ')
        
    while retries > 0 and wlan.status() != network.STAT_GOT_IP:
        retries -= 1
        if verbose: print('.', end='')
        time.sleep(1)      
    if wlan.status() != network.STAT_GOT_IP:
        if verbose: print('\nConnection failed. Check ssid and password')
        #raise RuntimeError('WLAN connection failed')
    else:
        blink_onboard_led(5,0.05)
        if verbose: print('\nConnected. IP Address = ' + wlan.ifconfig()[0]) 
        

def is_connected():  
    wlan = get_wlan()    
    return wlan.status() == network.STAT_GOT_IP