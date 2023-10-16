import base64
import json
import os
import time
from datetime import datetime
from typing import Optional
from urllib.parse import urlencode

import requests
from fastapi import FastAPI, Request, Form, Query
from pydantic.main import BaseModel
from sqlalchemy import select, insert, func, and_, or_
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, RedirectResponse, Response, JSONResponse
from starlette.routing import Mount

# from app.config.setting import log_path
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
import logging
from app import routes
from loguru import logger
import sys

from app.core.config import app_config
from app.core.database import SqlSession
from app.core.response import RedirectResponseWraper
from app.core.snowflake_id import id_worker
from app.model import KeyboardSwitch, Keyword, sqlm_keyboard_switch, sqlm_keyword

templates = Jinja2Templates(directory='front/templates')

def register_route(app):
    # app.include_router(routes.router, tags=['app'])
    app.mount('/js', StaticFiles(directory='front/js'), name='js')
    app.mount('/css', StaticFiles(directory='front/css'), name='css')
    app.mount('/plugins', StaticFiles(directory='front/plugins'), name='plugins')
    app.mount('/img', StaticFiles(directory='front/img'), name='img')
# app.mount('/fonts', StaticFiles(directory='front/fonts'), name='fonts')
    logger.debug('route_provider registering')
    if app.debug:
        for route in app.routes:
            if type(route) == Mount:
                logger.info({'path': route.path, 'name': route.name})
            else:
                logger.info({'path': route.path, 'name': route.name, 'methods': route.methods})

def register_logging(app):
    pass
    # logging.getLogger().handlers = [InterceptHandler()]
    # logger.configure(
    #     handlers=[{'sink': sys.stdout, 'level': logging.DEBUG}]
    # )
    # if not os.path.exists(log_path):
    #     os.mkdir(log_path)
    # log_file = '{0}/web-{1}.log'.format(log_path, datetime.now().strftime('%Y%m%d'))
    # logger.add(log_file, encoding='utf-8', rotation='500MB', retention='6 months', enqueue=True)
    # logger.debug('logging_provider registering')
    # logging.getLogger('uvicorn.access').handlers = [InterceptHandler()]
    # logging.getLogger('peewee').handlers = [InterceptHandler()]
    # logging.getLogger('sqlalchemy')

def register_app(app):
    logger.debug('app_provider registering')
    app.add_middleware(CORSMiddleware, allow_origins=["*"],
                       allow_credentials=True,
                       allow_methods=["*"],
                       allow_headers=["*"])

def init_app():
    app = FastAPI(title='文档', description='描述demo', docs_url='/docs', debug=True)
    register_logging(app)
    register_app(app)
    register_route(app)
    return app

app = init_app()

@app.middleware('http')
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers['X-Process-Time'] = str(process_time)
    return response

@app.middleware('http')
async def del_blank_str_query_param(request: Request, call_next):
    q_params = {}
    query_params = request.query_params
    for k in query_params.keys():
        v = query_params.get(k)
        if v != '':
            q_params[k] = v
    request.scope['query_string'] = urlencode(q_params).encode('utf-8')
    # print(str(request.scope))
    response = await call_next(request)
    return response


@app.get("/", response_class=HTMLResponse)
async def index():
    return RedirectResponseWraper(url='/p/mkslist', status_code=status.HTTP_302_FOUND)

@app.get('/p/mkslist', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse('index.html', context={'request': request})

@app.get("/p/mks", response_class=HTMLResponse)
async def index(request: Request, id: Optional[int]=None):
    with SqlSession() as session:
        if id is not None:
            model = session.fetchone(
                select(sqlm_keyboard_switch).where(sqlm_keyboard_switch.columns.id==id), KeyboardSwitch
            )
        else:
            model = KeyboardSwitch(name='')
        switch_types = session.fetchall(
            select(sqlm_keyword).where(sqlm_keyword.columns.type=='switch_type'),
            Keyword
        )
        manufacturers = session.fetchall(
            select(sqlm_keyword).where(sqlm_keyword.columns.type=='manufacturer'),
            Keyword
        )
    return templates.TemplateResponse('add.html', context={'request': request, 'keyboard_switch': model, 'switch_types': switch_types, 'manufacturers': manufacturers, 'error_msg': []})

@app.get('/api/mkslist')
async def axlist(draw: Optional[int]=None, start: Optional[int]=1, length: Optional[int]=10, search: str=Query(alias='s', default=None)):
    with SqlSession() as session:
        stmt_list = select(sqlm_keyboard_switch).offset(start).limit(length)
        stmt_count = select(func.count(sqlm_keyboard_switch.columns.id))
        if search is not None:
            s = '%' + search + '%'
            search_expression = and_(
                or_(
                    sqlm_keyboard_switch.columns.name.like(s),
                    sqlm_keyboard_switch.columns.studio.like(s),
                    sqlm_keyboard_switch.columns.manufacturer.like(s),
                    sqlm_keyboard_switch.columns.tag.like(s)
                )
            )
            stmt_list = stmt_list.where(search_expression)
            stmt_count = stmt_count.where(search_expression)
        list = session.fetchall(stmt_list, KeyboardSwitch)
        total = session.count(stmt_count)
    return {'draw': draw, 'page_list': list, 'recordsTotal': total, 'recordsFiltered': total}

@app.get("/add1", response_class=HTMLResponse)
async def index(request: Request, axial: Optional[str]=None):
    if axial is not None:
        # ax = json.loads(axial)
        a = base64.b64decode(axial)
        ax = json.loads(a)
    else:
        ax = None
    return templates.TemplateResponse('add.html', context={'request': request, 'axial': ax, 'error_msg': []})

class DownloadRequest(BaseModel):
    url: str
@app.post('/api/download_pic', response_class=JSONResponse)
async def download_pic(req: DownloadRequest):
    temp_image_id = id_worker.next_id()
    response = requests.get(req.url)
    with open(app_config.temp_dir + temp_image_id + '.jpg', 'wb') as f:
        f.write(response.content)
    return {'status': 'ok'}

@app.post("/api/mks", response_class=HTMLResponse)
async def add(request: Request, name=Form(None), studio=Form(None), foundry=Form(None), type=Form(None),
              pic=Form(None), remark=Form(None),
              operating_force=Form(None), pre_travel=Form(None), end_force=Form(None), full_travel=Form(None),
              upper=Form(None), bottom=Form(None), shaft=Form(None), light_pipe=Form(None),
              price=Form(None), desc=Form(None)):
    now = datetime.now().timestamp()
    id = id_worker.next_id()
    keyboard_switch = KeyboardSwitch(
        name=name, studio=studio, foundry=foundry, type=type,
        pic=pic, remark=remark,
        operating_force=operating_force, pre_travel=pre_travel, end_force=end_force, full_travel=full_travel,
        upper=upper, bottom=bottom, shaft=shaft, light_pipe=light_pipe,
        price=price, desc=desc,
        create_time=now, update_time=now, id=id
    )
    with SqlSession() as session:
        ax = session.fetchone(
            select(sqlm_keyboard_switch).where(sqlm_keyboard_switch.columns.name==keyboard_switch.name),
            KeyboardSwitch
        )
        if ax is not None:
            pass
            # headers = {'Location': '/add1'}
            # return Response(content={
            #     'axial': '222'
            # }, headers=headers, status_code=status.HTTP_302_FOUND)
            return RedirectResponseWraper(url='/add1', status_code=status.HTTP_302_FOUND, query={
                'axial': ax
            })
        else:
            pass
        # session.execute(
        #     insert()
        # )
        pass
    print(name)
    return RedirectResponse(url='/', status_code=302)


import uvicorn

if __name__ == '__main__':
    uvicorn.run('application:app', host='0.0.0.0', port=8001, access_log=True)