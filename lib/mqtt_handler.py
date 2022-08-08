import time
import logging
import paho.mqtt.publish as publish
import etc.config as config

# create logger
module_logger = logging.getLogger('fd_tone_notify_extension.mqtt')


def publish_to_mqtt(data):
    # Make sure data is not empty
    if data["mqtt_start_message"] and data["mqtt_topic"]:
        module_logger.info("Publishing to MQTT")
        # publish start message
        publish.single(topic=data["mqtt_topic"], payload=data["mqtt_start_message"],
                       hostname=config.mqtt_settings["mqtt_hostname"],
                       port=config.mqtt_settings["mqtt_port"], auth={'username': config.mqtt_settings["mqtt_username"],
                                                                     'password': config.mqtt_settings["mqtt_password"]})

        module_logger.debug("Start message published MQTT: " + data["mqtt_start_message"])
        # check for stop message
        if data["mqtt_stop_message"] and data["mqtt_message_interval"] and data["mqtt_message_interval"] > 0:
            # sleep for mqtt interval
            time.sleep(data["mqtt_message_interval"])
            # publish stop message
            publish.single(topic=data["mqtt_topic"], payload=data["mqtt_stop_message"],
                           hostname=config.mqtt_settings["mqtt_hostname"],
                           port=config.mqtt_settings["mqtt_port"],
                           auth={'username': config.mqtt_settings["mqtt_username"],
                                 'password': config.mqtt_settings["mqtt_password"]})
            module_logger.debug("Stop message published MQTT: " + data["mqtt_stop_message"])
        else:
            module_logger.debug("Stop message not configured skipping.")

    else:
        module_logger.critical("Must have start message and topic for MQTT configured")

