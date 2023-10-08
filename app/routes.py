# import os
# import shutil
# from datetime import datetime
# from typing import Optional
# from urllib import parse
# from urllib.parse import urlparse
#
# from fastapi import APIRouter, Depends
# from loguru import logger
# from starlette.requests import Request
# from starlette.responses import HTMLResponse
# from yt_dlp import version
#
# from app.application import templates
#
# router = APIRouter(prefix='')
#
# @router.get("/", response_class=HTMLResponse)
# async def index(request: Request):
#     return templates.TemplateResponse('index.html', context={'request': request})