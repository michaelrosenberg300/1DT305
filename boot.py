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
