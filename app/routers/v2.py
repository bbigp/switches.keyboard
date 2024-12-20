import gzip
from typing import Optional

from fastapi import Query, Depends, APIRouter
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.database import SqlSession
from app.service import icgb_mapper, board_mapper
from app.model.domain import Icgb
from app.model.vo import CalendarVO
from app.utils.jinja2_template_render import env, determine_page_size, render_switches_wrapper, render_switches_filter, \
    render_studios

api_router = APIRouter()

@api_router.get('/api/v2/icgb/calendar_events', response_class=JSONResponse)
async def calendar_events(start: str, end: str):
    with SqlSession() as session:
        list = session.fetchall(icgb_mapper.list_by_time(start, end), Icgb)
        events = [CalendarVO(title=data.title, start=data.icgb_day, end=data.icgb_day, url=data.href) for data in list]
    return {'page_list': events}


@api_router.get('/apih/keyboard')
async def keyboard(request: Request, s:Optional[str] = None):
    with SqlSession() as session:
        array_2d = board_mapper.fetch_2d_array_by_ref(session=session, ref=s)
    template = env.get_template('new/keyboard-table.html')
    rendered_html = template.render(request=request, data=array_2d)
    compressed_content = gzip.compress(rendered_html.encode('utf-8'))
    return Response(content=compressed_content, headers={"Content-Encoding": "gzip"}, media_type="text/html")

@api_router.get('/apih/filter/switches')
async def filter_switches(request: Request, page: Optional[int]=1,
                          size: int=Depends(determine_page_size),
                          search: str=Query(default=None, alias='s'),
                          type: str=Query(default=None, alias='t'),
                          stor_box: Optional[str]=None,
                          manufacturer: Optional[str]=None,
                          is_available: Optional[int]=1,
                          studio: Optional[str]=None,
                          stem: Optional[str]=None,
                          top_mat: Optional[str]=None,
                          bottom_mat: Optional[str]=None,
                          min_travel: Optional[int] = None,
                          max_travel: Optional[int] = None,
                          min_total_travel: Optional[int] = None,
                          max_total_travel: Optional[int] = None,
                          min_force: Optional[int] = None,
                          max_force: Optional[int] = None,
                          min_total_force: Optional[int] = None,
                          max_total_force: Optional[int] = None
                          ):
    with SqlSession() as session:
        switches_wrapper = render_switches_wrapper(session, page, size, search, type, stor_box,
                                                   manufacturer, is_available, studio, stem=stem,
                                                   top_mat=top_mat, bottom_mat=bottom_mat,
                                                   min_travel=min_travel, max_travel=max_travel,
                                                   min_total_travel=min_total_travel, max_total_travel=max_total_travel,
                                                   min_force=min_force, max_force=max_force,
                                                   min_total_force=min_total_force, max_total_force=max_total_force)
        switches_filter = render_switches_filter(session, request)
        compressed_content = gzip.compress((switches_wrapper + '<!--SPLIT-->' + switches_filter).encode('utf-8'))
    return Response(content=compressed_content, headers={"Content-Encoding": "gzip"}, media_type="text/html")


@api_router.get('/apih/filter/studios')
async def filter_studios(request: Request, page: Optional[int]=1,
                         size: Optional[int]=100,
                         search: Optional[str]=None):
    with SqlSession() as session:
        rendered_html = render_studios(session, request)
        compressed_content = gzip.compress(rendered_html.encode('utf-8'))
    return Response(content=compressed_content, headers={"Content-Encoding": "gzip"}, media_type="text/html")

