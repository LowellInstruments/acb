import json
import subprocess as sp
import threading
import time
import requests
from cli_conf import *



def _is_rpi():
    c = 'cat /proc/cpuinfo | grep aspberry'
    rv = sp.run(c, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    return rv.returncode == 0



def _icmp_ping(ip):
    try:
        c = f'timeout 2 ping -c 1 {ip}'
        rv = sp.run(c, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
        if rv.returncode:
            return 1
        return 0
    except (Exception, ):
        return 1



def _check_destination_is_reachable(ip):

    # we need environment variable RSYNC password to continue
    try:
        if not RSYNC_PASSWORD:
            raise Exception('RSYNC_PASSWORD not set')
    except (Exception, ) as ex:
        print(f'CLI: error, no env var -> {ex}')
        return 1


    # can we detect destination's remote network host
    rv = _icmp_ping(ip)
    if rv:
        print(f'CLI: error, no ICMP answer to ping')
        return 2
    print('CLI: received ICMP pong from target')


    # can we detect destination's remote API
    rv = _send_ping_to_api(ip)
    if rv:
        print(f'CLI: error, no API answer to ping')
        return 3
    print('CLI: received API pong from target')


    # basic RSYNC reachability test
    c_ls = f'rsync --list-only acb@{ip}::'
    rv = sp.run(c_ls, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    if rv.returncode:
        print(f'CLI: error, could not rsync-list target ip {ip}')
        return 4

    return 0



def _th_fxn_rsync_send_data_file(ip, fol_src):

    # ---------------------------------------------------
    # RSYNC-send thread writes its progress to file <ppf>
    # ---------------------------------------------------

    username = 'acbotics'
    if not _is_rpi():
        username = 'acbotics'
        print(f"CLI: development, changing user name from acb -> {username}")
    c = f'rsync -azvP {fol_src} {username}@{ip}::{RSYNC_MODULE} > {PATH_FILE_PROGRESS_RSYNC}'
    print(f"CLI: {c}")
    rv = sp.run(c, shell=True, stdout=sp.PIPE)
    if rv.returncode == 0:
        return
    with open(PATH_FILE_PROGRESS_RSYNC, 'w') as f:
        f.write('error_thread_rsync')



def _send_cmd_to_api(ip, s):
    d = {"text": s}
    url = f'http://{ip}:8000/rsync_state/'
    try:
        rsp = requests.put(url, data=json.dumps(d))
        rsp.raise_for_status()
        return rsp.text
    except (Exception, ) as ex:
        print(f'CLI: error, _send_to_api -> {ex}')



def _send_ping_to_api(ip):
    rv = _send_cmd_to_api(ip, f'ping by {SENDER_ID}')
    if rv:
        d = json.loads(rv)
        if d['answer'] == 'pong':
            return 0
    return 1



def _send_text_to_api(ip, s):
    print(f'<- {s}')
    return _send_cmd_to_api(ip, s)





def rsync_send(ip):

    rv = _check_destination_is_reachable(ip)
    if rv:
        return rv

    # pre-delete cli_send log file
    if os.path.exists(PATH_FILE_PROGRESS_RSYNC):
        os.unlink(PATH_FILE_PROGRESS_RSYNC)

    # check the things to send really exist
    if not os.path.isdir(FOLDER_TO_SEND):
        print(f"CLI: error, folder to send not found {FOLDER_TO_SEND}")
        return 1

    # ----------------------------------------------------
    # start thread to RSYNC-send the file, do not join it
    # ----------------------------------------------------

    th = threading.Thread(
        target=_th_fxn_rsync_send_data_file,
        args=(ip, FOLDER_TO_SEND)
    )
    th.start()


    # mark start of transfer
    _send_text_to_api(ip, 'Acbotics peer detected')


    # --------------------------------------
    # wait for thread RSYNC-send to finish
    # --------------------------------------
    rv = 0
    while 1:

        time.sleep(1)

        # happens always, either good or bad
        if not th.is_alive():
            _send_text_to_api(ip, 'all sent, leaving')
            break

        with open(PATH_FILE_PROGRESS_RSYNC, 'r') as f:
            ll = f.readlines()
            if not ll:
                print('.')
                continue


        # format list
        ll = [i.replace('\n', '') for i in ll if i != '\n']
        last_bn = ''
        d = {}

        # ll: example
        # ['sending incremental file list',
        #  'Sonde081425_142800/',
        #  'Sonde081425_142800/code_1.109.0-1770171879_amd64.deb',
        #  '            776   0%    0.00kB/s    0:00:00  ',
        #  '     15,023,976  12%   13.96MB/s    0:00:07  ',
        #  '     26,951,528  23%   12.69MB/s    0:00:06  ',

        for i, line in enumerate(ll):

            if 'error' in line:
                _send_text_to_api(ip, 'error in thread')
                rv = 1
                break

            elif 'total size' in line:
                _send_text_to_api(ip, 'all sent')
                break

            elif line[-4] == '.':
                # last basename
                last_bn = os.path.basename(line)

            elif 'kB/s' in line or 'MB/s' in line:
                ls = line.split()
                if 'xfr#' in line:
                    # indicates file complete
                    to_chk = ls[-1].split('=')[1].split(')')[0]
                    speed = ls[2]
                    # d[last_bn] = f'{speed}, ({to_chk})'
                    n_i = int(to_chk.split('/')[0])
                    n_max = int(to_chk.split('/')[1])
                    # show not remaining but done ones
                    to_chk_inv = f'({n_max - n_i} / {n_max})'
                    d[last_bn] = to_chk_inv
                # just progress
                else:
                    n = len(ls)
                    if n == 4:
                        # line: 94,131,168  80%   36.50MB/s    0:00:00
                        dl_xcent = ls[1]
                        dl_speed = ls[2]
                        s_progress = f'{last_bn}\n{dl_xcent}\n{dl_speed}'
                        if dl_xcent != '0%':
                            _send_cmd_to_api(ip, s_progress)


            elif i == len(ll) - 1:
                if d:
                    last_name = list(d.keys())[-1]
                    last_stats = list(d.values())[-1]
                    _send_text_to_api(ip, f'receiving {last_name}, {last_stats}')

    print('CLI: rv RSYNC-send = ', rv)
    return rv




if __name__ == '__main__':
    rsync_send(IP_DST)
