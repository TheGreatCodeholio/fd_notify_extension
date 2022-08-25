import json
import time
import datetime
from TwitterAPI import TwitterAPI
import logging
from lib.redis_handler import RedisCache
import etc.config as config

# create logger
module_logger = logging.getLogger('fd_tone_notify_extension.twitter')


def send_tweet(tone_name, tone_data, audio_link, audio_path):
    module_logger.info("Posting to Twitter")
    service = "twitter"
    tone_name = tone_name.replace("\"", "")
    now = datetime.datetime.now()
    RedisCache().add_call_to_redis(service, tone_name, tone_data, audio_link, audio_path)
    module_logger.debug("Waiting for additional tones from same call.")
    time.sleep(config.twitter_settings["call_wait_time"])
    calls_result = RedisCache().get_all_call(service)
    if calls_result:
        working_call = calls_result[tone_name.encode('utf-8')]
        if working_call:
            if len(calls_result) >= 2:
                message = "{}:{} {}\nDepartments:".format(now.strftime("%H"), now.strftime("%M"),
                                                          now.strftime("%b %d %Y"))
                for call in calls_result:
                    data = json.loads(str(calls_result[call].decode('utf-8')))
                    message += " " + str(data["call_tone_data"]["department_number"])
                RedisCache().delete_all_calls(service)
                message += "\n\n"
                message += "Dispatch Audio: " + str(audio_link)
                post_to_twitter(message)

            elif len(calls_result) == 1:
                RedisCache().delete_single_call(service, tone_name)
                message = "{}:{} {}\n{}\n\n".format(now.strftime("%H"), now.strftime("%M"), now.strftime("%b %d %Y"),
                                                    tone_name + tone_data["department_number"])
                message += "Dispatch Audio: " + str(audio_link) + "\n"
                post_to_twitter(message)

            return
    else:
        module_logger.debug(tone_name + " part of another call. Not Posting.")


def post_to_twitter(message):
    if config.twitter_settings["consumer_key"] and config.twitter_settings["consumer_secret"] and config.twitter_settings["access_token"] and config.twitter_settings["access_token_secret"]:
        api = TwitterAPI(config.twitter_settings["consumer_key"], config.twitter_settings["consumer_secret"],
                         config.twitter_settings["access_token"], config.twitter_settings["access_token_secret"])
        r = api.request('statuses/update', {'status': message})
        if r.status_code == 200:
            module_logger.debug("Tweet Successful")
        else:
            module_logger.critical("Tweet Failed: " + str(r.status_code) + " " + str(r.text))
    else:
        module_logger.critical("Missing consumer key/secret or access key/secret")


