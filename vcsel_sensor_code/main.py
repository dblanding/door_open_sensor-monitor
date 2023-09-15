"""
MicroPython webserver for distance sensor project
* Uses VL53L0x time-of-flight distance sensor
* Asynchrounous webserver reports distance (mm) in json format
"""

import gc
import json
import network
import uasyncio as asyncio
import _thread
from machine import Pin, I2C
import time
from secrets import secrets
import VL53L0X

ssid = secrets['ssid']
password = secrets['wifi_password']

# setup onboard LED
led = Pin("LED", Pin.OUT, value=0)

def setup_tof_sensor(bus_id, sda_pin, scl_pin):
    """Setup a Vcsel sensor on an I2C bus.
    There are two available busses: 0 & 1.
    Return VL53L0X object."""
    sda = Pin(sda_pin)
    scl = Pin(scl_pin)

    print("setting up i2c%s" % bus_id)
    i2c = I2C(id=bus_id, sda=sda, scl=scl)
    print("Set up device %s on i2c%s" % (i2c.scan(), bus_id))

    return VL53L0X.VL53L0X(i2c)

tof0 = setup_tof_sensor(0, 16, 17)
tof0.start()

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

async def serve_client(reader, writer):
    print("Client connected")
    request_line = await reader.readline()
    request_line = str(request_line)
    # We are not interested in HTTP request headers, skip them
    while await reader.readline() != b"\r\n":
        pass

    distance = tof0.read()
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
    while True:

        # Flash LED
        led.on()
        await asyncio.sleep(0.1)
        led.off()
        await asyncio.sleep(0.9)

try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()
