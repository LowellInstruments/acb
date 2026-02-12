#!/usr/bin/env python3


import datetime
import time
import subprocess as sp
import os
from acb.redis import *
from acb.utils import utils_write_to_log



access_key = os.getenv('AWS_ACCESS_KEY_ID')
secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
fol_upload = '/home/acbotics/Downloads/acbotics'
# fol_upload = '/home/kaz/Downloads/acbotics'
bucket_name = 'bkt-acbotics'



def _aws_write_to_log(s):
    return utils_write_to_log(s)



# -------------------------------------------------
# fish_data_archive
#     FB00001_10_20251118_122122
#         images
#             1_20251118_122122
#                 bgr1-10.jpg
#                 bgr1-1.jpg
#             2_20251118_122144
#                 bgr1-10.jpg
#                 bgr1-1.jpg
#         session.db
#     FB00001_11_20251118_122205
#         images
#             1_20251118_122205
#                 bgr1-10.jpg
#                 bgr1-1.jpg
#   FB00001_1_20251015_115350
#
#
# offload
#     20251204_112800
#     20251204_112826
#     20251204_151649
#         D1
#             AC1_1.dat
#             CC_1_1.cfg
#             CC_1_1.txt
#             SENS_1_1.dat
#         D2
#             AC2_1.dat
#             CC_2_1.cfg
#             CC_2_1.txt
#             SENS_2_1.dat
# -------------------------------------------------



def _aws_loop():

    # AWS progress indicator
    s_aws = 'working'
    red.set('acb:aws', s_aws)
    s_aws = 'error'


    if not access_key or not secret_key:
        print('AWS: error, credentials invalid')
        _aws_write_to_log('error AWS credentials')
    else:
        print(f"AWS: trying upload folder {fol_upload} to bucket {bucket_name}")
        c_debug = (
            f'AWS_ACCESS_KEY_ID={access_key} AWS_SECRET_ACCESS_KEY={secret_key} '
            f'aws s3 sync {fol_upload} s3://{bucket_name} '
            f'--exclude \'*\' '
            f'--include \'*.txt\' '
            f'--dryrun'
        )
        c_prod = (
            f'AWS_ACCESS_KEY_ID={access_key} AWS_SECRET_ACCESS_KEY={secret_key} '
            f'aws s3 sync {fol_upload} s3://{bucket_name} '
        )
        c = c_prod
        rv = sp.run(c, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
        ts = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        if rv.returncode == 0:
            s_aws = 'OK'
            print(f'{rv.stdout.decode()}')
            print(f"AWS: OK to bucket {bucket_name}")
            utils_write_to_log('AWS sync OK')
        else:
            print(f'error: AWS -> {rv.stderr.decode()}')
            utils_write_to_log('AWS sync error')



    # AWS state will be read by the timer in GUI
    red.set('acb:aws', s_aws)
    return s_aws



def aws_loop(just_once=False):
    utils_write_to_log(f'AWS bucket {bucket_name}')
    while 1:
        s_rv = _aws_loop()
        print(f'AWS: sleep 1 hour, last operation = {s_rv}')
        time.sleep(3600)
        if just_once:
            break



if __name__ == '__main__':
    aws_loop(just_once=True)
