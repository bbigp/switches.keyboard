from fastapi import APIRouter
from pydantic.main import BaseModel
from sqlalchemy import func, select

from app.core.database import SqlSession
from app.model.domain import sqlm_keyboard_switch, KeyboardSwitch

stats_router = APIRouter(prefix='/api/stats')

@stats_router.get('/mkswitch')
async def stats_mks():
    pass

class CountBO(BaseModel):
    count: int=0
    manufacturer: str=''

@stats_router.get('/manufacturer')
async def stats_manufacturer():
    with SqlSession() as session:
        list = session.fetchall(
            select(sqlm_keyboard_switch.c.manufacturer, func.count(sqlm_keyboard_switch.c.name).label('count'))
            .where(sqlm_keyboard_switch.c.deleted==0)
            .group_by('manufacturer'),
            CountBO
        )
        return list

def count_stash():
    with SqlSession() as session:
        list = session.fetchall(
            select(sqlm_keyboard_switch.c.variation, sqlm_keyboard_switch.c.name, sqlm_keyboard_switch.c.stash)
            .where(sqlm_keyboard_switch.c.deleted==0),
            KeyboardSwitch
        )
        result = {}
        for item in list:
            _len = item.variation.strip().split(' ').__len__()
            if result.keys().__contains__(item.stash):
                result[item.stash] += _len
            else:
                result[item.stash] = _len
    return result