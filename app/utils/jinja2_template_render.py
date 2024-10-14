import gzip
import os
import re
from typing import Optional

from fastapi import Query, Depends
from jinja2 import FileSystemLoader, Environment
from starlette.requests import Request

from app.core.database import SqlSession
from app.core.internal import paginate_info
from app.crud import switches_mapper, keyword_mapper
from app.model.assembler import convert_vo
from app.model.domain import Switches
from app.utils.jinja2_filters import format_with_tolerance, format_studio_with_manufacturer


template_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'ui', 'v2')
env = Environment(loader=FileSystemLoader(template_path))
env.filters['format_with_tolerance'] = format_with_tolerance
env.filters['format_studio_with_manufacturer'] = format_studio_with_manufacturer

def determine_page_size(request: Request, size: int=Query(None)) -> int:
    user_agent = request.headers.get("User-Agent", "")
    if size is not None:
        return size
    mobile_pattern = re.compile(r"Mobi|Android|iPhone|iPad|iPod|Windows Phone", re.I)
    return 8 if bool(mobile_pattern.search(user_agent)) else 15

def render_switches_wrapper(session, page: Optional[int]=1,
        size: int=Depends(determine_page_size),
        search: str=Query(default=None, alias='s'),
        type: str=Query(default=None, alias='t'),
        stor_box: Optional[str]=None,
        manufacturer: Optional[str]=None,
        is_available: Optional[int]=1):
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

    template = env.get_template('new/switches_wrapper.html')
    rendered_html = template.render(list=[convert_vo(i).dict() for i in list],
        page=paginate_info(total, page, size), search=search)
    return rendered_html
    # compressed_content = gzip.compress(rendered_html.encode('utf-8'))
    # return compressed_content

def render_switches_filter(session, request: Request):
    types, manufacturers, _, studios = keyword_mapper.fetch_text(session)
    template = env.get_template('new/switches_filter.html')
    return template.render(request=request, manufacturers=manufacturers, switches_types=types)