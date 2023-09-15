"""
MicroPython web client for monitoring distance sensor
and displaying whether object is detected (door open).
Quick flashing LED when object is detected.
Otherwise, LED toggles once per second.
"""

import gc
import json
import network
import uasyncio as asyncio
from machine import Pin, I2C
import time
from secrets import secrets
import urequests as requests

ssid = secrets['ssid']
password = secrets['wifi_password']

# setup onboard LED
led = Pin("LED", Pin.OUT, value=0)

wlan = network.WLAN(network.STA_IF)

def connect():
    wlan.active(True)
    wlan.config(pm = 0xa11140) # Disable power-save mode
    wlan.connect(ssid, password)

    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        time.sleep(1)

    if wlan.status() != 3:
        raise RuntimeError('network connection failed')
    else:
        print('connected')
        status = wlan.ifconfig()
        ip = status[0]
        print('ip = ' + status[0])
    return ip

async def get_distance():
    """
    Get json data from server
    Return value of "distance"
    """
    headers = {'Accept': 'application/json'}
    dist  = 0
    try:
        resp = requests.get("http://192.168.1.65/", timeout=1.0)
        msg = resp.json()
        dist = msg["distance"]
    except OSError:
        pass
    return dist

async def main():
    """
    Get distance from distance sensor every 5 sec
    Flash LED
        Quickly if door is open
        Otherwise once per second.
    """
    print('Connecting to Network...')
    connect()
    dist = 0
    count = 5  # seconds between readings
    while True:
        count -= 1
        if count == 0:
            dist = await get_distance()
            print(dist)
            count = 5

        if 0 < dist < 400:
            # Quick flash LED
            for rep in range(10):
                led.toggle()
                await asyncio.sleep(0.1)
        else:
            # Blink LED once per second
            led.on()
            await asyncio.sleep(0.1)
            led.off()
            await asyncio.sleep(0.9)

try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()
