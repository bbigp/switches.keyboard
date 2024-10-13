import gzip
from typing import Optional

from fastapi import APIRouter, Depends, Query
from starlette.requests import Request
from starlette.responses import Response

from app.core.database import SqlSession
from app.crud import board_mapper
from app.utils.jinja2_template_render import render_switches_wrapper, env, determine_page_size, render_switches_filter

html_api_router = APIRouter(prefix='/apih')


@html_api_router.get('/keyboard')
async def keyboard(request: Request, s:Optional[str] = None):
    with SqlSession() as session:
        array_2d = board_mapper.fetch_2d_array_by_ref(session=session, ref=s)
    template = env.get_template('new/keyboard-table.html')
    rendered_html = template.render(request=request, data=array_2d)
    compressed_content = gzip.compress(rendered_html.encode('utf-8'))
    return Response(content=compressed_content, headers={"Content-Encoding": "gzip"}, media_type="text/html")

@html_api_router.get("/filter/switches")
async def filter_switches(request: Request, page: Optional[int]=1,
        size: int=Depends(determine_page_size),
        search: str=Query(default=None, alias='s'),
        type: str=Query(default=None, alias='t'),
        stor_box: Optional[str]=None,
        manufacturer: Optional[str]=None,
        is_available: Optional[int]=1):
    with SqlSession() as session:
        switches_wrapper = render_switches_wrapper(session, page, size, search, type, stor_box, manufacturer, is_available)
        switches_filter = render_switches_filter(session, request)
        compressed_content = gzip.compress((switches_wrapper + '<!--SPLIT-->' + switches_filter).encode('utf-8'))
    return Response(content=compressed_content, headers={"Content-Encoding": "gzip"}, media_type="text/html")



