# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import time
import hashlib
import hmac
import random
import json
import secrets
import logging

class aliyun_iot(object):
  """docstring for aliyun_iot"""
  def __init__(self,debug = 0):
    self.host = secrets.options['productKey'] + '.iot-as-mqtt.'+secrets.options['regionId']+'.aliyuncs.com'
    self.port = 1883
    self.pub_topic = "/sys/" + secrets.options['productKey'] + "/" + secrets.options['deviceName'] + "/thing/event/property/post";
    self.heartbeat = 0
    self.debug_info = debug
    self.sub_topic_propset = "/sys/" + secrets.options['productKey'] + "/" + secrets.options['deviceName'] + "/thing/service/property/set"
      
  # The callback for when the client receives a CONNACK response from the server.
  def on_connect(self,client, userdata, flags, rc):
      if self.debug_info == 1:
        print("On connect: \t Connected with result code "+str(rc))
      self.heartbeat = 0
      
      # client.subscribe("the/topic")

  def on_disconnect(self,client, userdata, rc):
      if self.debug_info == 1:
        print("on disconnect:\t disconnected with result code "+str(rc))

  # The callback for when a PUBLISH message is received from the server.
  def on_message(self,client, userdata, msg):
      if msg.topic == self.sub_topic_propset:
        json_set = json.loads(msg.payload)
        if json_set['params']['debug_info_onoff'] is not None:
          self.debug_info = json_set['params']['debug_info_onoff']          

      if msg.topic == self.sub_topic_propset:
        json_set = json.loads(msg.payload)
        self.debug_info = json_set['params']['debug_info_onoff']



      if self.debug_info == 1:
        print("Received message '" + str(msg.payload) + "' on topic '"+ msg.topic + "' with QoS " + str(msg.qos))      
  def on_publish(self, client, userdata, mid):
      if self.debug_info == 1:    
        print("on publish:\t" + str(mid))
      self.heartbeat = int(mid)

  def on_subscribe(client, userdata, mid):
      print("subscribe: " + str(mid))

  def hmacsha1(self,key,msg):
      return hmac.new(key.encode(), msg.encode(), hashlib.sha1).hexdigest()

  def on_log(self, client, userdata, level, buf):
      print(level +' '+ buf)

  def getAliyunIoTClient(self):
    timestamp = str(int(time.time()))
    self.watchdog = 0
    CLIENT_ID = "paho.py|securemode=3,signmethod=hmacsha1,timestamp="+timestamp+"|"
    CONTENT_STR_FORMAT = "clientIdpaho.pydeviceName"+secrets.options['deviceName']+"productKey"+secrets.options['productKey']+"timestamp"+timestamp
    # set username/password.
    USER_NAME = secrets.options['deviceName']+"&"+secrets.options['productKey']
    PWD = self.hmacsha1(secrets.options['deviceSecret'],CONTENT_STR_FORMAT)
    client = mqtt.Client(client_id=CLIENT_ID, clean_session=False)
    client.username_pw_set(USER_NAME, PWD)
    client.on_connect = self.on_connect
    client.on_message = self.on_message
    client.on_subscribe = self.on_subscribe   
    client.on_publish = self.on_publish   
    client.on_disconnect = self.on_disconnect
    return client

  def build_prop_json_payload(self,temp,humility,hcho,longtitude,latitude,altitude):
    payload_json = {
      'id': int(time.time()),
      'params': {
        'mtemp': temp,
        'mhumi': humility,
        'HCHO' : hcho,
        'GeoLocation': {
          'Longitude': longtitude,
          'Latitude': latitude,
          'Altitude': altitude,
          'CoordinateSystem': 1
        }
      },
        'method': "thing.event.property.post"
    }
    return payload_json