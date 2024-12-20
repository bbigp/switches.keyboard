from datetime import datetime, timedelta
from typing import Optional

from fastapi import Request, Query, Depends, APIRouter
from fastapi.encoders import jsonable_encoder
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from app.config import options
from app.core.database import SqlSession
from app.core.internal import get_month_start_end
from app.service import switches_mapper, icgb_mapper, board_mapper, keyword_mapper
from app.model.assembler import convert_vo
from app.model.domain import Icgb, Switches, KeyCountBO
from app.model.vo import KeywordVO
from app.utils.jinja2_filters import format_with_tolerance, format_studio_with_manufacturer
from app.utils.jinja2_template_render import render_switches_wrapper, determine_page_size, render_switches_filter, \
    render_studios

templates = Jinja2Templates(directory='ui/v2')
templates.env.filters['format_with_tolerance'] = format_with_tolerance
templates.env.filters['format_studio_with_manufacturer'] = format_studio_with_manufacturer

page_router = APIRouter()
admin_page_router = APIRouter()

@page_router.get("/")
@page_router.get('/collections')
@page_router.get("/collections/")
@page_router.get("/collections/switches")
@page_router.get("/collections/switches/")
@page_router.get("/collections/switches/{page}")
async def main(
        request: Request,
        page: Optional[int]=1,
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
min_travel: Optional[int]=None,
                          max_travel: Optional[int]=None,
                          min_total_travel: Optional[int]=None,
                          max_total_travel: Optional[int]=None,
min_force: Optional[int]=None,
                          max_force: Optional[int]=None,
                          min_total_force: Optional[int]=None,
                          max_total_force: Optional[int]=None
):
    with SqlSession() as session:
        switches_wrapper = render_switches_wrapper(session, page, size, search, type, stor_box, manufacturer,
                                                   is_available, studio=studio, stem=stem,
                                                   top_mat=top_mat, bottom_mat=bottom_mat,
                                                   min_travel=min_travel, max_travel=max_travel,
                                                   min_total_travel=min_total_travel, max_total_travel=max_total_travel,
                                                   min_force=min_force, max_force=max_force,
                                                   min_total_force=min_total_force, max_total_force=max_total_force)
        switches_filter = render_switches_filter(session, request)
        hot_switches = switches_mapper.fetch_hot(session, size=3)
    return templates.TemplateResponse('collections-switches.html', context={
        'request': request,
        'switches_wrapper': switches_wrapper,
        'switches_filter': switches_filter,
        'hot_switches': [convert_vo(i).dict() for i in hot_switches],
        'show_control': options.is_master(),
    })

@page_router.get('/collections/products/{id}')
async def detail(request: Request, id: int):
    with SqlSession() as session:
        model = session.fetchone(switches_mapper.get_by_id(id), Switches)
    return templates.TemplateResponse('collections-products.html', context={
        'request': request,
        'switch': convert_vo(model).dict(),
        'show_control': options.is_master(),
    })

@page_router.get('/collections/studios')
@page_router.get('/collections/studios/')
@page_router.get('/collections/studios/{page}')
async def studios(request: Request, page: Optional[int]=1, search: Optional[str]=None):
    with SqlSession() as session:
        studio_wrapper = render_studios(session, request)
    return templates.TemplateResponse('collections-studios.html', context={
        'request': request,
        'studio_wrapper': studio_wrapper,
        'show_control': options.is_master(),
    })


@page_router.get('/collections/keyboard')
@page_router.get('/collections/keyboard/')
@page_router.get('/collections/keyboard/{ref}')
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

@page_router.get('/icgb')
async def ic(request: Request):
    with SqlSession() as session:
        start, end = get_month_start_end(datetime.now())
        list = session.fetchall(icgb_mapper.list_by_time(start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")), Icgb)
        # events = [CalendarVO(title=data.title, start=data.icgb_day, end=data.icgb_day, url=data.href) for data in list]
    return templates.TemplateResponse('icgb.html', context={
        'request': request,
        # 'events': jsonable_encoder(events)
    })

@admin_page_router.get('/control/ig')
async def ayb(request: Request,):
    yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    with SqlSession() as session:
        list = session.fetchall(icgb_mapper.list_by_day(day=yesterday), Icgb)
        days = session.fetchall(icgb_mapper.list_day(), Icgb)
        if len(list) <= 0:
            icgblist, day = icgb_mapper.gen_icgb(0)
            if len(icgblist) > 0:
                session.execute(icgb_mapper.batch_save_or_update(icgblist))
                list = session.fetchall(icgb_mapper.list_by_day(day=day), Icgb)
            else:
                list = [Icgb(title=day)]
    return templates.TemplateResponse('c-ig.html', context={
        'request': request,
        'list': list,
        'day': day if len(list) <= 0 else yesterday,
        'days': jsonable_encoder([d.day for d in days])
    })

@admin_page_router.get('/control/sqlite')
async def sqlite(request: Request):
    return templates.TemplateResponse('sqlite.html', context={
        'request': request,
    })

@admin_page_router.get('/control/board')
async def keyboard(request:Request):
    with SqlSession() as session:
        list = switches_mapper.list(session)
        refs = board_mapper.fetch_all_ref(session=session)
        array_2d = []
        if len(refs) > 0:
            array_2d = board_mapper.fetch_2d_array_by_ref(session=session, ref=refs[0])
    return templates.TemplateResponse('keyboard.html', context={
        'request': request,
        'list': [s.name for s in list],
        'stor_boxs': refs,
        'data': array_2d,
    })

@admin_page_router.get("/control/keyword", response_class=HTMLResponse)
async def keyword(request: Request):
    return templates.TemplateResponse('keyword.html', context={'request': request})


@admin_page_router.get("/control/switches", response_class=HTMLResponse)
@admin_page_router.get("/control/switches/{id}", response_class=HTMLResponse)
async def index(request: Request, id: Optional[int]=None):
    with SqlSession() as session:
        switches = Switches(name='', studio='')
        if id is not None:
            switches = session.fetchone(switches_mapper.get_by_id(id), Switches)
        types, manufacturers, marks, studios = keyword_mapper.fetch_text(session)
        stor_loc_boxs = get_keyword_counts(session, 'stor_loc_box')
    return templates.TemplateResponse('switches.html', context={
        'request': request,
        'switches': switches,
        'switch_types': types,
        'manufacturers': manufacturers,
        'stor_loc_boxs': stor_loc_boxs,
        'marks': [item.word for item in marks],
        'studios': [item.word for item in studios],
        'error_msg': []
    })

@admin_page_router.get("/control", response_class=HTMLResponse)
@admin_page_router.get('/control/main', response_class=HTMLResponse)
async def index(request: Request):
    with SqlSession() as session:
        box_list = get_keyword_counts(session, 'stor_loc_box')
        t = session.count(switches_mapper.count())
    return templates.TemplateResponse('switches-list.html', context={'request': request, 'total': t, 'box_list': box_list})



def get_keyword_counts(sql_session, type, offset=None, limit=None, search=None):
    key_count_list = sql_session.fetchall(switches_mapper.group_by_type(type), KeyCountBO)
    count_detail_map = {}
    for count_detail in key_count_list:
        count_detail_map[count_detail.key] = count_detail.count

    keywords = sql_session.fetchall(keyword_mapper.list_by_type(type, offset, limit, search), KeywordVO)
    for model in keywords:
        model.count = count_detail_map[model.word] if count_detail_map.keys().__contains__(model.word) else 0
    return keywords

