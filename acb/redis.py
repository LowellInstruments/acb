import redis


red = redis.Redis('localhost', port=6379)


RD_ACB_RSYNC_STATE_TEXT = 'acb:rsync_state_text'
RD_ACB_RSYNC_FLAG_LOG = 'acb:rsync_flag_log'
