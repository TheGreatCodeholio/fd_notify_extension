import requests
import logging
import etc.config as config

# create logger
module_logger = logging.getLogger('fd_tone_notify_extension.pushover')


def send_push(tone_name, tone_data, mp3_url):
    module_logger.info("Sending Pushover Notifications")

    if config.pushover_settings["all_groups"] == 1:
        module_logger.debug("Sending to Pushover Group All")
        if config.pushover_settings["all_groups_app_token"] and config.pushover_settings["all_groups_group_token"]:
            r = requests.post("https://api.pushover.net/1/messages.json", data={
                "token": config.pushover_settings["all_groups_app_token"],
                "user": config.pushover_settings["all_groups_group_token"],
                "html": 1,
                "message": config.pushover_settings["message_html_string"].format(tone_name, mp3_url)
            })
            if r.status_code == 200:
                module_logger.debug("Pushover Successful: Group All")
            else:
                module_logger.debug("Pushover Unsuccessful: Group All " + str(r.status_code))
        else:
            module_logger.critical("Missing Pushover APP or Group Token for All group")
    else:
        module_logger.debug("Pushover all group disabled.")

    if "pushover_app_token" in tone_data and "pushover_group_token" in tone_data:
        if tone_data["pushover_app_token"] and tone_data["pushover_group_token"]:
            module_logger.debug("Sending to Pushover Group")
            r = requests.post("https://api.pushover.net/1/messages.json", data={
                "token": tone_data["pushover_app_token"],
                "user": tone_data["pushover_group_token"],
                "html": 1,
                "message": config.pushover_settings["message_html_string"].format(tone_name, mp3_url)
            })
            if r.status_code == 200:
                module_logger.debug("Pushover Successful: Group " + tone_name)
            else:
                module_logger.debug("Pushover Unsuccessful: Group " + tone_name + " " + str(r.status_code))
        else:
            module_logger.critical("Missing Pushover APP or Group Token")
    else:
        module_logger.critical("Missing Pushover APP or Group Token")
