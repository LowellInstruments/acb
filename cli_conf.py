import os



PATH_FILE_PROGRESS_RSYNC = '/tmp/acb_progress.log'
FOLDER_TO_SEND = '/home/kaz/Downloads/Sonde081425_142800'
RSYNC_MODULE = "acbotics"
RSYNC_PASSWORD = ''
try:
    if not RSYNC_PASSWORD:
        RSYNC_PASSWORD = os.environ['RSYNC_PASSWORD']
except (Exception, ):
    print('error, cannot find environment variable RSYNC_PASSWORD')
IP_DST = '192.168.0.223'
SENDER_ID = 'ACB #3'



# example of rsync CLIENT command
# using :: means direct connection to rsync daemon w/out using SSH transport
# ---------------------------------------------------------------------------
# rsync -azvP {CLI_FOLDER_TO_SEND} {RSYNC_USERNAME}@192.168.0.169::{RSYNC_MODULE} > /tmp/acb_progress.log


# example of rsync SERVER file /etc/rsyncd.secrets
# ------------------------------------------------
# username:password
# (empty new line at the end)


# example of rsync SERVER file /etc/rsyncd.conf
# ---------------------------------------------
# lock file = /var/run/rsync.lock
# log file = /var/log/rsyncd.log
# pid file = /var/run/rsyncd.pid
# [module_name]
#     # path = /home/kaz/Downloads/acbotics
#     path = /home/pi/Downloads/acbotics
#     comment = acbotics download folder
#     uid = kaz
#     gid = kaz
#     read only = no
#     list = yes
#     secrets file = /etc/rsyncd.secrets
#     auth users = username_as_in_secrets_file
#     hosts allow = 127.0.0.1, 192.168.0.169, 192.168.0.0/255.255.255.0
