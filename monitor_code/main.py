"""
MicroPython web client for monitoring distance sensor
and displaying whether object is detected (door open).
LED flashes 5x per second when door is detected (0 < dist < 200mm).
elif dist > 200mm, LED toggles once per second.
If unable to reach server, LED toggles once per 5 seconds.
Power Failure tolerant
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
    """Return True on successful connection, otherwise False"""
    wlan.active(True)
    wlan.config(pm = 0xa11140) # Disable power-save mode
    wlan.connect(ssid, password)

    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            print("wlan.status =", wlan.status())
            break
        max_wait -= 1
        print('waiting for connection...')
        time.sleep(1)

    if not wlan.isconnected():
        return False
    else:
        print('connected')
        status = wlan.ifconfig()
        print('ip = ' + status[0])
        return True

def network_connection_OK():
    if not wlan.status() == 3:
        return False
    else:
        return True

async def get_distance():
    """
    Get json data from server
    Return value of "distance"
    """
    headers = {'Accept': 'application/json'}
    dist  = -1
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
    count = 0  # seconds between readings
    while True:
        # Test WiFi connection twice per minute
        if count == 30:
            count = 0
            if not wlan.isconnected():
                wlan.disconnect()
                success = connect()

        count += 1
        if count % 5 == 0:
            dist = await get_distance()
            print(dist)

        if 0 < dist < 400:
            # Quick flash LED
            for rep in range(10):
                led.toggle()
                await asyncio.sleep(0.1)
        elif dist > 400:
            # Blink LED once per second
            led.on()
            await asyncio.sleep(0.1)
            led.off()
            await asyncio.sleep(0.9)
        else:
            # Blink LED once every 5 seconds
            if count == 0:
                led.on()
                await asyncio.sleep(0.1)
                led.off()
                await asyncio.sleep(4.9)
try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()
