"""
MicroPython webserver for distance sensor project
* Uses HCSR04 ultrasonic distance sensor
* Asynchrounous webserver reports distance (mm) in json format
Power failure tolerant
"""

import gc
import json
import network
import uasyncio as asyncio
import _thread
from machine import Pin, I2C
import time
from secrets import secrets
from hcsr04 import HCSR04

ssid = secrets['ssid']
password = secrets['wifi_password']

# setup onboard LED
led = Pin("LED", Pin.OUT, value=0)

# setup ultrasonic distanc sensor
sensor = HCSR04(trigger_pin=2, echo_pin=3, echo_timeout_us=10000)

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

async def serve_client(reader, writer):
    print("Client connected")
    request_line = await reader.readline()
    request_line = str(request_line)
    # We are not interested in HTTP request headers, skip them
    while await reader.readline() != b"\r\n":
        pass

    distance = sensor.distance_mm()
    print(distance)
    mydict = {"distance": distance}
    response = json.dumps(mydict)
    writer.write('HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n')
    writer.write(response)

    await writer.drain()
    await writer.wait_closed()
    # print("Client disconnected")

async def main():
    print('Connecting to Network...')
    connect()

    print('Setting up webserver...')
    asyncio.create_task(asyncio.start_server(serve_client, "0.0.0.0", 80))

    loop_count = 0
    while True:
        # Test WiFi connection twice per minute
        if loop_count == 30:
            loop_count = 0
            if not wlan.isconnected():
                wlan.disconnect()
                success = connect()

        # Flash LED
        led.on()
        await asyncio.sleep(0.1)
        led.off()
        await asyncio.sleep(0.9)

try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()
