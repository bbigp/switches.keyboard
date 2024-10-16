# import uvicorn
#
# if __name__ == '__main__':
#     uvicorn.run('app.application:app', host='0.0.0.0', port=8002, access_log=True)

import json

from fastapi import FastAPI, Request
from loguru import logger
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

from app.config import options
from app.core.internal import convert_long_to_str
from app.routers.admin_api import admin_api_router
from app.routers.image import image_router
from app.routers.page import page_router, admin_page_router
from app.routers.v2 import api_router


def register_route(app):
    app.include_router(api_router)
    app.include_router(page_router)
    app.include_router(image_router)
    if options.is_master():
        app.include_router(admin_api_router)
        app.include_router(admin_page_router)
    app.mount('/js', StaticFiles(directory='ui/js'), name='js')
    app.mount('/assets', StaticFiles(directory='ui/assets'), name='assets')
    app.mount('/', StaticFiles(directory='ui/img'), name='rootImg')
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
    # log_file = '{0}/routers-{1}.log'.format(log_path, datetime.now().strftime('%Y%m%d'))
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

# @app.middleware('http')
# async def add_process_time_header(request: Request, call_next):
#     start_time = time.time()
#     response = await call_next(request)
#     process_time = time.time() - start_time
#     response.headers['X-Process-Time'] = str(process_time)
#     return response

# @app.middleware('http')
# async def del_blank_str_query_param(request: Request, call_next):
#     q_params = {}
#     query_params = request.query_params
#     for k in query_params.keys():
#         v = query_params.get(k)
#         if v != '':
#             q_params[k] = v
#     request.scope['query_string'] = urlencode(q_params).encode('utf-8')
#     # print(str(request.scope))
#     response = await call_next(request)
#     return response

@app.middleware("http")
async def convert_long_middleware(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.__contains__("api") and not request.url.path.__contains__('apih'):
        body = b"".join([chunk async for chunk in response.body_iterator])
        content = json.loads(body.decode("utf-8"))
        # 转换 long 类型数据为字符串
        content = convert_long_to_str(content)

        # 返回新的 JSONResponse
        return JSONResponse(content=content)
    return response

@app.exception_handler(AttributeError)
@app.exception_handler(ValueError)
async def exception_handler(request: Request, e):
    logger.error(e)
    msg = str(e.args[0])
    msg = msg if len(msg) <= 100 else str(msg[0:100])
    return JSONResponse(status_code=200, content={'status': 'error', 'msg': msg})
