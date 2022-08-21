# This script will generate a new default.json for fd_tone_notify from tones.cfg for TTD
import configparser
import json
import os.path
import shutil

import lib.icad_shell_menu as menu
from lib.util import Colors

import etc.config as config


def convert_ttd():
    if not os.path.exists(config.fd_tone_notify_extension_path + "tones.cfg"):
        print(
            Colors.FG.Red + Colors.Bold + "Can't find tones.cfg. Please place tones.cfg in: " + config.fd_tone_notify_extension_path + Colors.Reset)
        return

    parser = configparser.ConfigParser()
    parser.read(config.fd_tone_notify_extension_path + "tones.cfg")

    if not os.path.exists(config.fd_tone_notify_extension_path + 'var/config/default.json'):
        print(
            Colors.FG.Red + Colors.Bold + "Can't find default.json. Please place default fd-tone-notify config in: " + config.fd_tone_notify_extension_path + 'var/config/default.json' + Colors.Reset)
        return
    else:
        print(Colors.FG.Green + Colors.Bold + "Converting..." + Colors.Reset)
    fd_config = open(config.fd_tone_notify_extension_path + 'var/config/default.json')
    # returns JSON object as
    # a dictionary
    fd_data = json.load(fd_config)

    detectors = []

    for tone in parser.sections():
        new_detector = {
            "name": parser[tone]["description"],
            "tones": [float(parser[tone]["atone"]), float(parser[tone]["btone"])],
            "matchThreshold": 6,
            "tolerancePercent": 0.02,
            "notifications": {
                "preRecording": {
                    "pushbullet": [],
                    "webhooks": [],
                    "externalCommands": [
                        {
                            "command": "python3 " + config.fd_tone_notify_extension_path + "pre_record.py \"[detectorName]\" [custom]",
                            "description": "fd_extension",
                            "custom": {
                                "department_number": "",
                                "mqtt_topic": "dispatch/" + parser[tone]["description"].replace(" ", "_"),
                                "mqtt_start_message": "ON",
                                "mqtt_stop_message": "OFF",
                                "mqtt_message_interval": 5
                            }
                        }
                    ],
                    "emails": []
                },
                "postRecording": {
                    "pushbullet": [],
                    "webhooks": [],
                    "externalCommands": [
                        {
                            "command": "python3  " + config.fd_tone_notify_extension_path + "post_record.py [timestamp] \"[detectorName]\" [recordingRelPath] [custom]",
                            "description": "fd_extension",
                            "custom": {
                                "department_number": "",
                                "twilio_sms_numbers": [],
                                "pushover_group_token": "",
                                "pushover_app_token": "",
                                "mp3_append_file": ""
                            }
                        }
                    ],
                    "emails": []
                }
            }
        }
        detectors.append(new_detector)

    fd_data["detection"]["detectors"] = detectors
    with open('default.json', 'w+') as outfile:
        json.dump(fd_data, outfile, indent=4)
    outfile.close()
    print(
        Colors.FG.Green + Colors.Bold + "A new default.json has been created in: " + config.fd_tone_notify_extension_path + Colors.Reset)
    menu.main_menu()


def add_external_command():
    if not os.path.exists(config.fd_tone_notify_path + "config/default.json"):
        print(
            Colors.FG.Red + Colors.Bold + "Can't find default.json. Please add default.json to fd-tone-notify: " + config.fd_tone_notify_extension_path + Colors.Reset)
        return
    else:
        shutil.copy2(config.fd_tone_notify_path + "config/default.json",
                     config.fd_tone_notify_path + "config/default_backup.json")
        print(
            Colors.FG.Green + Colors.Bold + "Current default.json backed up to: " + config.fd_tone_notify_path + "config/default_backup.json" + Colors.Reset)

    fd_config = open(config.fd_tone_notify_path + "config/default.json")
    fd_data = json.load(fd_config)

    detectors = []

    for detector in fd_data["detection"]["detectors"]:
        detector_pre = [
            {
                "command": "python3 " + config.fd_tone_notify_extension_path + "pre_record.py \"[detectorName]\" [custom]",
                "description": "fd_extension",
                "custom": {
                    "department_number": "",
                    "mqtt_topic": "dispatch/" + detector["name"].replace(" ", "_"),
                    "mqtt_start_message": "ON",
                    "mqtt_stop_message": "OFF",
                    "mqtt_message_interval": 5
                }
            }
        ]
        detector_post = [
            {
                "command": "python3 " + config.fd_tone_notify_extension_path + "post_record.py [timestamp] \"[detectorName]\" [recordingRelPath] [custom]",
                "description": "fd_extension",
                "custom": {
                    "department_number": "",
                    "twilio_sms_numbers": [],
                    "pushover_group_token": "",
                    "pushover_app_token": "",
                    "mp3_append_file": ""
                }
            }
        ]
        detector["notifications"]["preRecording"]["externalCommands"] = detector_pre
        detector["notifications"]["postRecording"]["externalCommands"] = detector_post
        detectors.append(detector)

    fd_data["detection"]["detectors"] = detectors
    with open(config.fd_tone_notify_path + "config/default.json", 'w+') as outfile:
        json.dump(fd_data, outfile, indent=4)
    outfile.close()
    print(
        Colors.FG.Green + Colors.Bold + "default.json has been save in: " + config.fd_tone_notify_path + "config/default.json" + Colors.Reset)
    menu.main_menu()


def generate_mqtt_config():
    fd_config = open(config.fd_tone_notify_path + 'var/config/default.json')
    fd_data = json.load(fd_config)

    mqtt_client_config = open(config.fd_tone_notify_extension_path + 'etc/mqtt_client_config.json')
    mqtt_data = json.load(mqtt_client_config)

    mqtt_topics = []

    for detector in fd_data["detection"]["detectors"]:
        topic_tuple = ("dispatch/" + detector["name"].replace(" ", "_"), 0)
        mqtt_topics.append(topic_tuple)

    mqtt_data["topics"] = mqtt_topics

    with open(config.fd_tone_notify_extension_path + 'etc/mqtt_client_config.json', 'w+') as outfile:
        json.dump(mqtt_data, outfile, indent=4)
    outfile.close()
    print(
        Colors.FG.Green + Colors.Bold + "MQTT Client Config Saved" + Colors.Reset)

    menu.main_menu()