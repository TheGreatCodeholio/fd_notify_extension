import logging

# importing libraries
from deepgram import Deepgram


from lib.database_handler import Database
import etc.config as config

# create logger
module_logger = logging.getLogger('fd_tone_notify_extension.transcription')


async def audio_transcription(mp3_path, mp3_url):
    module_logger.info("Transcribing Audio to Text")

    if not config.speech_to_text["deepgram_api"]:
        module_logger.critical("No Deepgram API key")
        return
    else:
        # Initializes the Deepgram SDK
        dg_client = Deepgram(config.speech_to_text["deepgram_api"])

        with open(mp3_path, 'rb') as audio:
            source = {'buffer': audio, 'mimetype': 'audio/mp3'}
            options = {'punctuate': True, 'language': 'en', 'model': 'phonecall', 'tier': 'enhanced'}

            response = await dg_client.transcription.prerecorded(source, options)
            module_logger.debug("Adding Transcription to Database Entry")
            Database().update_transcribe_text(mp3_url, response["results"]["channels"][0]["alternatives"][0]["transcript"].replace("'", "").replace(",", " "))
        audio.close()

