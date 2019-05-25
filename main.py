#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2019 Deliang Wang
# See LICENSE.rst for details.

import configparser
import os.path
import logging
import logging.handlers
from time import sleep,monotonic
import datetime
from sensors import AM2301,WZ_S,MY_GPS
from display import WS_RGB_OLED
from thing_alink import aliyun_iot


def main():
	# configure the logger 
	logger = logging.getLogger('logger')
	logger.setLevel(level = logging.DEBUG)
	rf_handler = logging.handlers.TimedRotatingFileHandler('all.log', when = 'midnight', interval = 1, backupCount = 7, atTime = datetime.time(0,0,0,0))
	rf_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
	c_handler = logging.StreamHandler()
	c_handler.setLevel(logging.DEBUG)
	c_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
	f_handler = logging.FileHandler('error.log')
	f_handler.setLevel(logging.ERROR)
	f_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s[:%(lineno)d] - %(message)s"))
	logger.addHandler(rf_handler)
	logger.addHandler(f_handler)
	logger.addHandler((c_handler))
	logger.info('Home Condition Monitoring Sensor StartUp...')
	logger.info('logger configuration done')

	# read configuration
	config = configparser.ConfigParser()
	cfg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'default.cfg'))
	config.read(cfg_path)
	logger.info('configuration file loaded successfully')

	last_print = monotonic()

	# initilize wz-s sensor: port ttyUSB0,9600
	logger.info('wz-s sensor initilizing...')
	myWZ_S = WZ_S(config.get('dart_wzs','serial_port'), baud_rate = int(config.get('dart_wzs','baudrate')))
	myWZ_S.getConnected()
	myWZ_S.changeMode()
	logger.info('wz-s sensor initializing: change mode to REQ-RES done')
	logger.info('wz-s sensor building done')

	# initialize the 1-wire Temperature & Humility sensor am2301
	myAM2301 = AM2301(int(config['am2301']['gpio_bcm']))
	logger.info('AM2301 sensor initializing done')
	
	myOLED = WS_RGB_OLED()
	
	#initialize the gps module: ttyUSB1, 9600
	myGPS = MY_GPS(config['gps']['serial_port'])
	myGPS.gps_config()
	logger.info('GPS module initializing done')

	logger.info('Connecting to AliCloud...')
	myIoT = aliyun_iot()
	client = myIoT.getAliyunIoTClient()
	client.connect_async(host = myIoT.host, port = int(config['alicloud']['port']), keepalive = int(config['alicloud']['keepalive']))
	client.loop_start()
	client.subscribe(topic = myIoT.sub_topic_propset)
	logger.info('Connecting to AliCloud successfully')

	while True:
		current = monotonic()
		now = datetime.datetime.now()
		humidity, temperature = myAM2301.read()
		hcho = round(myWZ_S.getValue(),3)
		myOLED.draw_test(2,2,hcho,round(humidity,1),round(temperature),"white")

		while True:
			try:
				myGPS.gps.update()
			except ValueError:
				logger.error(ValueError)	

			if myGPS.check_gps_info_valid():
				latitude = myGPS.gps.latitude
				longtitude = myGPS.gps.longitude
				satellites = myGPS.gps.satellites
				altitude = myGPS.gps.altitude_m
				speed = myGPS.gps.speed_knots
				height_geoid = myGPS.gps.height_geoid
				logger.debug('Sensor Values: lat: %.6f | lon: %.6f | sat: %d | alt: %.3f | spd: %.3f | heig_geoid: %.3f' ,latitude, longtitude, satellites, altitude, speed, height_geoid)

				break

		if humidity is not None and temperature is not None and hcho is not None:
			if current - last_print >= 10.0:
				last_print = current
				payload = myIoT.build_prop_json_payload(int(temperature), int(humidity), hcho, longtitude, latitude, altitude)
				client.publish(topic = myIoT.pub_topic, payload = str(payload), qos = 1)
				logger.debug('Msg Published: heartbeat: %d | hum: %.2f | temp: %.2f | hcho:%.4f | lat: %f | lon: %f | alt: %f', myIoT.heartbeat, humidity, temperature, hcho, myGPS.gps.latitude, myGPS.gps.longitude, myGPS.gps.altitude_m)
				#print("[ OK ]\t heartbeat: %d \t hum: %f \t temp: %f \t hcho:%f \t lat: %f \t lon: %f \t alt: %f" % (myIoT.heartbeat,humidity,temperature,hcho,myGPS.gps.latitude,myGPS.gps.longitude,myGPS.gps.altitude_m))
		sleep(1)	

if __name__ == "__main__":
    try:
    	main()
    except KeyboardInterrupt:
    	logger.info('Keyboard interrupted by User')
    except ValueError:
    	logger.error(ValueError)
    except UnboundLocalError:
    	pass