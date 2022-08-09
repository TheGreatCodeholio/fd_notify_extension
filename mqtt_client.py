#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright (c) 2010-2013 Roger Light <roger@atchoo.org>
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Distribution License v1.0
# which accompanies this distribution.
#
# The Eclipse Distribution License is available at
#   http://www.eclipse.org/org/documents/edl-v10.php.
#
# Contributors:
#    Roger Light - initial implementation
# Copyright (c) 2010,2011 Roger Light <roger@atchoo.org>
# All rights reserved.

# This shows a simple example of an MQTT subscriber.
import sys

import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import json
import time
import etc.config as config
from threading import Thread

relay_pin = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(relay_pin, GPIO.OUT)
flash = False
switch = True


def on_connect(mqttc, obj, flags, rc):
    print("rc: " + str(rc))


def on_message(mqttc, obj, msg):
    message = msg.payload.decode()
    Thread(target=flash_loop, args=(message,)).start()


def on_publish(mqttc, obj, mid):
    print("mid: " + str(mid))


def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mqttc, obj, level, string):
    print(string)


def flash_loop(message):
    global switch
    global flash
    if message.lower() == "on":
        if not flash:
            flash = True
            switch = False
            GPIO.output(relay_pin, GPIO.HIGH)
            while not switch:
                time.sleep(.5)
            GPIO.output(relay_pin, GPIO.LOW)
            print("Flash Stopped")
        else:
            print("In Use")
            return
    elif message.lower() == "off":
        if flash:
            flash = False
        if not switch:
            switch = True

# If you want to use a specific client id, use
# mqttc = mqtt.Client("client-id")
# but note that the client id must be unique on the broker. Leaving the client
# id parameter empty will generate a random id for you.
GPIO.output(relay_pin, GPIO.LOW)
mqttc = mqtt.Client()
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
# Uncomment to enable debug messages
# mqttc.on_log = on_log
mqtt_client_config = open(config.fd_tone_notify_extension_path + 'etc/mqtt_client_config.json')
mqtt_data = json.load(mqtt_client_config)

topics = mqtt_data["topics"]
if len(topics) <= 0:
    print("No Topics Found Exiting")
    GPIO.cleanup()
    sys.exit(1)

mqttc.username_pw_set(config.mqtt_settings["mqtt_username"], config.mqtt_settings["mqtt_password"])
mqttc.connect(config.mqtt_settings["mqtt_hostname"], config.mqtt_settings["mqtt_port"], 60)
mqttc.subscribe(topics)
try:
    mqttc.loop_forever()
except KeyboardInterrupt as e:
    print("Exiting")
    GPIO.cleanup()
    sys.exit(0)
except Exception as e:
    print("Exiting: ")
    GPIO.cleanup()
    sys.exit(1)
