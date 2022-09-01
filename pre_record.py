__author__ = "Ian Carey"
__version__ = "0.1"
__license__ = "MIT"

import argparse
import logging
import json
import etc.config as config
import lib.mqtt_handler as mqtt

# create logger
logger = logging.getLogger('fd_tone_notify_extension')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler(config.fd_tone_notify_extension_path + 'var/log/fd_tone_notify_extension_pre.log')

if config.logger["debug"] == 1:
    fh.setLevel(logging.DEBUG)
else:
    fh.setLevel(logging.WARN)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)

parser = argparse.ArgumentParser(description='Process Arguments.')
parser.add_argument("tone_name", help="Tone Name.")
parser.add_argument("tone_data", help="Tone Data Info JSON String.")
args = parser.parse_args()
logger.info("Pre Record Script Start")

try:
    tone_data = json.loads(args.tone_data)
    if config.mqtt_settings["enabled"] == 1:
        logger.debug('Publishing to MQTT')
        mqtt.publish_to_mqtt(tone_data)
    else:
        logger.debug('Not Sending To MQTT.')

    logger.info("Pre Record Script Complete")
except Exception as e:
    logger.error(e)

