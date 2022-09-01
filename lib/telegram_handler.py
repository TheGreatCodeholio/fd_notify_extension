import json
import time
import datetime
import requests
import logging
from lib.redis_handler import RedisCache
import etc.config as config

# create logger
module_logger = logging.getLogger('fd_tone_notify_extension.telegram')


def post_to_telegram(timestamp, tone_name, tone_data, audio_link, audio_path):
    module_logger.info("Posting to Facebook Page")
    tone_name = tone_name.replace("\"", "")
    service = "telegram"
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

                telegram_channels = config.telegram_settings["telegram_channel_ids"]
                for channel in telegram_channels:
                    connect_and_post_text(message, channel)
                    connect_and_post_audio(audio_path, channel)

            else:
                RedisCache().delete_single_call(service, tone_name)
                message = "{}:{} {}\n{}\n\n".format(timestamp.strftime("%H"), timestamp.strftime("%M"),
                                                    timestamp.strftime("%b %d %Y"),
                                                    tone_name + " " + tone_data["department_number"] + "\n")

                telegram_channels = config.telegram_settings["telegram_channel_ids"]
                for channel in telegram_channels:
                    connect_and_post_text(message, channel)
                    connect_and_post_audio(audio_path, channel)

            return
    else:
        module_logger.debug(tone_name + " part of another call. Not Posting.")


def connect_and_post_text(message, channel_id):
    payload = {
        'chat_id': channel_id,
        'text': message,
        'parse_mode': 'HTML'
    }

    resp = requests.post(
        f'https://api.telegram.org/bot{config.telegram_settings["telegram_bot_token"]}/sendMessage',
        data=payload).json()
    if resp["ok"]:
        module_logger.debug("Posted Text to Telegram Channel: " + str(channel_id))
    else:
        module_logger.critical("Telegram Text Post Failed: " + str(channel_id))


def connect_and_post_audio(audio_path, channel_id):
    with open(audio_path, 'rb') as audio:
        payload = {
            'chat_id': channel_id,
            'title': f'Dispatch Audio',
            'parse_mode': 'HTML'
        }
        files = {
            'audio': audio.read(),
        }
        resp = requests.post(
            f'https://api.telegram.org/bot{config.telegram_settings["telegram_bot_token"]}/sendAudio',
            data=payload,
            files=files).json()
        audio.close()
        if resp["ok"]:
            module_logger.debug("Posted Audio to Telegram Channel: " + str(channel_id))
        else:
            module_logger.critical("Telegram Audio Post Failed: " + str(channel_id))
