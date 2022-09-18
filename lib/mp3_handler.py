import logging
import shutil
import subprocess

from pydub import AudioSegment, effects, silence
import pyttsx3
import os

import etc.config as config

# create logger
module_logger = logging.getLogger('fd_tone_notify_extension.mp3')


def append_text2speech_audio(tone_name, mp3_file, local_audio_path):
    module_logger.info("Appending Text to Speech")
    tone_name = tone_name.replace(" ", "_")
    engine = pyttsx3.init()
    engine.setProperty('rate', config.mp3_append_text2speech_settings["speech_rate"])
    engine.save_to_file(tone_name, local_audio_path + tone_name + ".mp3")
    engine.runAndWait()
    audio1 = AudioSegment.from_mp3(mp3_file)
    audio2 = AudioSegment.from_mp3(local_audio_path + tone_name + ".mp3")
    new_audio = audio2 + audio1
    new_audio.export(mp3_file, format="mp3", tags={'artist': tone_name})
    if os.path.exists(local_audio_path + tone_name + ".mp3"):
        os.remove(local_audio_path + tone_name + ".mp3")


def remove_silence(wav_file_path):
    module_logger.info("Removing Silence From Audio")
    temp_wav_file_path = wav_file_path + ".tmp"
    os.replace(wav_file_path, temp_wav_file_path)
    command = "ffmpeg -y -i " + temp_wav_file_path + " -af silenceremove=stop_periods=-1:stop_threshold=" + str(
        config.mp3_remove_silence_settings["silence_threshold"]) + "dB:stop_duration=" + str(
        config.mp3_remove_silence_settings["min_silence_length"]) + " " + wav_file_path
    subprocess.run(command.split(), capture_output=True)
    os.remove(temp_wav_file_path)

    os.replace(wav_file_path.replace(".wav", ".mp3"), temp_wav_file_path.replace(".wav", ".mp3"))
    command = "ffmpeg -y -i " + temp_wav_file_path.replace(".wav", ".mp3") + " -af silenceremove=stop_periods=-1:stop_threshold=" + str(
        config.mp3_remove_silence_settings["silence_threshold"]) + "dB:stop_duration=" + str(
        config.mp3_remove_silence_settings["min_silence_length"]) + " " + wav_file_path.replace(".wav", ".mp3")
    subprocess.run(command.split(), capture_output=True)
    os.remove(temp_wav_file_path.replace(".wav", ".mp3"))


def convert_stereo(tone_name, file):
    module_logger.info("Converting to Stereo")
    audio1 = AudioSegment.from_mp3(file)
    new_audio = audio1.set_channels(2)
    new_audio.export(file, format="mp3", tags={'artist': tone_name})


def gain_filter(tone_name, file):
    module_logger.info("Applying Gain Filter")
    audio1 = AudioSegment.from_mp3(file)
    new_audio = audio1.apply_gain(config.mp3_gain_settings["gain_db"])
    new_audio.export(file, format="mp3", tags={'artist': tone_name})


def append_audio_file(tone_name, local_mp3_path, tone_data):
    module_logger.info("Appending Audio File")
    audio1 = AudioSegment.from_mp3(local_mp3_path)
    audio2 = AudioSegment.from_mp3(tone_data["mp3_append_file"])
    new_audio = audio2 + audio1
    new_audio.export(local_mp3_path, format="mp3", tags={'artist': tone_name})


def low_pass_filter(tone_name, file):
    module_logger.info("Applying Low Pass Filter")
    audio1 = AudioSegment.from_mp3(file)
    new_audio = effects.low_pass_filter(audio1, cutoff=config.mp3_low_pass_settings["cutoff_freq"])
    new_audio.export(file, format="mp3", tags={'artist': tone_name})


def high_pass_filter(tone_name, file):
    module_logger.info("Applying High Pass Filter")
    audio1 = AudioSegment.from_mp3(file)
    new_audio = effects.high_pass_filter(audio1, cutoff=config.mp3_high_pass_settings["cutoff_freq"])
    new_audio.export(file, format="mp3", tags={'artist': tone_name})
