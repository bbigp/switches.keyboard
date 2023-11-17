from fastapi import APIRouter
from pydantic.main import BaseModel
from sqlalchemy import func, select

from app.core.database import SqlSession
from app.model.domain import sqlm_keyboard_switch

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
            .group_by('manufacturer'),
            CountBO
        )
        return list