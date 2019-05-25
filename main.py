#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2019 Deliang Wang
# See LICENSE.rst for details.

import configparser
import os.path
from time import sleep,monotonic
import datetime
from sensors import AM2301,WZ_S,MY_GPS
from display import WS_RGB_OLED
from thing_alink import aliyun_iot


def main():
	last_print = monotonic()
	config = configparser.ConfigParser()
	cfg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'default.cfg'))
	config.read(cfg_path)
	myWZ_S = WZ_S(config.get('dart_wzs','serial_port'), baud_rate = int(config.get('dart_wzs','baudrate')))
	myWZ_S.getConnected()
	myWZ_S.changeMode()
	myAM2301 = AM2301(int(config['am2301']['gpio_bcm']))
	myOLED = WS_RGB_OLED()
	myGPS = MY_GPS(config['gps']['serial_port'])
	myGPS.gps_config()

	myIoT = aliyun_iot()
	client = myIoT.getAliyunIoTClient()
	client.connect_async(host = myIoT.host, port = int(config['alicloud']['port']), keepalive = int(config['alicloud']['keepalive']))
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
				print("[ OK ] \t lat: %.6f \t lon: %.6f \t sat: %d, alt: %.3f \t spd: %.3f \t heig_geoid: %.3f" %(latitude, longtitude, satellites, altitude, speed, height_geoid))
				break

		if humidity is not None and temperature is not None and hcho is not None:
			if current - last_print >= 10.0:
				last_print = current
				payload = myIoT.build_prop_json_payload(int(temperature), int(humidity), hcho, longtitude, latitude, altitude)
				client.publish(topic = myIoT.pub_topic, payload = str(payload), qos = 1)
				print("[ OK ]\t heartbeat: %d \t hum: %f \t temp: %f \t hcho:%f \t lat: %f \t lon: %f \t alt: %f" % (myIoT.heartbeat,humidity,temperature,hcho,myGPS.gps.latitude,myGPS.gps.longitude,myGPS.gps.altitude_m))
		sleep(1)	

if __name__ == "__main__":
    try:
    	main()
    except KeyboardInterrupt:
    	pass