from datetime import datetime, timedelta
from typing import Optional, List, Dict

from fastapi import Request, APIRouter, Query, Depends
from fastapi.encoders import jsonable_encoder
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from app.core.database import SqlSession
from app.core.internal import paginate_info, get_month_start_end
from app.crud import switches_mapper, keyword_mapper, icgb_mapper, board_mapper
from app.model.assembler import convert_vo
from app.model.domain import Keyword, Switches, KeyCountBO, \
    Icgb
from app.model.vo import KeywordVO, CalendarVO
from app.utils.jinja2_filters import format_with_tolerance, format_studio_with_manufacturer
from app.utils.jinja2_template_render import render_switches_wrapper, determine_page_size, render_switches_filter

templates = Jinja2Templates(directory='ui/v2')
templates.env.filters['format_with_tolerance'] = format_with_tolerance
templates.env.filters['format_studio_with_manufacturer'] = format_studio_with_manufacturer

main_router = APIRouter(prefix='')



@main_router.get("/")
@main_router.get('/collections')
@main_router.get("/collections/")
@main_router.get("/collections/switches")
@main_router.get("/collections/switches/")
@main_router.get("/collections/switches/{page}")
async def main(
        request: Request,
        page: Optional[int]=1,
        size: int=Depends(determine_page_size),
        search: str=Query(default=None, alias='s'),
        type: str=Query(default=None, alias='t'),
        stor_box: Optional[str]=None,
        manufacturer: Optional[str]=None,
        is_available: Optional[int]=1
):
    with SqlSession() as session:
        switches_wrapper = render_switches_wrapper(session, page, size, search, type, stor_box, manufacturer, is_available)
        switches_filter = render_switches_filter(session, request)
        hot_switches = switches_mapper.fetch_hot(session, size=3)
    return templates.TemplateResponse('collections-switches.html', context={
        'request': request,
        'switches_wrapper': switches_wrapper,
        'switches_filter': switches_filter,
        'hot_switches': hot_switches,
    })


@main_router.get('/icgb')
async def ic(request: Request):
    with SqlSession() as session:
        start, end = get_month_start_end(datetime.now())
        list = session.fetchall(icgb_mapper.list_by_time(start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")), Icgb)
        # events = [CalendarVO(title=data.title, start=data.icgb_day, end=data.icgb_day, url=data.href) for data in list]
    return templates.TemplateResponse('icgb.html', context={
        'request': request,
        # 'events': jsonable_encoder(events)
    })

@main_router.get('/collections/keyboard')
@main_router.get('/collections/keyboard/')
@main_router.get('/collections/keyboard/{ref}')
async def keyboard(request: Request, ref:Optional[str] = None, mode:Optional[str] = 't'):
    with SqlSession() as session:
        refs = board_mapper.fetch_all_ref(session=session)
        array_2d = []
        if len(refs) > 0:
            array_2d = board_mapper.fetch_2d_array_by_ref(session=session, ref=ref if ref else refs[0])
    return templates.TemplateResponse('collections-keyboard.html', context={
        'request': request,
        'data': array_2d,
        'stor_boxs': refs,
    })


