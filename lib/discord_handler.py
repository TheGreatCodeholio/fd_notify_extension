import json
import time
import requests
import logging
from lib.redis_handler import RedisCache
import etc.config as config

# create logger
module_logger = logging.getLogger('fd_tone_notify_extension.discord')


def send_audio_text(timestamp, tone_name, tone_data, audio_link, audio_path):
    module_logger.info("Sending To Discord Server")
    tone_name = tone_name.replace("\"", "")
    service = "discord"

    RedisCache().add_call_to_redis(service, tone_name, tone_data, audio_link, audio_path)
    module_logger.debug("Waiting for additional tones from same call.")
    time.sleep(config.discord_settings["call_wait_time"])
    calls_result = RedisCache().get_all_call(service)
    if calls_result:
        working_call = calls_result[tone_name.encode('utf-8')]
        if working_call:
            if len(calls_result) >= 2:
                # build our json data for discord bot api
                detectors = {}

                call_data = {"timestamp": timestamp, "mp3_url": audio_link, "call_mp3_path": audio_path,
                             "detector_name": "multi", "detectors": detectors}

                for call in calls_result:
                    data = json.loads(str(calls_result[call].decode('utf-8')))
                    detectors[data["call_tone_name"]] = data["call_department_number"]

                RedisCache().delete_all_calls(service)

            else:
                RedisCache().delete_single_call(service, tone_name)
                call_data = {"timestamp": timestamp, "mp3_url": audio_link, "call_mp3_path": audio_path,
                             "detector_name": tone_name + " " + tone_data["department_number"]}

            if config.discord_settings["text"] == 1:
                module_logger.info("Sending Text Request To Discord Server")
                r = requests.post(config.discord_settings["client_url"] + "/text", json=call_data)
                if r.status_code == 200:
                    module_logger.debug("Discord Client Accepted Text Post")
                else:
                    module_logger.debug("Discord Client Text Post Error: " + str(r.status_code))

            if config.discord_settings["voice"] == 1:
                module_logger.info("Sending Voice Request To Discord Server")
                r = requests.post(config.discord_settings["client_url"] + "/voice", json=call_data)
                if r.status_code == 200:
                    module_logger.debug("Discord Client Accepted Voice Post")
                else:
                    module_logger.debug("Discord Client Voice Post Error: " + str(r.status_code))

            return
    else:
        module_logger.debug(tone_name + " part of another call. Not Posting.")
