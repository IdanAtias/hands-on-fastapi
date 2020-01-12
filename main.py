import threading
import logging
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException

purim_app = FastAPI()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Costume(BaseModel):
    name: str
    size: int
    costume_id: int = None


costumes = {}
curr_id = 0
lock = threading.Lock()


@purim_app.get("/")
async def root():
    return {"message": "Welcome to Purim app"}


@purim_app.post("/costumes/")
async def add_costume(c: Costume):
    global curr_id
    logger.debug("%s adding costume '%s'" % (threading.current_thread(), c))
    with lock:
        costumes[curr_id] = c
        c.costume_id = curr_id
        curr_id += 1
    logger.debug("%s added costume '%s'" % (threading.current_thread(), c))
    return c


@purim_app.get("/costumes/")
async def get_costumes(costume_id: int = None):
    with lock:
        if costume_id is None:
            logger.debug("%s getting info on all costumes" % threading.current_thread())
            res = costumes.copy()
        elif costume_id in costumes:
            logger.debug("%s getting info on costume with id %s" % (threading.current_thread(), costume_id))
            res = costumes[costume_id]
        else:
            raise HTTPException(status_code=400, detail="No such costume with id '%s'" % costume_id)
    logger.debug("%s done getting info" % threading.current_thread())
    return res
