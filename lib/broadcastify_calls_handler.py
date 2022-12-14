import os
import logging
import time
import datetime

import urllib3
from pydub import AudioSegment
import etc.config as config

# create logger
from lib.redis_handler import RedisCache

module_logger = logging.getLogger('fd_tone_notify_extension.broadcastify_calls')


# post_call(int(time.time()), "test.wav") example request
# process steps
# load wav file - convert to m4a 32k with 22050 bitrate
# load mp4 get length
# send upload request
# get back url
# read m4a file as data
# put m4a file to the url

def queue_call(timestamp, tone_name, tone_data, audio_link, audio_path_wav):
    module_logger.info("Queueing For Broadcastify Calls")
    tone_name = tone_name.replace("\"", "")
    service = "bcfy"
    timestamp = datetime.datetime.fromtimestamp(timestamp)
    RedisCache().add_call_to_redis(service, tone_name, tone_data, audio_link, audio_path_wav)
    module_logger.debug("Waiting for additional tones from same call.")
    time.sleep(config.facebook_page_settings["call_wait_time"])
    calls_result = RedisCache().get_all_call(service)
    if calls_result:
        working_call = calls_result[tone_name.encode('utf-8')]
        if working_call:
            if len(calls_result) >= 2:
                RedisCache().delete_all_calls(service)
                post_call(timestamp, audio_path_wav)

            else:
                RedisCache().delete_single_call(service, tone_name)
                post_call(timestamp, audio_path_wav)

            return
    else:
        module_logger.debug(tone_name + " part of another call. Not Posting.")


def post_call(timestamp, wav_file_path):
    module_logger.info("Uploading to Broadcastify Calls")

    wav_audio = AudioSegment.from_file(wav_file_path)
    wav_audio.export(wav_file_path.replace(".wav", ".m4a"), format="mp4",
                     parameters=["-af", "aresample=resampler=soxr", "-ar", "22050", "-c:a", "aac", "-b:a", "32k",
                                 "-cutoff", "18000"])

    mp4_path = wav_file_path.replace(".wav", ".m4a")
    mp4_audio = AudioSegment.from_file(mp4_path)
    call_duration = int(round(mp4_audio.duration_seconds, 2))

    broadcastify_url = "https://api.broadcastify.com/call-upload"
    module_logger.info("Requesting Call Upload Url")
    http = urllib3.PoolManager()
    r = http.request(
        'POST',
        broadcastify_url,
        fields={'apiKey': config.broadcastify_calls_settings["calls_api_key"],
                'systemId': config.broadcastify_calls_settings["calls_system_id"], 'callDuration': str(call_duration),
                'ts': str(int(timestamp)), 'tg': config.broadcastify_calls_settings["calls_slot"],
                'freq': config.broadcastify_calls_settings["calls_frequency"],
                'enc': 'm4a'})

    if r.status != 200:
        module_logger.critical("Request for Call Upload Url Failed: " + str(r.status))
    else:
        module_logger.info("Uploading Call Audio")
        response = r.data.decode('utf-8').split(' ')
        upload_url = response[1]
        with open(wav_file_path.replace(".wav", ".m4a"), 'rb') as up_file:
            file_data = up_file.read()
        r = http.request('PUT', upload_url, headers={'Content-Type': 'audio/aac'}, body=file_data)
        if r.status != 200:

            module_logger.critical("Upload Call Audio Failed: " + str(r.status))
        else:

            module_logger.info("Upload Call Audio Complete")
        module_logger.debug("Cleaning Call Files")
        os.remove(wav_file_path.replace(".wav", ".m4a"))
