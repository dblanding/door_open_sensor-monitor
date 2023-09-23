# Door Open Sensor & Monitor

## Here's the problem:


* In general, I try to keep the garage door closed except when it needs to be open.
* If I happen to be constantly going in and out (say I'm working in the yard), I leave it open.
* Occasionally, I will wake up in the morning and realize that I left the door open all night.
* Apparently, I need a reminder at the end of the day (before going to bed) to close the garage door if it is open.

![door open schematic](imgs/door_open.png)

## Here's the solution: Using micropython programs on Raspberry Pi Pico-W microcontrollers

* A **distance sensor** detects the presence of the garage door in the open position
    * The sensor publishes the distance on a webserver
* A remotely located **monitor** periodically requests the distance value from the sensor
    * The monitor (located where I will notice it before going to bed) flashes its onboard LED at a **rate** which is **tri-modal**:
        * 5 flashes per second if the door is open (distance is below a threshold value)
        * 1 flash per second if the door is closed (distance exceeds the threshold value)
        * 1 flash every 5 seconds if the distance value was not received

## Unanticipated problems (RF Interference with garage door opener)

### Welcome to real life!

* As anyone who has ever impemented a simple solution to a simple problem realizes, Murphy's Law is there to remind us that we have overlooked something.
* My first solution used a **VL53LOX VCSEL sensor** to measure the distance to the garage door.
    * Problem was that when the VCSEL was running, my garage door receiver was not responsive to button presses from the remote radio transmitter.
    * Apparently, the VCSEL circuitry generates RFI at a frequency that interferes with the operation of the opener's radio signal.
* My next solution was to try a **TF-Mini optical Lidar** module that I happened to have laying around.
    * Same problem
* Eventually, I used the **HC-SR04 ultrasonic distance sensor**.
    * It did the job and didn't generate RFI that interfered with the operation of the garage door opener radio signals.

![Sensor board](imgs/sensor.jpg)

![Breadboard Diagram](imgs/hc-sr04_bb.png)

