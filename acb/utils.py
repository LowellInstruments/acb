import datetime
import socket
import struct
import subprocess as sp
import fcntl
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




def utils_is_rpi():
    c = 'cat /proc/cpuinfo | grep aspberry'
    rv = sp.run(c, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    return rv.returncode == 0




def utils_get_ip_address(if_name):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', if_name[:15])
        )[20:24])
    except (Exception, ):
        return 'N/A'
