## Path Settings all need to end with /
fd_tone_notify_path = ""
fd_tone_notify_extension_path = ""
local_audio_path = ""
audio_url_path = ""

# Logger Settings
logger = {
    "debug": 0
}

mqtt_settings = {
    "enabled": 0,
    "mqtt_hostname": "",
    "mqtt_port": 1883,
    "mqtt_username": "",
    "mqtt_password": ""
}

broadcastify_calls_settings = {
    "enabled": 0,
    "calls_api_key": "",
    "calls_system_id": "",
    "calls_frequency": "",
    "calls_slot": "1"
}

mp3_append_text2speech_settings = {
    "enabled": 0,
    "speech_rate": 125
}

mp3_append_audio_file_settings = {
    "enabled": 0
}

mp3_convert_stereo = {
    "enabled": 0
}

mp3_high_pass_settings = {
    "enabled": 0,
    "cutoff_freq": 100
}

mp3_low_pass_settings = {
    "enabled": 0,
    "cutoff_freq": 2000
}

mp3_gain_settings = {
    "enabled": 0,
    "gain_db": 2
}

sftp_settings = {
    "enabled": 0,
    "sftp_remote_path": "",
    "sftp_username": "",
    "sftp_password": "",
    "sftp_hostname": "",
    "sftp_port": 22,
    "delete_local_file_after_upload": 0
}

mysql_settings = {
    "enabled": 0,
    "mysql_host": "",
    "mysql_port": 3306,
    "mysql_username": "",
    "mysql_password": "",
    "mysql_database": "",
}

speech_to_text = {
    "enabled": 0,
    "deepgram_api": "",
    "audio_speed": 1
}
pushover_settings = {
    "enabled": 0,
    "all_groups": 0,
    "all_groups_group_token": "",
    "all_groups_app_token": "",
    "message_html_string": """<font color="red"><b>{}</b></font>

    <a href="{}">Click for Dispatch Audio</a>
    """
}

facebook_page_settings = {
    "enabled": 0,
    "call_wait_time": 70,
    "facebook_app_token_page": "",
    "facebook_page_ids": [0000000000, 9980000000]
}

twitter_settings = {
    "enabled": 0,
    "call_wait_time": 70,
    "consumer_key": "",
    "consumer_secret": "",
    "access_token": "",
    "access_token_secret": ""
}

twilio_settings = {
    "enabled": 0,
    "account_sid": "",
    "auth_token": "",
    "from_number": ""
}

zello_settings = {
    "enabled": 0,
    "delete_after_stream": 1,
    "username": "",
    "password": "",
    "token": "",
    "channel": "",
    "issuer": "",
    "private_key": """"""
}

local_cleanup_settings = {
    "enabled": 0,
    "cleanup_days": 7
}

remote_cleanup_settings = {
    "enabled": 0,
    "cleanup_days": 7
}