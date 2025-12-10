#!/usr/bin/env python3


import time
import subprocess as sp
import os
import redis



r = redis.Redis('localhost')
ak = os.getenv('AWS_ACCESS_KEY_ID')
sk = os.getenv('AWS_SECRET_ACCESS_KEY')
fol_upload = '/home/acbotics/Downloads/acbotics'
# fol_upload = '/home/kaz/Downloads/acbotics'
bucket_name = 'bkt-acbotics'



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
    s = 'working'
    r.set('acb:aws', s)
    s = 'error'

    if ak == '' or sk == '':
        print('error, AWS credentials invalid')
    else:
        c_debug = (
            f'AWS_ACCESS_KEY_ID={ak} AWS_SECRET_ACCESS_KEY={sk} '
            f'aws s3 sync {fol_upload} s3://{bucket_name} '
            f'--exclude \'*\' '
            f'--include \'*.txt\' '
            f'--dryrun'
        )
        c_prod = (
            f'AWS_ACCESS_KEY_ID={ak} AWS_SECRET_ACCESS_KEY={sk} '
            f'aws s3 sync {fol_upload} s3://{bucket_name} '
        )
        c = c_prod
        rv = sp.run(c, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
        if rv.returncode == 0:
            s = 'OK'
            print(f'{rv.stdout.decode()}')
        else:
            print(f'error: AWS -> {rv.stderr.decode()}')


    # AWS state will be read by the timer in GUI
    r.set('acb:aws', s)
    return s



def aws_loop(just_once=False):
    while 1:
        s = _aws_loop()
        print(f'AWS loop sleeping for 1 hour, last operation = {s}')
        time.sleep(3600)
        if just_once:
            break



if __name__ == '__main__':
    print('starting AWS loop')
    aws_loop(just_once=True)
