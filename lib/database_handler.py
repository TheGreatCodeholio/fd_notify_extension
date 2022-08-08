# Python Core
import datetime
import json
import logging
# Python 3rd Party
import mysql.connector as mysql

# Project Libraries
import etc.config as config

# create logger
module_logger = logging.getLogger('fd_tone_notify_extension.mysql')


class Database:
    def __init__(self):
        self.logger = logging.getLogger('fd_tone_notify_extension.mysql.Database')
        self.connection = mysql.connect(
            host=config.mysql_settings["mysql_host"],
            user=config.mysql_settings["mysql_username"],
            password=config.mysql_settings["mysql_password"],
            database=config.mysql_settings["mysql_database"],
            auth_plugin='mysql_native_password'
        )
        self.cursor = self.connection.cursor(dictionary=True)

    def add_new_call(self, timestamp, tone_name, tone_data, mp3_url):
        self.logger.info("Adding Detection to Database")
        timestamp = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        query = "INSERT INTO fd_notify_detections (detection_tone_name, detection_tone_data, detection_mp3_url, detection_timestamp) VALUES (%s, %s, %s, %s)"
        self.cursor.execute(query, (tone_name, json.dumps(tone_data), mp3_url, timestamp))
        self.connection.commit()
        self.cursor.close()
        self.connection.close()

    def update_transcribe_text(self, call_mp3_url, transctiption):
        self.logger.info("Updating Transcription in Database")
        query = "UPDATE fd_notify_detections set detection_transcription = %s WHERE detection_mp3_url = %s"
        values = (transctiption, call_mp3_url)
        self.cursor.execute(query, values)
        self.connection.commit()
        self.cursor.close()
        self.connection.close()

    def get_call_info(self, call_mp3_url):
        self.logger.info("Getting Detection Info")
        query = "SELECT * from fd_notify_detections WHERE detection_mp3_url = %s"
        values = (call_mp3_url,)
        self.cursor.execute(query, values)
        data = self.cursor.fetchall()
        self.cursor.close()
        self.connection.close()
        if data:
            self.logger.debug("Returning Detection Info")
            return data
        else:
            self.logger.debug("No Detection Info Found")
            return False
