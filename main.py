#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2019 Deliang Wang
# See LICENSE.rst for details.

from time import sleep,monotonic
import datetime
from sensors import AM2301,WZ_S,MY_GPS
from display import WS_RGB_OLED
from thing_alink import aliyun_iot


def main():
	last_print = monotonic()
	myWZ_S = WZ_S("/dev/ttyUSB0",9600)
	myWZ_S.getConnected()
	myWZ_S.changeMode()
	myAM2301 = AM2301(22)
	myOLED = WS_RGB_OLED()
	myGPS = MY_GPS('/dev/ttyUSB1')
	myGPS.gps.send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
	#myGPS.gps.send_command(b'PMTK314,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0')
	sleep(0.2)
	myGPS.gps.send_command(b'PMTK220,1000')
	sleep(0.2)

	myIoT = aliyun_iot()
	client = myIoT.getAliyunIoTClient()
	client.connect_async(host = myIoT.host, port = myIoT.port, keepalive = 60)
	client.loop_start()
	client.subscribe(topic = myIoT.sub_topic_propset)

	while True:
		current = monotonic()
		now = datetime.datetime.now()
		humidity, temperature = myAM2301.read()
		hcho = round(myWZ_S.getValue(),3)
		myOLED.draw_test(2,2,hcho,round(humidity,1),round(temperature),"white")

		while True:
			myGPS.gps.update()
			if myGPS.check_gps_info_valid():
				latitude = myGPS.gps.latitude
				longtitude = myGPS.gps.longitude
				satellites = myGPS.gps.satellites
				altitude = myGPS.gps.altitude_m
				speed = myGPS.gps.speed_knots
				height_geoid = myGPS.gps.height_geoid
				#print("[ OK ] \t lat: %.6f \t lon: %.6f \t sat: %d, alt: %.3f \t spd: %.3f \t heig_geoid: %.3f" %(latitude, longtitude, satellites, altitude, speed, height_geoid))
				break

		if humidity is not None and temperature is not None and hcho is not None:
			if current - last_print >= 10.0:
				last_print = current
				payload = myIoT.build_prop_json_payload(temperature, humidity, hcho, longtitude, latitude, altitude)
				client.publish(topic = myIoT.pub_topic, payload = str(payload), qos = 1)
				print("[ OK ]\t heartbeat: %d \t hum: %f \t temp: %f \t hcho:%f \t lat: %f \t lon: %f \t alt: %f" % (myIoT.heartbeat,humidity,temperature,hcho,myGPS.gps.latitude,myGPS.gps.longitude,100.9))
		sleep(1)	

if __name__ == "__main__":
    try:
    	main()
    except KeyboardInterrupt:
    	pass