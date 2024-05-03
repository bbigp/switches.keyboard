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
from app.crud import switches_mapper
from app.model.assembler import convert_vo
from app.model.domain import sqlm_keyboard_switch, KeyboardSwitch, sqlm_keyword, Keyword
from app.model.vo import MksVO, Specs, KeywordVO
from app.web import api
from app.web.stats import count_stash

templates = Jinja2Templates(directory='ui/templates')

page_router = APIRouter(prefix='')

def format_with_tolerance(value):
    base_value, tolerance, unit = value
    if base_value is None or base_value == '':
        return '-'
    elif tolerance is None or tolerance == '':
        return f'{base_value}{unit}'
    else:
        return f'{base_value}±{tolerance}{unit}'

def format_studio_with_manufacturer(value):
    studio, manufacturer = value
    if studio and manufacturer:
        return f'{studio} | {manufacturer}'
    elif studio or manufacturer:
        return f'{studio}{manufacturer}'
    else:
        return ''

templates.env.filters['format_with_tolerance'] = format_with_tolerance
templates.env.filters['format_studio_with_manufacturer'] = format_studio_with_manufacturer

@page_router.get('/dash/mkslist', response_class=HTMLResponse)
async def index(request: Request):
    with SqlSession() as session:
        stashlist = list_stash(session)
        t = session.count(select(func.count(sqlm_keyboard_switch.c.id)).where(sqlm_keyboard_switch.c.deleted==0))
    return templates.TemplateResponse('switches-list.html', context={'request': request, 'total': t, 'stashlist': stashlist})

def list_stash(session):
    stashlist = session.fetchall(
        select(sqlm_keyword)
            .where(sqlm_keyword.c.deleted==0, sqlm_keyword.c.type=='stash')
            .order_by(desc(sqlm_keyword.c.update_time)),
        KeywordVO
    )
    scount = count_stash()
    for item in stashlist:
        item.count = scount[item.word] if scount.keys().__contains__(item.word) else 0
    return stashlist

def list_image(path):
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    latest_files = sorted(files)[-20:]
    return latest_files[::-1]



@page_router.get("/dash/mks", response_class=HTMLResponse)
@page_router.get("/dash/mks/{id}", response_class=HTMLResponse)
async def index(request: Request, id: Optional[int]=None):
    with SqlSession() as session:
        if id is not None:
            model = session.fetchone(
                select(sqlm_keyboard_switch).where(sqlm_keyboard_switch.columns.id==id), KeyboardSwitch
            )
            mks = convert_vo(model) if model is not None else MksVO(name='')
        else:
            mks = MksVO(name='', specs=Specs())
        list = session.fetchall(
            select(sqlm_keyword)
                .where(sqlm_keyword.c.deleted==0, sqlm_keyword.c.type.in_(['switch_type', 'manufacturer', 'stash', 'logo', 'studio']))
                .order_by(desc(sqlm_keyword.c.update_time)),
            KeywordVO
        )
        scount = count_stash()
        switch_types = []
        manufacturers = []
        stashs = []
        logos = []
        studios = []
        for item in list:
            if item.type == 'switch_type':
                switch_types.append(item)
            elif item.type == 'manufacturer':
                manufacturers.append(item)
            elif item.type == 'stash':
                item.count = scount[item.word] if scount.keys().__contains__(item.word) else 0
                stashs.append(item)
            elif item.type == 'logo':
                logos.append(item.word)
            elif item.type == 'studio':
                studios.append(item.word)
            else:
                pass
    images = list_image(app_config.temp_dir)
    return templates.TemplateResponse('switches.html', context={
        'request': request,
        'keyboard_switch': mks,
        'switch_types': switch_types,
        'manufacturers': manufacturers,
        'switch_stashs': stashs,
        'logos': logos,
        'studios': studios,
        'error_msg': [],
        'images': images
    })

@page_router.get("/dash/keyword", response_class=HTMLResponse)
async def keyword(request: Request):
    return templates.TemplateResponse('keyword.html', context={'request': request})

@page_router.get('/dash/stash', response_class=HTMLResponse)
async def stash(request: Request):
    with SqlSession() as session:
        stashlist = list_stash(session)
    return templates.TemplateResponse('stash.html', context={'request': request, 'stashlist': stashlist})

@page_router.get('/test')
async def mx_switches_list(request: Request):
    with SqlSession() as session:
        stashlist = list_stash(session)
    return templates.TemplateResponse('mx/switches-list.html', context={'request': request})

@page_router.get("/")
@page_router.get("/dev")
@page_router.get('/dev/{page}')
async def dev(
        request: Request,
        page: Optional[int]=1,
        size: Optional[int]=15
):
    with SqlSession() as session:
        stmt_list, stmt_count = switches_mapper.filter((page - 1) * size, size, None, None, None, True)
        list = session.fetchall(stmt_list, KeyboardSwitch)
        total = session.count(stmt_count)
        manufacturers = session.fetchall(
            text('select * from keyword where deleted = 0 and type = :type').bindparams(type='manufacturer'),
            Keyword
        )
    return templates.TemplateResponse('dev.html', context={
        'request': request,
        'list': [convert_vo(i) for i in list],
        'page': paginate_info(total, page, size),
        'manufacturers': manufacturers
    })


async def add(request: Request, name=Form(None), studio=Form(None), foundry=Form(None), type=Form(None),
              pic=Form(None), remark=Form(None),
              operating_force=Form(None), pre_travel=Form(None), end_force=Form(None), full_travel=Form(None),
              upper=Form(None), bottom=Form(None), shaft=Form(None), light_pipe=Form(None),
              price=Form(None), desc=Form(None)):
    # headers = {'Location': '/add1'}
    # return Response(content={
    #     'axial': '222'
    # }, headers=headers, status_code=status.HTTP_302_FOUND)
    return RedirectResponseWraper(url='/add1', status_code=status.HTTP_302_FOUND, query={'axial': {}})
