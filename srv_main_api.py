import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import setproctitle
from acb.utils import utils_write_to_log
from acb.redis import *



setproctitle.setproctitle('srv_main_api')
app = FastAPI()



def _api_write_to_log(s):
    return utils_write_to_log(s)




class RsyncState(BaseModel):
    text: str




@app.put("/rsync_state/")
def rsync_state(state: RsyncState):

    # curl -X PUT -H "Content-Type: application/json" -d '{"text": "nyu"}' http://localhost:8000/rsync_state/

    red.setex(
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
