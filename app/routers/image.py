import os
from datetime import datetime

from fastapi import Query, APIRouter
from starlette.responses import StreamingResponse, FileResponse

from app.config import app_config
from app.core.internal import gen_white_image, ImageProcessor

image_router = APIRouter()

# x-oss-process=image/resize,m_fixed,h_100,w_100
@image_router.get('/bfs/{source}/{path}', response_class=FileResponse)
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

