import datetime
from acb.redis import *





def utils_get_today_log_path():
    s_t = datetime.datetime.now().strftime("%Y_%m_%d")
    filename_log = f'logs/acbotics_{s_t}.txt'
    return filename_log



def utils_write_to_log(s):
    filename_log = utils_get_today_log_path()
    now = datetime.datetime.now().strftime("%H:%M:%S")
    with open(filename_log, 'a') as f:
        f.write(now + '\n')
        f.write(f'{s}\n')
    red.set(RD_ACB_RSYNC_FLAG_LOG, s)
