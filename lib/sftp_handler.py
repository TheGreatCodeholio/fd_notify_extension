import logging
from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient
import etc.config as config

# create logger
module_logger = logging.getLogger('fd_tone_notify_extension.sftp')

def upload_to_path(remote_path, local_file):
    module_logger.info("Uploading " + local_file + " to " + config.sftp_settings["sftp_hostname"])
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    ssh.connect(config.sftp_settings["sftp_hostname"], port=config.sftp_settings["sftp_port"],
                username=config.sftp_settings["sftp_username"], password=config.sftp_settings["sftp_password"])

    scp = SCPClient(ssh.get_transport())
    scp.put(local_file, remote_path=remote_path)

def clean_remote_files():
    module_logger.info("Cleaning Remote Files")
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    ssh.connect(config.sftp_settings["sftp_host"], port=config.sftp_settings["sftp_port"],
                username=config.sftp_settings["sftp_user"], password=config.sftp_settings["sftp_pass"])
    command = "find " + config.sftp_settings["remote_path"] + "* -mtime +" + str(
        config.remote_cleanup_settings["cleanup_days"]) + " -exec rm {} \;"
    stdin, stdout, stderr = ssh.exec_command(command)
    for line in stdout:
        module_logger.debug(line)
    module_logger.debug("Cleaned Remote Files")
