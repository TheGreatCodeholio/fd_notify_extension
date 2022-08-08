import os
import json
import logging
import urllib3
from pydub import AudioSegment
import etc.config as config

# create logger
module_logger = logging.getLogger('fd_tone_notify_extension.broadcastify_calls')


# post_call(int(time.time()), "test.wav") example request
# process steps
# load wav file - convert to m4a 32k with 22050 bitrate
# load mp4 get length
# create meta_data like Trunk Recorder - save meta data to json and read back
# send upload request
# get back url
# read m4a file as data
# put m4a file to the url


def post_call(timestamp, wav_file_path):
    module_logger.info("Uploading to Broadcastify Calls")
    wav_audio = AudioSegment.from_file(wav_file_path)
    wav_audio.export(wav_file_path.replace(".wav", ".m4a"), format="mp4",
                     parameters=["-af", "aresample=resampler=soxr", "-ar", "22050", "-c:a", "libfdk_aac", "-b:a", "32k",
                                 "-cutoff", "18000"])
    mp4_path = wav_file_path.replace(".wav", ".m4a")
    mp4_audio = AudioSegment.from_file(mp4_path)
    call_duration = round(mp4_audio.duration_seconds, 2)

    broadcastify_url = "https://api.broadcastify.com/call-upload"
    meta_data = {
        "freq": 154265000,
        "start_time": timestamp,
        "stop_time": timestamp - call_duration,
        "emergency": 0,
        "encrypted": 0,
        "call_length": 0,
        "talkgroup": int(config.broadcastify_calls_settings["calls_slot"]),
        "talkgroup_tag": "",
        "talkgroup_description": "",
        "talkgroup_group_tag": "",
        "talkgroup_group": "",
        "audio_type": "analog",
        "short_name": "calls",
        "freqList": [
            {"freq": 154265000, "time": timestamp, "pos": 0.00, "len": call_duration,
             "error_count": "0", "spike_count": "0"}],
        "srcList": [{"src": -1, "time": timestamp, "pos": 0.00, "emergency": 0, "signal_system": "", "tag": ""}]
    }
    with open(wav_file_path.replace(".wav", ".json"), "w+") as metadata:
        json.dump(meta_data, metadata)
    metadata.close()
    with open(wav_file_path.replace(".wav", ".json"), "r") as fp:
        file_data = fp.read()
    fp.close()
    metadata.close()
    module_logger.debug("Sending Request for Call Upload Url")
    http = urllib3.PoolManager()
    headers = urllib3.make_headers(user_agent='TrunkRecorder1.0')
    r = http.request(
        'POST',
        broadcastify_url,
        fields={'metadata': (wav_file_path.replace(".wav", ".json"), file_data, 'application/json'),
                'apiKey': config.broadcastify_calls_settings["calls_api_key"],
                'systemId': config.broadcastify_calls_settings["calls_system_id"], 'callDuration': str(call_duration),
                'ts': str(int(timestamp)), 'tg': config.broadcastify_calls_settings["calls_slot"],
                'freq': config.broadcastify_calls_settings["calls_frequency"],
                'enc': 'm4a'}, headers=headers)

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
        os.remove(wav_file_path.replace(".wav", ".json"))
        os.remove(wav_file_path)
