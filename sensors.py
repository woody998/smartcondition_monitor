#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2019 Deliang Wang
# See LICENSE.rst for details.

import Adafruit_DHT
import adafruit_gps
from time import sleep
import serial

class AM2301:
	def __init__(self,gpio_pin_bcm):
		self.gpio_pin_bcm = gpio_pin_bcm
		self.sensor=Adafruit_DHT.AM2302

	def read(self):
		humidity, temperature = Adafruit_DHT.read_retry(self.sensor, self.gpio_pin_bcm)
		return humidity,temperature


class WZ_S:
	def __init__(self, port, baud_rate = 9600, mode = 'REQ_RESP', debug_output = False):
		self.port = port
		self.baud_rate = baud_rate
		self.mode = mode
		self.debug_output = debug_output
		self.isOpen = False

	def getConnected(self):
		self.ser = serial.Serial(
			port = self.port,
			baudrate = self.baud_rate,
			# for some reason, below 3 args do not work
			#bytesize = EIGHTBITS,  
            #parity = PARITY_NONE,
            #stopbits = STOPBITS_ONE,
            timeout = 0.2,
            xonxoff = False,
            rtscts = False,
            dsrdtr = False,
            write_timeout = 0.5,
            inter_byte_timeout = None)
		if self.ser.isOpen==0:
			self.ser.open()
			self.isOpen = self.ser.isOpen
			if self.debug_output:
				print('[OK]\t the port - %s  open sucessfully' %self.port)
		else:
			if self.debug_output:
				print('[OK]\t the port - %s  is already open' %self.port)

	def changeMode(self):
		if self.ser.isOpen:
			self.ser.write(b'\xFF\x01\x78\x41\x00\x00\x00\x00\x46')
			sleep(0.1)
			self.ser.reset_input_buffer()
			if self.debug_output:
				print('[OK]\t Mode changed to Request-Respond')
		else:
			print("[nOK]\t port is not open, pls check!")

	def getValue(self):
		self.ser.write(b'\xFF\x01\x86\x00\x00\x00\x00\x00\x79')
		sleep(0.1)
		if (self.ser.inWaiting() == 9):
			result = self.ser.read(9)
			if self.debug_output:
				print("[OK]\t Raw data: %s" %result)
			valueHigh = int(hex(result[6]), 16)
			valueLow = int(hex(result[7]), 16)
			self.value = float(valueHigh * 256 + valueLow)/1000
			if self.debug_output:
				print("[OK]\t HCHO[ppm] is %f" %self.value)
			return self.value
		else:
			print("[nOK] data length error")
			self.ser.reset_input_buffer()

	def __del__(self):
		if self.ser.isOpen:
			self.ser.close()
			sleep(0.1)
			self.isOpen = False
		if self.debug_output:
			print("[OK] \t WZ-S module is destroyed")
		self.debug_output = False



class MY_GPS(object):
	"""docstring for MY_GPS"""
	def __init__(self, port, baudrate = 9600, timeout = 30):
		super(MY_GPS, self).__init__()
		self.baudrate = baudrate
		self.timeout = timeout
		self.port = port
		self.isconfigured = False

		self.uart = serial.Serial(
			port = self.port,
			baudrate = self.baudrate,
			# for some reason, below 3 args do not work
			#bytesize = EIGHTBITS,  
            #parity = PARITY_NONE,
            #stopbits = STOPBITS_ONE,
            timeout = 3,
            xonxoff = False,
            rtscts = False,
            dsrdtr = False,
            write_timeout = 0.5,
            inter_byte_timeout = None)		

		self.gps = adafruit_gps.GPS(self.uart, debug = False)

	def check_gps_info_valid(self):
		if self.gps.has_fix and \
			self.gps.latitude is not None and self.gps.latitude is not None and self.gps.longitude is not None and \
			self.gps.satellites is not None and self.gps.altitude_m is not None and \
			self.gps.speed_knots is not None and self.gps.height_geoid is not None:
			return True
		else:
			return False

	def gps_config(self):
		self.gps.send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
		sleep(0.2)
		self.gps.send_command(b'PMTK220,1000')
		sleep(0.2)
		self.isconfigured = True


