from typing import Optional

from fastapi import Request, Form, APIRouter
from sqlalchemy import select
from starlette import status
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from app.core.database import SqlSession
from app.core.response import RedirectResponseWraper
from app.model.assembler import convert_vo
from app.model.domain import sqlm_keyboard_switch, KeyboardSwitch, sqlm_keyword, Keyword
from app.model.vo import MksVO, Specs

templates = Jinja2Templates(directory='front/templates')

page_router = APIRouter(prefix='/p')

@page_router.get('/mkslist', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse('index.html', context={'request': request})

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
            select(sqlm_keyword).where(sqlm_keyword.c.deleted==0, sqlm_keyword.c.type.in_(['switch_type', 'manufacturer', 'stash'])),
            Keyword
        )
        switch_types = []
        manufacturers = []
        stashs = []
        for item in list:
            if item.type == 'switch_type':
                switch_types.append(item)
            elif item.type == 'manufacturer':
                manufacturers.append(item)
            elif item.type == 'stash':
                stashs.append(item)
            else:
                pass
    return templates.TemplateResponse('add.html', context={
        'request': request,
        'keyboard_switch': mks,
        'switch_types': switch_types,
        'manufacturers': manufacturers,
        'switch_stashs': stashs,
        'error_msg': []
    })

@page_router.get("/keyword", response_class=HTMLResponse)
async def keyword(request: Request):
    return templates.TemplateResponse('keyword.html', context={'request': request})


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
