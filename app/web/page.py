from typing import Optional

from fastapi import Request, Form, APIRouter
from sqlalchemy import select, func, desc
from starlette import status
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from app.core.database import SqlSession
from app.core.response import RedirectResponseWraper
from app.model.assembler import convert_vo
from app.model.domain import sqlm_keyboard_switch, KeyboardSwitch, sqlm_keyword, Keyword
from app.model.vo import MksVO, Specs, KeywordVO
from app.web.stats import count_stash

templates = Jinja2Templates(directory='front/templates')

page_router = APIRouter(prefix='/p')

@page_router.get('/mkslist', response_class=HTMLResponse)
async def index(request: Request):
    with SqlSession() as session:
        t = session.count(select(func.count(sqlm_keyboard_switch.c.id)))
    return templates.TemplateResponse('switches-list.html', context={'request': request, 'total': t})

@page_router.get("/mks", response_class=HTMLResponse)
@page_router.get("/mks/{id}", response_class=HTMLResponse)
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
                item.count = scount[item.word]
                stashs.append(item)
            elif item.type == 'logo':
                logos.append(item.word)
            elif item.type == 'studio':
                studios.append(item.word)
            else:
                pass
    return templates.TemplateResponse('switches.html', context={
        'request': request,
        'keyboard_switch': mks,
        'switch_types': switch_types,
        'manufacturers': manufacturers,
        'switch_stashs': stashs,
        'logos': logos,
        'studios': studios,
        'error_msg': []
    })

@page_router.get("/keyword", response_class=HTMLResponse)
async def keyword(request: Request):
    return templates.TemplateResponse('keyword.html', context={'request': request})

@page_router.get('/test')
async def mx_switches_list(request: Request):
    return templates.TemplateResponse('mx/switches-list.html', context={'request': request})


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
