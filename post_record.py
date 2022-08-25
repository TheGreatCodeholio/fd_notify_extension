__author__ = "Ian Carey"
__version__ = "0.1"
__license__ = "MIT"

import argparse
import logging
import datetime
import json
import os
import shutil
import asyncio
from threading import Thread

import lib.broadcastify_calls_handler as broadcastify
import lib.mp3_handler as mp3
import lib.sftp_handler as sftp
from lib.audio_transcription_handler import audio_transcription
from lib.database_handler import Database
import lib.pushover_handler as pushover
import lib.facebook_handler as fbook
import lib.discord_handler as discord
import lib.twitter_handler as twitter
import lib.twilio_handler as twilio
import lib.zello_handler as zello
import lib.cleanup_handler as cleanup

import etc.config as config

# create logger
logger = logging.getLogger('fd_tone_notify_extension')

logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler(config.fd_tone_notify_extension_path + 'var/log/fd_tone_notify_extension_post.log')
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
parser.add_argument("timestamp", help="Timestamp.")
parser.add_argument("tone_name", help="Tone Name.")
parser.add_argument("audio_path", help="MP3 Filepath.")
parser.add_argument("department_info", help="Department Info JSON String.")
args = parser.parse_args()
logger.info("Post Record Script Start")
threads = []


def zello_init(config, mp3_local_path):
    config.token = zello.zello_create_token(config)
    opus_file = zello.zello_convert(mp3_local_path)
    zello.ZelloSend(config, opus_file).zello_init_upload()
    if config.zello_settings["delete_after_stream"] == 1:
        if os.path.exists(opus_file):
            os.remove(opus_file)


try:
    # create timestamp
    ts = int(args.timestamp) / 1000
    x = datetime.datetime.fromtimestamp(ts)
    current_date = x.strftime("%Y_%m_%d_%H_%M_%S")
    year = x.strftime("%Y")
    month = x.strftime("%m")
    day = x.strftime("%d")

    # folder creation for audio files
    if not os.path.exists(config.local_audio_path + str(year) + "/"):
        os.mkdir(config.local_audio_path + str(year) + "/")
    if not os.path.exists(config.local_audio_path + str(year) + "/" + str(month) + "/"):
        os.mkdir(config.local_audio_path + str(year) + "/" + str(month) + "/")
    if not os.path.exists(config.local_audio_path + str(year) + "/" + str(month) + "/" + str(day) + "/"):
        os.mkdir(config.local_audio_path + str(year) + "/" + str(month) + "/" + str(day) + "/")

    local_audio_path = config.local_audio_path + str(year) + "/" + str(month) + "/" + str(day) + "/"

    # remove quotes and replace spaces with _ in tone name
    tone_name = args.tone_name.replace("\"", "")

    # load tone data from json
    tone_data = json.loads(args.department_info)

    # cleanup mp3 name and delete wav
    mp3_fd_notify_path = config.fd_tone_notify_path + args.audio_path.replace("./", "")
    mp3_new_name = tone_name.replace(" ", "_") + "_" + current_date + ".mp3"
    mp3_url = config.audio_url_path + mp3_new_name
    mp3_local_path = local_audio_path + mp3_new_name

    # Move both files created by fd tone notify to audio local path
    shutil.move(mp3_fd_notify_path.replace(".mp3", ".wav"),
                local_audio_path + mp3_new_name.replace(".mp3", ".wav"))
    shutil.move(mp3_fd_notify_path, local_audio_path + mp3_new_name)

    if config.mp3_remove_silence_settings["enabled"] == 1:
        logger.debug("Remove Silence Enabled")
        mp3.remove_silence(int(ts), tone_name.lower().replace(" ", "_"),
                           local_audio_path + mp3_new_name.replace(".mp3", ".wav"))
    else:
        logger.debug("Remove Silence Disabled")

    if config.broadcastify_calls_settings["enabled"] == 1:
        logger.debug("Broadcastify Calls Enabled")
        bcfy = Thread(target=broadcastify.queue_call,
                      args=(int(ts), tone_name.lower().replace(" ", "_"), tone_data, mp3_url, local_audio_path + mp3_new_name.replace(".mp3", ".wav")))
        bcfy.start()
        threads.append(bcfy)
    else:
        logger.debug("Broadcastify Calls Disabled")

    if config.discord_settings["enabled"] == 1:
        logger.debug("Discord Posting Enabled")
        disc = Thread(target=discord.send_audio_text,
                      args=(int(ts), args.tone_name, tone_data, mp3_url, local_audio_path + mp3_new_name))
        disc.start()
        threads.append(disc)
    else:
        logger.debug("Discord Posting Disabled")

    if config.twilio_settings["enabled"] == 1:
        logger.debug("Twilio SMS Enabled")
        tw = Thread(target=twilio.create_twilio_sms, args=(tone_name, tone_data, mp3_url))
        tw.start()
        threads.append(tw)
    else:
        logger.debug("Twilio SMS Calls Disabled")

    if config.pushover_settings["enabled"] == 1:
        logger.debug("Pushover Enabled")
        po = Thread(target=pushover.send_push, args=(tone_name, tone_data, mp3_url))
        po.start()
        threads.append(po)
    else:
        logger.debug("Pushover Disabled")

    if config.facebook_page_settings["enabled"] == 1:
        logger.debug("Facebook Page Post Enabled")
        # Post to Facebook Group
        fb = Thread(target=fbook.send_post, args=(ts, args.tone_name, args.department_info, mp3_url, mp3_local_path))
        fb.start()
        threads.append(fb)
    else:
        logger.debug("Facebook Page Post Disabled")

    if config.twitter_settings["enabled"] == 1:
        logger.debug("Twitter Enabled")
        # Post to Twitter
        tr = Thread(target=twitter.send_tweet, args=(args.tone_name, args.department_info, mp3_url, mp3_local_path))
        tr.start()
        threads.append(tr)
    else:
        logger.debug("Twitter Disabled")

    # Mp3 Manipulation In order: append text2speech -> append file -> stereo -> low pass -> high pass -> gain
    if config.mp3_append_text2speech_settings["enabled"] == 1:
        logger.debug("Append Tone Name Audio Enabled")
        mp3.append_text2speech_audio(tone_name, mp3_local_path, local_audio_path)
    else:
        logger.debug("Append Tone Name Audio Disabled")

    if tone_data["mp3_append_file"]:
        logger.debug("Append Audio File Enabled")
        mp3.append_audio_file(tone_name, mp3_local_path, tone_data)
    else:
        logger.debug("Append Audio File Disabled")

    if config.mp3_convert_stereo["enabled"] == 1:
        logger.debug('Stereo Convert Enabled')
        mp3.convert_stereo(tone_name, mp3_local_path)
    else:
        logger.debug('Stereo Convert Disabled')

    if config.mp3_low_pass_settings["enabled"] == 1:
        logger.debug('Low Pass Filter Enabled')
        mp3.low_pass_filter(tone_name, mp3_local_path)
    else:
        logger.debug('Low Pass Filter Disabled')

    if config.mp3_high_pass_settings["enabled"] == 1:
        logger.debug('High Pass Filter Enabled')
        mp3.high_pass_filter(tone_name, mp3_local_path)
    else:
        logger.debug('High Pass Filter Disabled')

    if config.mp3_gain_settings["enabled"] == 1:
        logger.debug("Gain Filter Enabled")
        mp3.gain_filter(tone_name, mp3_local_path)
    else:
        logger.debug("Gain Filter Disabled")

    if config.zello_settings["enabled"] == 1:
        logger.debug("Zello Enabled")
        zl = Thread(target=zello_init, args=(config, mp3_local_path))
        zl.start()
        threads.append(zl)
    else:
        logger.debug("Zello Disabled")

    # Upload MP3 to remote webserver
    if config.sftp_settings["enabled"] == 1:
        logger.debug("SFTP Enabled")
        # Send file to remote server
        sftp.upload_to_path(config.sftp_settings["sftp_remote_path"], mp3_local_path)
    else:
        logger.debug("SFTP Disabled")

    if config.mysql_settings["enabled"] == 1:
        logger.debug("MySQL Enabled")
        Database().add_new_call(ts, tone_name, tone_data, mp3_url)
    else:
        logger.debug("MySQL Enabled")

    if config.speech_to_text["enabled"] == 1 and config.mysql_settings["enabled"] == 1:
        logger.debug("Speech to Text Enabled")
        asyncio.run(audio_transcription(mp3_local_path, mp3_url))
    else:
        logger.debug("Speech to Text Disabled")

    if config.sftp_settings["enabled"] == 1:
        if config.sftp_settings["delete_local_file_after_upload"] == 1:
            os.remove(mp3_local_path)

    if config.local_cleanup_settings["enabled"] == 1:
        logger.debug("Local File Cleanup Enabled")
        cleanup.cleanup_local_audio()
    else:
        logger.debug("Local File Cleanup Disabled")

    if config.remote_cleanup_settings["enabled"] == 1:
        logger.debug("Remote File Cleanup Enabled")
        sftp.clean_remote_files()
    else:
        logger.debug("Remote File Cleanup Disabled")

    for x in threads:
        x.join()

    logger.info("Post Record Script Complete")


except Exception as e:
    logger.critical(e)
