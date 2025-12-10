import uvicorn
from fastapi import FastAPI, Response, status
from pydantic import BaseModel
import setproctitle
import redis



setproctitle.setproctitle('srv_main_api')
app = FastAPI()
r = redis.Redis('localhost', port=6379)
RD_ACB_RSYNC_STATE_TEXT = 'acb:rsync_state_text'



class RsyncState(BaseModel):
    text: str




@app.put("/rsync_state/")
async def rsync_state(state: RsyncState):
    # curl -X PUT -H "Content-Type: application/json" -d '{"text": "nyu"}' http://localhost:8000/rsync_state/
    r.set(RD_ACB_RSYNC_STATE_TEXT, state.text)


    # we only have 2 commands
    if 'ping' in state.text:
        d_ans = {'answer': 'pong'}
    else:
        d_ans = {'answer': state.text}


    # the client sending thread tells us the rsync state
    # this will be read by GUI
    if d_ans:
        r.set(RD_ACB_RSYNC_STATE_TEXT, state.text)
        r.expire(RD_ACB_RSYNC_STATE_TEXT, 10)

    return d_ans



if __name__ == '__main__':
    uvicorn.run(app, port=8000, host='0.0.0.0')
