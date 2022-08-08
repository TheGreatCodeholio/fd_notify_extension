import os
import time
import logging
import etc.config as config

# create logger
module_logger = logging.getLogger('fd_tone_notify_extension.local_cleanup')


def cleanup_local_audio():
    module_logger.info("Cleaning Files")
    current_time = time.time()
    count = 0
    for f in os.listdir(config.local_audio_path):
        path = os.path.join(config.local_audio_path, f)
        creation_time = os.path.getctime(path)
        if (current_time - creation_time) // (24 * 3600) >= config.local_cleanup_settings["cleanup_days"]:
            count += 1
            os.unlink(path)
    module_logger.debug("Cleaned " + str(count) + " Files")
