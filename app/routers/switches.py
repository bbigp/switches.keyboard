from datetime import datetime, timedelta
from typing import Optional, List, Dict

from fastapi import Request, APIRouter, Query, Depends
from fastapi.encoders import jsonable_encoder
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from app.core.database import SqlSession
from app.core.internal import paginate_info, get_month_start_end
from app.crud import switches_mapper, keyword_mapper, icgb_mapper, board_mapper
from app.model.assembler import convert_vo
from app.model.domain import Keyword, Switches, KeyCountBO, \
    Icgb
from app.model.vo import KeywordVO, CalendarVO
from app.utils.jinja2_filters import format_with_tolerance, format_studio_with_manufacturer
from app.utils.jinja2_template_render import render_switches_wrapper, determine_page_size, render_switches_filter

templates = Jinja2Templates(directory='ui/v2')
templates.env.filters['format_with_tolerance'] = format_with_tolerance
templates.env.filters['format_studio_with_manufacturer'] = format_studio_with_manufacturer

v2_page_router = APIRouter(prefix='')





@v2_page_router.get('/control/ig')
async def ayb(request: Request,):
    yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    with SqlSession() as session:
        list = session.fetchall(icgb_mapper.list_by_day(day=yesterday), Icgb)
        days = session.fetchall(icgb_mapper.list_day(), Icgb)
        if len(list) <= 0:
            icgblist, day = icgb_mapper.gen_icgb(0)
            if len(icgblist) > 0:
                session.execute(icgb_mapper.batch_save_or_update(icgblist))
                list = session.fetchall(icgb_mapper.list_by_day(day=day), Icgb)
            else:
                list = [Icgb(title=day)]
    return templates.TemplateResponse('c-ig.html', context={
        'request': request,
        'list': list,
        'day': day if len(list) <= 0 else yesterday,
        'days': jsonable_encoder([d.day for d in days])
    })

@v2_page_router.get('/control/sqlite')
async def sqlite(request: Request):
    return templates.TemplateResponse('sqlite.html', context={
        'request': request,
    })

@v2_page_router.get('/control/board')
async def keyboard(request:Request):
    with SqlSession() as session:
        list = switches_mapper.list(session)
        refs = board_mapper.fetch_all_ref(session=session)
        array_2d = []
        if len(refs) > 0:
            array_2d = board_mapper.fetch_2d_array_by_ref(session=session, ref=refs[0])
    return templates.TemplateResponse('keyboard.html', context={
        'request': request,
        'list': [s.name for s in list],
        'stor_boxs': refs,
        'data': array_2d,
    })

@v2_page_router.get('/collections/products/{id}')
async def detail(request: Request, id: int):
    with SqlSession() as session:
        model = session.fetchone(switches_mapper.get_by_id(id), Switches)
    return templates.TemplateResponse('collections-products.html', context={
        'request': request,
        'switch': convert_vo(model).dict()
    })




