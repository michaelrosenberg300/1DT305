# Tutorial on how to use temperature measurements to determine air flow direction
**Project by Michael Rosenberg (mr223xi) - 1DT305 Introduction to Applied Internet of Things, 7.5 credits**

## Objective
The course objective for this project is to "to build a connected sensor unit that provides a measured value that is presented over the internet". In addition that I added some personal objectives, namely learning how to use Python and getting familiar with GitHub. I also wanted to keep the project cheap and simple.

I already have a "smart home" with many sensors handled by HomeAssistant. Hence I did have some problems determining what kind of project to do. Finally I decided to try to measure air flow direction using two temperature sensors. My apartment built in 1949 has a passive ventilation system which does not always work as intended. Sometimes the system sucks cold air into the apartment instead of the opposite. In wintertime (when this is an actual problem) the air is very cold. My idea is to measure the incoming/outgoing temperature and compare it to a temperature inside the room. If the difference is "large" I can conclude that the air is flowing in the wrong direction. 

I decided to use Wi-Fi to communicate with the device (since it will be located in my home) and I also decided to use the MQTT protocol to transfer measurement data since that amount of data sent from the device will be low.

**Time estimate:** 60 hours including setting up electronics, installing IDE, develop the source code for the Lopy4 device, create data presentation and to test everything.
## Material
The material I used was the [basic IoT bundle kit from Electrokit](https://www.electrokit.com/produkt/lnu-1dt305-tillampad-iot-lopy4-basic-bundle/). From that bunde I more specifically used:


| Item | Description | Estimated price |
| -------- | -------- | -------- |
| Lopy4 with headers     | The micro controller needed for the sensor     | 300SEK     |
| Expansion board V3.1     |   Makes it easy to access the pins on the controller   | 170SEK     |
| 2 x Temperature sensors MCP9700     |  One for room temperature and one for the airflow    | 2*9 = 18SEK     |
| Breadboard     |   Used to be able to easy connect the sensors to the controller   | 59SEK     |
| Wires     |   To connect the sensors to the Lopy4   |   -   |
| **Total**     |      | **ca 550SEK**     |

This hardware is powered via USB from either a computer or a charger.

## Computer Setup
When developing software on my Macbook Pro for my Lopy4 I needed an *Integrated Development Environment (IDE)* to help me handle the source files in my project. I ended up with *Atom* because it includes a *Pymakr* plugin that can be used to flash the Lopy4 device via the REPL interface. The plugin can also (for example) execute single source files on target and you also have access to Pythons interactive environment, meaning that you can run individual Python commands on target. Atom also includes a syntax highlighter for Python.

To install Atom and the plugin use these [instructions](https://docs.pycom.io/gettingstarted/software/atom/).

Now the host is setup for development and it is a good idea to update the firmware (FW) of the target. Note that there are two firmwares to be updated, the FW on the Lopy4 and the FW on the expansion board.

To update the FW on the Lopy4 please follow these [instructions](https://docs.pycom.io/updatefirmware/device/).

When that is done update the FW on the expansion board with these [instructions](https://docs.pycom.io/updatefirmware/expansionboard/).

The second update is a little bit more complicated than the first one. First you need to make sure that you know the version of your expansion board and then you need to download a specific tool (`DFU-Util`) to your computer to do the update. Since I am running on MacOS I used Homebrew to install it and everything went smoothly.

## Putting everything together
After fitting the PyCom onto the expansion board the temperature sensors were added to the breadboard. Use the power from the expansion board the power them. See the picture below for proper wiring:

![](https://i.imgur.com/WSPr37n.png)

The pins between the Lopy4 device and the two MCP9700 sensors are connected according to:

| Device pin | Sensor pin number/name| 
| -------- | -------- | 
| 3V3     | 1 - V~DD~     | 
| GND     | 3 - GND     | 
| P15 and P16     | 2 - V~OUT~     | 

Now the device and the sensors are up and running and you should be able to control it from your host via Atom and the Pymakr plugin. 

The MCP9700 temperature sensors outputs a voltage proportional to the measured temperature. The Lopy4 reads the input pin and gets the voltage. This voltage needs to be converted into a temperature in software. 

In the data sheet for the [MCP9700 sensor]( http://ww1.microchip.com/downloads/en/devicedoc/20001942g.pdf) we see that the output is 500*mV* at 0*ºC* and the sensitivity of this *linear* sensor is 10*mV/ºC*. This gives us that *V~OUT~ =* 10*mV/ºC･T* + 500*mV* from which we can get the wanted temperature *T* (in degrees Celsius). 

Finally the device needs to get connected to the Wi-Fi in order to deliver measurements. This is done during the boot phase, see the `boot.py` file below.

## Platform
Once the device starts to collect data, the data needs to be stored and visualised somewhere. There are a number of more or less free cloud services that can provide this "out there". I decided to choose Ubidots STEM which is free to use. It includes a MQTT broker, a database (where data is stored for a limited time) and it includes a web interface to visualise data. There are some [limitations](https://help.ubidots.com/en/articles/639806-what-is-the-difference-between-ubidots-and-ubidots-stem) on how much data you can upload, but for this project that is not an issue.

Create an STEM account at [Ubidots](https://stem.ubidots.com) and you are ready to go! 

Ubidots uses a simple data structure where each device can have a number *variables* or time series connected to them. Once that data is uploaded to Ubidots there is a *dashboard* that you can use to visualise the data from your device. That is done by adding *widgets* of wanted type, for example a line graph.

Ubidots also provides something they call *syntetic variables* which is really that you can do some kind of processing/calculation on the uploaded data. I intended to use this feature to estimate the air flow direction (*cloud computing*). 

Via MQTT you are able to subscribe to a syntetic variable. Each time a syntetic variable is updated, you get an update. Please note that it can take quit some time for Ubidots to update its syntetic variables. My impression when testing it was that you can expect new values every 4-5 minutes.

**Unfortunately, I found out that Ubidots have some major restrictions on syntetic variables in the STEM edition**. Only very basic operations can be done with syntetic variables, which in turn forced me to do the air flow estimation in the Lopy4 device rather than in the cloud (which even could be the preferred way of doing it!).

In order to get access to the MQTT broker you need to have a *token*. This token can be found when you are logged in to Ubidots. From the meny `API credentials` the token can be found and copied into your Python code. The token shall be used as username and the password shall be an empty string when setting up the MQTT broker.
## The Code
The Lopy4 includes a flash file system where you store your Python-files. The Lopy4 device supports a sub-set of Python well suited for embedded systems.

When the Lopy4 is started up if looks for a file named`boot.py` and it runs it. Then the `main.py` file is next in turn to be run. There is also a folder named `/lib` where all libraries should be put for Python to find them.

All my source code can be found at [GitHub](https://github.com/michaelrosenberg300/1DT305).

In my boot file I connect to Wi-Fi and I use NTP to get the correct time (which is useful if you want to put timestamps on your measurements). All the needed credentials are hidden in the `secrets.py` file. 

```python=
import pycom
import secrets
import time
import sys
from network import WLAN
import machine

pycom.heartbeat(False)

wlan = WLAN(mode=WLAN.STA)

print('Trying to connect to wifi with SSID:', secrets.SSID)

try:
    wlan.connect(ssid=secrets.SSID, auth=(WLAN.WPA2, secrets.PASSWORD), timeout=10000)

    while not wlan.isconnected():
        time.sleep_ms(500)
        print(".", end = '')

    print('\nSuccessfully connected to network:', secrets.SSID)

except:
    print('\nNot possible to connect to wifi!')
    sys.exit()
    # Seems like main.py is running even if sys.exit() is executed. This
    # exception needs to be handled in main.py when setting up the MQTT connection.

# With Wifi up and running it is now possible to get a correct time from internet
rtc = machine.RTC()
rtc.ntp_sync("pool.ntp.org")

while not rtc.synced():
    machine.idle()

time.timezone(2*60**2)                      # Set timezone GMT+2
print("Current time:", time.localtime())
```

As previously mentioned I wanted to learn Python when doing this course. Therefore the implementation is probably a bit overkill. I decided to do a simple object oriented abstraction of the sensors. The result was support for one physical sensor, the MCP9700, and one "virtual" sensor, the air flow estimator. 

The base sensor class also calculates things like max/min and average values which (of course) could be done in the cloud instead. 

Have a look in my [GitHub](https://github.com/michaelrosenberg300/1DT305) to see the details. Here I only show the MCP9700 class and the air flow direction estimator class:

```python=
class AirFlowEstimator(Sensor):
#
# The class used to estimate the direction of the airflow
#
    def __init__(self, SensorName):

        self.State = UNKNOWN
        super().__init__(9, 0, SensorName)         # Create a filter of length 9

    def PerformMeasurement(self, T_delta):

        self.T = T_delta
        super().PerformMeasurement()

    def GetState(self):

        if abs(self.GetAverage()) > 2.0:     # If temperature difference is larger than 2 degrees...
            self.State = AIR_IN              # ... it is assumed that air is going in the "wrong" direction
        else:
            self.State = AIR_OUT

        return self.State


class MCP9700E(Sensor):
#
# A MCP9700E class that only contains things that are specific to the MCP9700E
# sensor like hot it is connected to the Pycom and how temperature is
# calculated from the measured voltage.
#
    def __init__(self, SensorName, pin):
        # Initiate the ADC input to be able to make measurements
        self.pin = pin

        self.adc = machine.ADC()
        self.apin = self.adc.channel(pin=self.pin)

        super().__init__(9, 0, SensorName)         # Create a filter of length 9

    def PerformMeasurement(self):
        #
        # From data sheets we get that the sensor is linear with sensitivity
        # 10mV/C and that for 0C the output is 500mV. This gives us
        #
        #   V_out = 10mv/C*T + 500mV which gives us the wanted temperature:
        #
        #   T = (V_out - 0.5)/0.01 (units in Volts and C)
        #

        V = self.apin.voltage()/1000    # Convert to V from mV
        self.T = (V-0.5)/0.01           # Convert to T from V

        super().PerformMeasurement()
```
Since the MCP9700 sensors are analog they are connected to P15 and P16 so that Lopy4 can get readings from them. The `main.py` program shows how everything is carried out:

```python=
# Import standard libraries
import pycom
import time
from mqtt import MQTTClient
import json
from machine import Timer
from micropython import const

# Import custom libraries
import sensors
import secrets

devicename = "AirFlowMeter"
topic = "/v1.6/devices/" + devicename

GREEN = const(0x00FF00)
RED = const(0xFF0000)

pycom.rgbled(RED)

# The callback that is used by the timer that triggers every 10th minute
# when the airflow estimate is to be updated.
def UpdateLED_cb(alarm):
    global MyEstimator

    if MyEstimator.GetState() == sensors.AIR_OUT:       # Outgoing airflow...
        pycom.rgbled(GREEN)                             # ... and green LED
    else:
        pycom.rgbled(RED)

    print("State:", MyEstimator.GetState())
    print("Alarm triggered at:", time.localtime())

# Setup the two temperature sensors
MyRoomTemp = sensors.MCP9700E('MCP9700E_Room', 'P15')           # Room Temperature at input pin 15
MyTemp = sensors.MCP9700E('MCP9700E', 'P16')                    # Air flow Temperature at input pin 16
MyEstimator = sensors.AirFlowEstimator('AirFlowEstimator')      # The air flow estimator

# Setup connection to MQTT broker
try:
    client = MQTTClient(devicename, "industrial.api.ubidots.com", user=secrets.TOKEN, password='', port=1883)
    client.connect()

except:
    print('Not possible to create connection to MQTT-broker. Please check your wifi!')
    # No point in continuing exeution if not able to connect to the broker
    sys.exit()

# Setup the alarm needed to handle the LED update with hysteresis
Timer.Alarm(UpdateLED_cb, 1.0*60*10, periodic=True)

# Main infinite loop
while True:
    MyRoomTemp.PerformMeasurement()         # Trigger a temperature measurement
    MyTemp.PerformMeasurement()             # Trigger a temperature measurement
    MyEstimator.PerformMeasurement(MyTemp.Get() - MyRoomTemp.Get())

    TemperatureData = {"Room_Temperature": MyRoomTemp.Get(), "Air_Temperature": MyTemp.Get(), "T_delta": MyEstimator.Get(), "T_deltaAvg": MyEstimator.GetAverage()}

    client.publish(topic, msg=json.dumps(TemperatureData), qos=0)

    print("Time:", time.localtime(), "\nData", TemperatureData)
    time.sleep(60)                      # One new measurement every minute
```

First the temperature sensors are created and then the connection to the Ubidots MQTT broker is set up. I use the standard Lopy4 MQTT library to do that and I also added some error handling to make sure that the connection is established.

In the main loop of the program the temperature measurements are carried out once every minute and published to the MQTT broker. At the same time an air flow direction estimate is done by averaging the difference between the two temperature sensors. If the difference is larger than 2*ºC* the airflow direction is concluded to be *outgoing*.

## Transmitting the data/connectivity
The two temperature sensors and the air flow estimator in the device sends their measurements to the Ubidots cloud for storage once every minute. Also the temperature difference and the averaged temperature difference is sent (which is used for air flow estimate in the Lopy4). 

All data is stored in in Ubidots database (given the limitations already described above). The PyCom device is connected to my home Wi-fi network and the data is sent using the MQTT protocol. Another way of saying that is that the PyCom device publishes data to the topic `/v1.6/devices/{MY_DEVICE}/{MEASUREMENT}`. 

In my case `MY_DEVICE = AirFlowMeter` and the 4 measurements are denoted `MEASUREMENT = {"Room_Temperature", "Air_Temperature", "T_delta", "T_deltaAvg"}`. The data uploaded is found with the same names in Ubidots:

![](https://i.imgur.com/QmQt6dE.png)*Screenshot from Ubidots showing the variables.*


The MQTT protocol includes a *Quality of Service (QoS)* parameter which sets the "amition level" when sending data. I used `QoS = 0` which means that the data is sent but my Lopy4 will not know if Ubidots received the data or not. This is the most efficient way to send data and since the data rate is "high" anyhow it should not be a problem if single data readings are lost sometimes.

## Presenting the data
The data is presented in two ways. The first one is that the PyCom device uses its LED with `Green` = "Outgoing airflow" and `Red` = "Incoming or uncertain airflow" to show the estimated airflow direction, *which was the objective of this project!* Please note that I have added some hysteresis (in software) so the LED can only change color every 10th minute.

The second presentation is done via Ubidots. Below is a screen dump that shows how temperature from the two sensors are presented. The idea was to use a syntetic variable to calculate the air flow direction estimate but  
that functionality was not included in the free version of Ubidots. Instead I found an *indicator* widget that will turn green when the air flow is outgoing and turn red when the air flow is incoming. 

![](https://i.imgur.com/YP7lBsg.png)*Ubidots dashboard with the published data*


## Finalizing the design
I am happy with this first prototype and I am looking forward to try it out more in the winter time. 

![](https://i.imgur.com/Yw7pVhC.jpg)*The resulting prototype with both the LED- and the Ubidots airflow direction indicator.*


Thinking of what could be done different/better, I come up with the following:

* During summer this idea of measuring the temperature difference will not work, since there is no temperature difference. However, I expect a significant temperature difference in the wintertime. The software in the Lopy4 is already tested and should work as expected!
* Add a notification to the user (e-mail, text message, ...) when the airflow changes direction.
* Extend the Python classes to include more sensor, including digital sensors. Maybe a humidity sensor could help making a better air flow direction estimate?
* Add more error handling (at least recover from lost Wi-Fi)
* Support individual measurement rates for each sensor
* Have a paid Ubidots account (or similar) that supports more cloud computing so that a better estimate of the air flow direction could be done in the cloud. 
