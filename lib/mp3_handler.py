import logging
import shutil

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


def remove_silence(timestamp, detector_name, wav_file_path):
    chunk_list = {}
    wav_audio = AudioSegment.from_file(wav_file_path)
    chunks = silence.split_on_silence(wav_audio, min_silence_len=config.mp3_remove_silence_settings["min_silence_length"], silence_thresh=config.mp3_remove_silence_settings["silence_threshold"])
    if not os.path.exists(f'{str(timestamp)}_{detector_name}/'):
        os.mkdir(f'{str(timestamp)}_{detector_name}/')
    for i, chunk in enumerate(chunks):
        afile = f'{str(timestamp)}_{detector_name}/chunk{i}.wav'
        # print("Exporting file", afile)
        chunk.export(afile, format="wav")
        caudio = AudioSegment.from_file(afile)
        caudio_len = caudio.duration_seconds
        chunk_list[i] = caudio_len

    max_value = max(chunk_list, key=chunk_list.get)
    del chunk_list[max_value]
    for ch in chunk_list:
        dfile = f'{str(timestamp)}_{detector_name}/chunk{ch}.wav'
        os.remove(dfile)
    ffile = f'{str(timestamp)}_{detector_name}/chunk{max_value}.wav'

    split_audio = AudioSegment.from_file(ffile)
    split_audio.export(wav_file_path, format="wav", tags={'artist': detector_name})
    split_audio.export(wav_file_path.replace(".wav", ".mp3"), format="mp3", tags={'artist': detector_name})

    if os.path.exists(f'{str(timestamp)}_{detector_name}'):
        shutil.rmtree(f'{str(timestamp)}_{detector_name}')


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
