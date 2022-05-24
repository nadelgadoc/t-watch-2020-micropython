import uos
import utime
import usys
import ntptime
import lvgl as lv
import numclock
from machine import Pin, SoftI2C
from machine import Timer
import pcf8563

numericalClock = numclock.numClock(lv.scr_act(),timezone=-3)

i2c1 = SoftI2C(scl=Pin(22), sda=Pin(21))
rtc = pcf8563.PCF8563(i2c1)
datetime = rtc.datetime()

_network = None
if 'net' in locals():
    _network = locals()['net']

def correct_time(dt=None):
    if _network.isconnected():
        try:
            ntptime.settime()
            rtc.set_datetime(utime.gmtime())
        except Exception as e:
            print('Exception handled on loop\n'+str(e))
            usys.print_exception(e)

_time_check = Timer(1)
_time_check.init(period=30000, mode=Timer.PERIODIC, callback=correct_time)

# while True:
#     if 'net' in locals():
#         if locals('net').isConnected():
#             pass