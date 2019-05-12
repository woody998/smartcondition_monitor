#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2019 Deliang Wang
# See LICENSE.rst for details.

import sys
import os.path
import time
import datetime
from luma.core import interface
from luma.oled.device import ssd1331
from luma.core.render import canvas
from luma.core.virtual import terminal
from PIL import Image
from PIL import ImageFont
from luma.core.sprite_system import framerate_regulator


labels = [
	("HCHO[ppm]",12), ("Temperature",12),("Humility",12)
]

class WS_RGB_OLED:
	def __init__(self, rotate = 0, debug_output = False):
		self.padding = 2
		self.top = self.padding
		self.bottom = 64-self.padding-1
		self.rotate = rotate
		self.debug_output = debug_output
		self.ser = interface.serial.spi(port = 0, device = 0)
		self.device = ssd1331(serial_interface = self.ser, width = 96, height = 64, rotate = self.rotate)
		self.device.contrast(150)
		if debug_output == True:
			print("[OK]\t waveshare 0.96\" oled initilizaed successully" )

	def set_contrast(self,level = 0.8):
		self.device.contrast(level*255)

	def make_font(self, font, size):
		font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'fonts', font))
		return ImageFont.truetype(font_path, size)

	def get_time(self):
		now = datetime.datetime.now()
		today_time = now.strftime("%H:%M:%S")
		return today_time
	
	def get_date(self):
		now = datetime.datetime.now()
		today_date = now.strftime("%d %b %y")
		return today_date


	def draw_test(self,x, y, val_HCHO, val_humidity, val_temperature, color):
		with canvas(self.device) as draw:
			font = self.make_font("ProggyTiny.ttf", 12)
			size = draw.textsize('HCHO[ppm]',font)
			x = self.padding
			y = self.top
			draw.text((x, y),'HCHO[ppm]', font = font, fill = color)
			y+= size[1]
			font = self.make_font("ProggyTiny.ttf", 18)
			size = draw.textsize('HCHO[ppm]',font)
			draw.text((x, y), str(val_HCHO), font = font, fill = "yellow")
			y+= size[1]
			draw.line((self.padding, y, self.padding+94, y), fill = color, width = 0)

			font = self.make_font("ProggyTiny.ttf", 12)
			draw.text((x, y+2),'Temp', font = font, fill = color)	
			draw.text((54, y+2),'Humility', font = font, fill = color)				
			font = self.make_font("ProggyTiny.ttf", 18)	
			draw.text((x, y+2+8), str(val_temperature)[:4]+'°C', font = font, fill = "yellow")	
			draw.text((54, y+2+8), str(val_humidity)[:4]+'%', font = font, fill = "yellow")	
			draw.line((self.padding, y+2+8+12, self.padding+94, y+2+8+12), fill = color, width = 0)	

			font = self.make_font("ProggyTiny.ttf", 16)				
			draw.text((self.padding, y+2+8+12+2),"MENU", font = font, fill = "white")			
			font = self.make_font("ProggyTiny.ttf", 12)	
			draw.text((32, y+2+8+12+2),self.get_time(), font = font, fill = "white")	