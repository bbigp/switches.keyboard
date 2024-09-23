import gzip
import os
from typing import Optional

from fastapi import APIRouter, Depends, Query
from jinja2 import Environment, FileSystemLoader
from starlette.requests import Request
from starlette.responses import Response

from app.core.database import SqlSession
from app.core.internal import paginate_info
from app.crud import switches_mapper, board_mapper
from app.model.assembler import convert_vo
from app.model.domain import Switches
from app.web.v2page import determine_page_size

html_api_router = APIRouter(prefix='/apih')
template_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'ui', 'v2')
env = Environment(loader=FileSystemLoader(template_path))

@html_api_router.get('/keyboard')
async def keyboard(request: Request, s:Optional[str] = None):
    with SqlSession() as session:
        array_2d = board_mapper.fetch_2d_array_by_ref(session=session, ref=s)
    template = env.get_template('new/keyboard-table.html')
    rendered_html = template.render(request=request, data=array_2d)
    compressed_content = gzip.compress(rendered_html.encode('utf-8'))
    return Response(content=compressed_content, headers={"Content-Encoding": "gzip"}, media_type="text/html")

@html_api_router.get("filter/switches")
async def filter_switches(request: Request, page: Optional[int]=1,
        size: int=Depends(determine_page_size),
        search: str=Query(default=None, alias='s'),
        type: str=Query(default=None, alias='t'),
        stor_box: Optional[str]=None,
        manufacturer: Optional[str]=None,
        is_available: Optional[int]=1):
    with SqlSession() as session:
        if is_available == 1:
            available = True
        elif is_available == 2:
            available = False
        else:
            available = None
        stmt_list, stmt_count = switches_mapper.filter((page - 1) * size, size, search, stor_box, manufacturer,
                                                       available, type=type)
        list = session.fetchall(stmt_list, Switches)
        total = session.count(stmt_count)

    template = env.get_template('new/keyboard-table.html')
    rendered_html = template.render(request=request, list=[convert_vo(i).dict() for i in list],
        page=paginate_info(total, page, size))
    compressed_content = gzip.compress(rendered_html.encode('utf-8'))
    return Response(content=compressed_content, headers={"Content-Encoding": "gzip"}, media_type="text/html")
