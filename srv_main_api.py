import uvicorn
from fastapi import FastAPI, Response, status
from pydantic import BaseModel
import setproctitle
import redis

from acb.utils import utils_get_today_log_path


setproctitle.setproctitle('srv_main_api')
app = FastAPI()
r = redis.Redis('localhost', port=6379)
RD_ACB_RSYNC_STATE_TEXT = 'acb:rsync_state_text'
RD_ACB_RSYNC_FLAG_LOG = 'acb:rsync_flag_log'



def _api_write_to_log(s):

    # choose things we log
    filename_log = utils_get_today_log_path()
    with open(filename_log, 'a') as f:
        f.write(f'{s}\n')
    r.set(RD_ACB_RSYNC_FLAG_LOG, s)




class RsyncState(BaseModel):
    text: str




@app.put("/rsync_state/")
def rsync_state(state: RsyncState):

    # curl -X PUT -H "Content-Type: application/json" -d '{"text": "nyu"}' http://localhost:8000/rsync_state/

    r.setex(
        RD_ACB_RSYNC_STATE_TEXT,
        10,
        state.text
    )
    if 'ping' in state.text:
        d_ans = {'answer': 'pong'}
    else:
        d_ans = {'answer': state.text}


    # add to today's_log and flag it
    _api_write_to_log(state.text)


    return d_ans



if __name__ == '__main__':
    uvicorn.run(app, port=8000, host='0.0.0.0')
