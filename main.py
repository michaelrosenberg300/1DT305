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

# Setup the alarm needed to handle the Limited
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
