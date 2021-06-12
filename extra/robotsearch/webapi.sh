from fastapi import FastAPI
from pydantic import BaseModel

# config numpy
import numpy as np
np_load_old = np.load
np.load = lambda *a,**k: np_load_old(*a, allow_pickle=True, **k)

# config RCT tool
from robotsearch.robots import rct_robot
rct_clf = rct_robot.RCTRobot()

# create service
app = FastAPI()

class Paper(BaseModel):
    ti: str
    ab: str


@app.get("/")
async def pred_get(paper: Paper):
    ptyp = ['Journal Article']
    params = {
        "title": paper.ti,
        "abstract": paper.ab,
        "ptyp": ptyp,
        "use_ptyp": True
    }
    p = rct_clf.predict(params, filter_type="balanced", filter_class="svm_cnn")
    ret = {
        'pred': p,
        'params': params
    }
    return ret
    
@app.post("/")
async def pred_get(paper: Paper):
    ptyp = ['Journal Article']
    params = {
        "title": paper.ti,
        "abstract": paper.ab,
        "ptyp": ptyp,
        "use_ptyp": True
    }
    p = rct_clf.predict(params, filter_type="balanced", filter_class="svm_cnn")
    ret = {
        'pred': p,
        'params': params
    }
    return ret