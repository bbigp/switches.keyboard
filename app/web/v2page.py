import os.path
from typing import Optional

from fastapi import Request, Form, APIRouter
from sqlalchemy import select, func, desc, text
from starlette import status
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from app import crud
from app.core.config import app_config
from app.core.database import SqlSession
from app.core.internal import paginate_info
from app.core.response import RedirectResponseWraper
from app.crud import switches_mapper, keyword_mapper
from app.model.assembler import convert_vo
from app.model.domain import sqlm_keyboard_switch, KeyboardSwitch, sqlm_keyword, Keyword, Switches, KeyCountBO
from app.model.vo import MksVO, Specs, KeywordVO
from app.web import api
from app.web.stats import count_stash

templates = Jinja2Templates(directory='ui/v2')

v2_page_router = APIRouter(prefix='')

def format_with_tolerance(value):
    base_value, tolerance, unit = value
    if base_value is None or base_value == '':
        return '-'
    elif tolerance is None or tolerance == '':
        return f'{base_value}{unit}'
    else:
        return f'{base_value}{tolerance}{unit}'

def format_studio_with_manufacturer(value):
    studio, manufacturer = value
    if studio and manufacturer:
        if studio == manufacturer:
            return f'{studio}'
        else:
            return f'{studio} | {manufacturer}'
    elif studio or manufacturer:
        return f'{studio}{manufacturer}'
    else:
        return ''

templates.env.filters['format_with_tolerance'] = format_with_tolerance
templates.env.filters['format_studio_with_manufacturer'] = format_studio_with_manufacturer

@v2_page_router.get("/control", response_class=HTMLResponse)
@v2_page_router.get('/control/main', response_class=HTMLResponse)
async def index(request: Request):
    with SqlSession() as session:
        box_list = get_keyword_counts(session, 'stor_loc_box')
        t = session.count(switches_mapper.count())
    return templates.TemplateResponse('switches-list.html', context={'request': request, 'total': t, 'box_list': box_list})


def get_keyword_counts(sql_session, type, offset=None, limit=None, search=None):
    key_count_list = sql_session.fetchall(switches_mapper.group_by_type(type), KeyCountBO)
    count_detail_map = {}
    for count_detail in key_count_list:
        count_detail_map[count_detail.key] = count_detail.count

    keywords = sql_session.fetchall(keyword_mapper.list_by_type(type, offset, limit, search), KeywordVO)
    for model in keywords:
        model.count = count_detail_map[model.word] if count_detail_map.keys().__contains__(model.word) else 0
    return keywords


@v2_page_router.get("/control/switches", response_class=HTMLResponse)
@v2_page_router.get("/control/switches/{id}", response_class=HTMLResponse)
async def index(request: Request, id: Optional[int]=None):
    with SqlSession() as session:
        switches = Switches(name='', studio='')
        if id is not None:
            switches = session.fetchone(switches_mapper.get_by_id(id), Switches)
        list = session.fetchall(keyword_mapper.list_by_types(['switch_type', 'manufacturer', 'mark', 'studio']),
            KeywordVO
        )
        switch_types = []
        manufacturers = []
        stor_loc_boxs = get_keyword_counts(session, 'stor_loc_box')
        marks = []
        studios = []
        for item in list:
            if item.type == 'switch_type':
                switch_types.append(item)
            elif item.type == 'manufacturer':
                manufacturers.append(item)
            elif item.type == 'logo':
                marks.append(item.word)
            elif item.type == 'studio':
                studios.append(item.word)
            else:
                pass
    return templates.TemplateResponse('switches.html', context={
        'request': request,
        'switches': switches,
        'switch_types': switch_types,
        'manufacturers': manufacturers,
        'stor_loc_boxs': stor_loc_boxs,
        'marks': marks,
        'studios': studios,
        'error_msg': []
    })

@v2_page_router.get("/control/keyword", response_class=HTMLResponse)
async def keyword(request: Request):
    return templates.TemplateResponse('keyword.html', context={'request': request})


@v2_page_router.get("/")
@v2_page_router.get("/main")
@v2_page_router.get('/main/{page}')
async def dev(
        request: Request,
        page: Optional[int]=1,
        size: Optional[int]=15
):
    with SqlSession() as session:
        stmt_list, stmt_count = switches_mapper.filter((page - 1) * size, size, None, None, None, True)
        list = session.fetchall(stmt_list, Switches)
        total = session.count(stmt_count)
        manufacturers = session.fetchall(keyword_mapper.list_by_type('manufacturer'), Keyword)
    return templates.TemplateResponse('dev.html', context={
        'request': request,
        'list': [convert_vo(i) for i in list],
        'page': paginate_info(total, page, size),
        'manufacturers': manufacturers
    })
