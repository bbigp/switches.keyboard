import mimetypes
import os
import shutil
from datetime import datetime

from aiohttp import ClientSession
from fastapi import APIRouter, UploadFile, Query
from pydantic.main import BaseModel
from starlette.responses import FileResponse, JSONResponse, StreamingResponse

from app.core.config import app_config
from app.core.internal import ImageProcessor, gen_white_image
from app.core.snowflake_id import id_worker

pic_router = APIRouter(prefix='')

class DownloadRequest(BaseModel):
    url: str

@pic_router.post('/api/direct_use_pic', response_class=JSONResponse)
async def direct_use(req: DownloadRequest):
    if not req.url.startswith('/bfs/t/'):
        return {'status': 'error', 'mgs': '非法链接'}
    u = req.url.replace('/bfs/t/', '')
    _from = app_config.temp_dir + u
    temp_image_id = str(id_worker.next_id())
    _to = app_config.file_dir + temp_image_id + '.jpg'
    shutil.copy(_from, _to)
    return {'status': 'ok', 'data': '/bfs/fs/' + temp_image_id + '.jpg' }

@pic_router.post('/api/download_pic', response_class=JSONResponse)
async def download_pic(req: DownloadRequest):
    temp_image_id = str(id_worker.next_id())
    # https://blog.csdn.net/e5pool/article/details/131014343  https://blog.csdn.net/wq10_12/article/details/133944658 使用代理
    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'}
    async with ClientSession(headers=headers) as session:
        async with session.get(req.url) as response:
            with open(app_config.temp_dir + temp_image_id + '.jpg', 'wb') as f:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    f.write(chunk)
    return {'status': 'ok', 'data': '/bfs/t/' + temp_image_id + '.jpg' }

@pic_router.post('/api/upload_pic')
async def upload_pic(image: UploadFile):
    image_id = str(id_worker.next_id())
    with open(app_config.file_dir + image_id + '.jpg', 'wb') as f:
        f.write(await image.read())
    return {'status': 'ok', 'data': '/bfs/fs/' + image_id + '.jpg'}

@pic_router.post('/api/upload_temp_pic')
async def upload_pic(image: UploadFile):
    image_id = str(id_worker.next_id())
    with open(app_config.temp_dir + image_id + '.jpg', 'wb') as f:
        f.write(await image.read())
    return {'status': 'ok', 'data': '/bfs/t/' + image_id + '.jpg'}

@pic_router.get('/api/page_temp_image')
async def page_temp_image():
    path = app_config.temp_dir
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    latest_files = sorted(files)[-20:]
    return latest_files[::-1]

# x-oss-process=image/resize,m_fixed,h_100,w_100
@pic_router.get('/bfs/{source}/{path}', response_class=FileResponse)
async def show_pic(path: str, source: str, process: str=Query(None, alias='x-process')):
    if source == 't':
        full_path = app_config.temp_dir + path
    elif source == 'fs':
        full_path = app_config.file_dir + path
    else:
        full_path = ''
    if not os.path.isfile(full_path):
        return StreamingResponse(gen_white_image(), media_type='image/png', headers={'Etag': str(datetime.now().timestamp())})
    if not process:
        return FileResponse(full_path, media_type='image/jpg')
    thumbnail_path = ImageProcessor(process).process(full_path, app_config.image_cache_path)
    return FileResponse(thumbnail_path, media_type='image/webp')

# 应用评分规则里边新增了云安全巡检项项，在我的抖店云控制台，安全风控中心里，有一项中危任务：检测公网IP有没有绑定ECS，给出的整改步骤https://op.jinritemai.com/docs/guide-docs/1469/6337?from=list&docLabel=
# 点击页面上的CLB用户指南 之后，将我定位
