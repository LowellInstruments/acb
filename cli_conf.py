import os


PATH_FILE_PROGRESS_RSYNC = '/tmp/acb_progress.log'
FOLDER_TO_SEND = '/home/kaz/Downloads/Sonde081425_142800'
RSYNC_DST_ENTRY = "acbotics"
RSYNC_PASSWORD = ''
try:
    if not RSYNC_PASSWORD:
        RSYNC_PASSWORD = os.environ['RSYNC_PASSWORD']
except (Exception, ):
    print('error, cannot find environment variable RSYNC_PASSWORD')
IP_DST = '192.168.9.1'
SENDER_ID = 'ACB #3'

