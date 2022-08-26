import json
import time
import datetime
import requests
import logging
from lib.redis_handler import RedisCache
import etc.config as config

# create logger
module_logger = logging.getLogger('fd_tone_notify_extension.facebook')


def send_post(timestamp, tone_name, tone_data, audio_link, audio_path):
    module_logger.info("Posting to Facebook Page")
    tone_name = tone_name.replace("\"", "")
    service = "facebook"
    timestamp = datetime.datetime.fromtimestamp(timestamp)
    RedisCache().add_call_to_redis(service, tone_name, tone_data, audio_link, audio_path)
    module_logger.debug("Waiting for additional tones from same call.")
    time.sleep(config.facebook_page_settings["call_wait_time"])
    calls_result = RedisCache().get_all_call(service)
    if calls_result:
        working_call = calls_result[tone_name.encode('utf-8')]
        if working_call:
            if len(calls_result) >= 2:
                message = "{}:{} {}\nDepartments: ".format(timestamp.strftime("%H"), timestamp.strftime("%M"),
                                                          timestamp.strftime("%b %d %Y"))
                for call in calls_result:
                    data = json.loads(str(calls_result[call].decode('utf-8')))
                    message += str(data["call_tone_name"] + " " + data["call_department_number"] + "\n")
                RedisCache().delete_all_calls(service)
                message += "\n\n"
                message += "Dispatch Audio: " + str(audio_link)
                facebook_pages = config.facebook_page_settings["facebook_page_ids"]
                for page in facebook_pages:
                    connect_and_post_page(message, page)

            else:
                RedisCache().delete_single_call(service, tone_name)
                message = "{}:{} {}\n{}\n\n".format(timestamp.strftime("%H"), timestamp.strftime("%M"),
                                                    timestamp.strftime("%b %d %Y"),
                                                    tone_name + " " + tone_data["department_number"])
                message += "Dispatch Audio: " + str(audio_link) + "\n"
                facebook_pages = config.facebook_page_settings["facebook_page_ids"]
                for page in facebook_pages:
                    connect_and_post_page(message, page)

            return
    else:
        module_logger.debug(tone_name + " part of another call. Not Posting.")


def connect_and_post_page(message, page_id):
    if config.facebook_page_settings["facebook_app_token_page"]:
        post_url = f"https://graph.facebook.com/v14.0/{page_id}/feed"
        payload = {
            'message': message,
            'access_token': config.facebook_page_settings["facebook_app_token_page"]
        }
        r = requests.post(post_url, data=payload)
        if r.status_code == 200:
            module_logger.debug("Page Post Successful: " + str(page_id))
        else:
            module_logger.critical("Page Post Failed: " + str(page_id) + " " + str(r.status_code) + " " + r.text)

    else:
        module_logger.critical("No Page ID given or app token is empty!")
