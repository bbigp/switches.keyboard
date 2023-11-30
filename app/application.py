import time
from urllib.parse import urlencode

from fastapi import FastAPI, Request
from loguru import logger
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

from app.core.response import RedirectResponseWraper
from app.web.api import api_router
from app.web.page import page_router, templates
from app.web.pic import pic_router
from app.web.stats import stats_router



def register_route(app):
    app.include_router(stats_router, tags=['stats_router'])
    app.include_router(pic_router, tags=['pic_router'])
    app.include_router(page_router, tags=['page_router'])
    app.include_router(api_router, tags=['api_router'])
    app.mount('/js', StaticFiles(directory='front/js'), name='js')
    app.mount('/css', StaticFiles(directory='front/css'), name='css')
    app.mount('/plugins', StaticFiles(directory='front/plugins'), name='plugins')
    app.mount('/img', StaticFiles(directory='front/img'), name='img')
    app.mount('/images', StaticFiles(directory='front/images'), name='images')
    app.mount('/fonts', StaticFiles(directory='front/fonts'), name='fonts')
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

@app.exception_handler(AttributeError)
@app.exception_handler(ValueError)
async def exception_handler(request: Request, e):
    logger.error(e)
    msg = str(e.args[0])
    msg = msg if len(msg) <= 100 else str(msg[0:100])
    return JSONResponse(status_code=200, content={'status': 'error', 'msg': msg})

@app.get("/", response_class=HTMLResponse)
async def index():
    return RedirectResponseWraper(url='/p/mkslist', status_code=status.HTTP_302_FOUND)

@app.get("/test", response_class=HTMLResponse)
async def test(request: Request):
    return templates.TemplateResponse('layout.html', context={'request': request})
