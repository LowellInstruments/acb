import datetime


def utils_get_today_log_path():
    s_t = datetime.datetime.now().strftime("%Y_%m_%d")
    filename_log = f'logs/acbotics_{s_t}.txt'
    return filename_log