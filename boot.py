# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import network
import uos
import config
import sys
import ubinascii
from machine import unique_id

def df():
	bits = uos.statvfs('/')
	freesize = bits[0] * bits[3]
	mbfree = freesize / (1024 * 1024)
	print('Free memory: ' + str(mbfree) + 'MB')

config_handler = config.local()
t_ssid, t_pass = config_handler.getSettings([ 'ssid', 'password' ])
net = network.WLAN(network.STA_IF)
net.active(True)
mac = ubinascii.hexlify(unique_id()).upper().decode('utf-8')
net.config(dhcp_hostname='ESP-WATCH-' + mac[len(mac)-4:])
#net.config(dhcp_hostname='BEER-IOT')
try:
	print('Scanning available networks')
	netlist = net.scan()
	print(netlist)
	try_to_connect = False
	for t_net in netlist:
		if t_ssid.encode() in t_net:
			try_to_connect = True
	if try_to_connect:
		print('Attempting connection to \'' + str(t_ssid) + '\' with password \'' + str(t_pass) + '\'')
		net.connect(t_ssid, t_pass)
	else:
		print('Not Found')
		raise Exception('SSID not found')
except KeyboardInterrupt:
	print('Keyboard Interrupt detected**********')
	sys.exit()
	# utime.sleep(2)
except Exception as e:
	print('****Exception: ' + str(e))
	print('Failed\n')
	# net.active(False)
	# utime.sleep(0.5)

# while net.isconnected() == False:
# 	utime.sleep(0.2)
# print('*****Connected******')


#webrepl.start()
#ntptime.settime()