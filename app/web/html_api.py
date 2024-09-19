import gzip
import os
from typing import Optional

from fastapi import APIRouter
from jinja2 import Environment, FileSystemLoader
from starlette.requests import Request
from starlette.responses import Response

from app.core.database import SqlSession
from app.crud import switches_mapper
from app.model.domain import Switches
from app.web.v2page import generate_2d_array

html_api_router = APIRouter(prefix='/apih')
template_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'ui', 'v2')
env = Environment(loader=FileSystemLoader(template_path))

@html_api_router.get('/keyboard')
async def keyboard(request: Request, s:Optional[str] = 'D.1'):
    with SqlSession() as session:
        stmt_list, _ = switches_mapper.filter(start=0, length=1000, stor_box=s)
        list = session.fetchall(stmt_list, Switches)
        array_2d = generate_2d_array(list)
        template = env.get_template('new/keyboard-table.html')

    rendered_html = template.render(request=request, data=array_2d)
    compressed_content = gzip.compress(rendered_html.encode('utf-8'))
    return Response(content=compressed_content, headers={"Content-Encoding": "gzip"}, media_type="text/html")

