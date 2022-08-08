import time
import logging
from twilio.rest import Client
import etc.config as config

# create logger
module_logger = logging.getLogger('fd_tone_notify_extension.twilio')

def create_twilio_sms(tone_name, tone_data, mp3_url):
    module_logger.info("Sending SMS with Twilio")
    message = f'''🚨 Dispatch Alert {tone_name}
    {mp3_url}
    '''
    for num in tone_data["twilio_sms_numbers"]:
        send_twilio_sms(message, num)
        time.sleep(1)


def send_twilio_sms(message, sms_number):
    # Find your Account SID and Auth Token at twilio.com/console
    # and set the environment variables. See http://twil.io/secure
    client = Client(config.twilio_settings["account_sid"], config.twilio_settings["auth_token"])

    message = client.messages.create(body=message, from_=config.twilio_settings["from_number"], to=sms_number)
    module_logger.info(message.status)

