from datetime import datetime
from typing import Optional, List

from fastapi import Query, APIRouter
from pydantic.main import BaseModel
from sqlalchemy import select, insert, func, and_, or_, update, desc, text
from starlette.responses import JSONResponse

from app.core.database import SqlSession
from app.core.internal import generate_random_string, paginate_info, get_month_start_end
from app.core.snowflake_id import id_worker
from app.crud import keyword_mapper, switches_mapper, icgb_mapper, board_mapper
from app.crud.switches_mapper import Filter
from app.model.assembler import convert_vo, convert_keywrod_sqlm
from app.model.domain import sqlm_keyword, Keyword, sqlm_keyboard_switch, KeyboardSwitch, Switches, KeyCountBO, Icgb, \
    Board
from app.model.request import KeywordRequest, IcgbRequest, SqliteRequest
from app.model.vo import CalendarVO
from app.web.v2page import get_keyword_counts

v2_api_router = APIRouter(prefix='/api/v2')

@v2_api_router.get('/switches/copy')
async def copymks(id: int):
    with SqlSession() as session:
        switches = session.fetchone(switches_mapper.get_by_id(id), Switches)
        if switches is None:
            return {'status': 'error', 'msg': '轴体不存在'}
        now = datetime.now().timestamp()
        switches.name=switches.name + '副本' + generate_random_string(4)
        switches.id = id_worker.next_id()
        switches.create_time = now
        switches.update_time = now
        switches.stor_loc_box = ''
        switches.num = 0
        session.execute(switches_mapper.save(switches))
        return {'status': 'ok'}

@v2_api_router.delete('/switches')
async def delete(id: int):
    with SqlSession() as session:
        row = session.execute(switches_mapper.delete_by_id(id))
        if row > 0:
            return {'status': 'ok'}
        else:
            return {'status': 'error', 'msg': '删除失败'}



@v2_api_router.get('/switches/filter')
async def mkslist(
        draw: Optional[int]=None,
        start: Optional[int]=0,
        length: Optional[int]=10,
        search: str=Query(default=None, alias='s'),
        stor_box: Optional[str]=None,
        manufacturer: Optional[str]=None,
        is_available: Optional[bool]=None
):
    with SqlSession() as session:
        stmt_list, stmt_count = switches_mapper.filter(start, length, search, stor_box, manufacturer, is_available)
        list = session.fetchall(stmt_list, Switches)
        total = session.count(stmt_count)
    return {
        'draw': draw,
        'page_list': [convert_vo(i) for i in list],
        'recordsTotal': total,
        'recordsFiltered': total,
        'page': paginate_info(total, start / length +1, length)
    }

@v2_api_router.post('/switches', response_class=JSONResponse)
async def save_mks(req: Switches):
    now = datetime.now().timestamp()
    with SqlSession() as session:
        db_switches = session.fetchone(switches_mapper.get_by_name(req.name), Switches)
        if req.id is None or req.id == '':
            if db_switches is not None:
                return {'status': 'error', 'msg': '新增轴体已存在'}
            req.create_time = now
            req.update_time = now
            req.id = id_worker.next_id()
            req.deleted = 0
            session.execute(switches_mapper.save(req))
            save_or_ignore_keyword(req.studio, 'studio', session)
            save_or_ignore_keyword(req.mark, 'mark', session)
            return {'status': 'ok'}
        else:
            if db_switches is not None and db_switches.id != req.id:
                return {'status': 'error', 'msg': req.name + '已经存在'}
            req.update_time = now
            session.execute(switches_mapper.update_by_id(req, req.id))
            save_or_ignore_keyword(req.studio, 'studio', session)
            save_or_ignore_keyword(req.mark, 'mark', session)
            return {'status': 'ok'}


def save_or_ignore_keyword(word: str, type: str, session):
    if word is None or word == '':
        return
    kw = session.fetchone(keyword_mapper.get_by_word(word, type), Keyword)
    if kw is not None:
        return
    session.execute(keyword_mapper.save(word, type))


@v2_api_router.get("/keyword", response_class=JSONResponse)
async def keyword(
        draw: Optional[int]=None,
        start: Optional[int]=None,
        length: Optional[int]=None,
        search: str=Query(alias='s', default=None),
        type: str=Query(alias='t', default=None)
):
    with SqlSession() as session:
        list = get_keyword_counts(session, type, start, length, search)
        filter = Filter(None, select(text('count(*)')).select_from(text('keyword')).where(text('deleted = 0')))
        if search:
            filter.append_where(text('word like :search').bindparams(search=f'%{search}%'))
        _, count = filter.append_where(text('type = :type').bindparams(type=type)).build()
        total = session.count(count)
        return {'draw': draw, 'page_list': list, 'recordsTotal': total, 'recordsFiltered': total}

@v2_api_router.post('/keyword', response_class=JSONResponse)
async def save_keyword(req: KeywordRequest):
    with SqlSession() as session:
        if req.id is None or req.id == '':
            session.execute(keyword_mapper.save(req.word, req.type, req.memo, req.rank))
            return {'status': 'ok'}
        else:
            _old = session.fetchone(keyword_mapper.get_by_word(req.id, req.type), Keyword)
            if _old is None:
                return {'status': 'error', 'msg': '数据不存在'}
            session.execute(keyword_mapper.update_by_word_and_type(req, req.id, req.type))
            session.execute(switches_mapper.update_keyword(req.type, req.word, req.id))
            return {'status': 'ok'}

@v2_api_router.delete('/keyword', response_class=JSONResponse)
async def delete_keyword(req: KeywordRequest):
    with SqlSession() as session:
        if session.count(switches_mapper.count_by_field(req.type, req.word)) > 0:
            return {'status': 'error', 'msg': '数据还在使用,无法删除'}
        session.execute(keyword_mapper.delete(req.word, req.type))
    return {'status': 'ok'}

@v2_api_router.post('/icgb', response_class=JSONResponse)
async def update_icgb(req: IcgbRequest):
    with SqlSession() as session:
        session.execute(
            icgb_mapper.update_very_useful(title=req.title, href=req.href, icgb_day=req.icgb_day, id=req.id, usefulness=1)
        )
        return {'status': 'ok'}

@v2_api_router.get('/icgb/unuseful')
async def update_unuseful(id: str):
    with SqlSession() as session:
        session.execute(icgb_mapper.update_unuseful(id))
    return {'status': 'ok'}

@v2_api_router.get('/icgb', response_class=JSONResponse)
async def list_icgb(day: str=None, usefulness: int=1):
    with SqlSession() as session:
        list = session.fetchall(icgb_mapper.list_by_day(day=day, usefulness=usefulness), Icgb)
    return {'page_list': list}

@v2_api_router.get('/gen-icgb', response_class=JSONResponse)
async def gen_icgb(index: int):
    icgblist, day = icgb_mapper.gen_icgb(index)
    if len(icgblist) == 0:
        return {'status': 'error', 'msg': day}
    with SqlSession() as session:
        session.execute(icgb_mapper.batch_save_or_update(icgblist))
        list = session.fetchall(icgb_mapper.list_by_day(day=day), Icgb)
    return {'status': 'ok', 'page_list': list}

@v2_api_router.get('/done_icgblist', response_class=JSONResponse)
async def done_icgblist(day: str):
    with SqlSession() as session:
        done_icgblist = session.fetchall(icgb_mapper.list_by_icgb_day(day), Icgb)
    return {'page_list': done_icgblist}


@v2_api_router.post('/sqlite', response_class=JSONResponse)
async def sqlite(req: SqliteRequest):
    with SqlSession() as session:
        session.execute(text(f"{req.sql}"))
        # session.execute(text(f"CREATE TABLE IF NOT EXISTS icgb (id INTEGER PRIMARY KEY, title TEXT NOT NULL, href TEXT, icgb_day TEXT, day TEXT, text TEXT, unique_title TEXT, url TEXT NOT NULL, create_time INTEGER, update_time INTEGER, deleted INTEGER DEFAULT 0, usefulness INTEGER DEFAULT 0, UNIQUE(unique_title, url));"))
    return {'status': 'ok'}

@v2_api_router.get('/icgb/calendar_events', response_class=JSONResponse)
async def calendar_events(start: str, end: str):
    with SqlSession() as session:
        list = session.fetchall(icgb_mapper.list_by_time(start, end), Icgb)
        events = [CalendarVO(title=data.title, start=data.icgb_day, end=data.icgb_day, url=data.href) for data in list]
    return {'page_list': events}

class BoardRequest(BaseModel):
    matrix: List[List[str]]
    ref: str=''

@v2_api_router.post('/keyboard', response_class=JSONResponse)
async def save_keyboard(request: BoardRequest):
    with SqlSession() as session:
        non_empty_values = set()
        value_positions = {}

        for row_idx, row in enumerate(request.matrix):
            for col_idx, value in enumerate(row):
                if value:
                    non_empty_values.add(value)
                    if value not in value_positions:
                        value_positions[value] = []
                    value_positions[value].append((row_idx + 1, col_idx + 1))
        list = switches_mapper.list_by_names(session, names=non_empty_values)
        value_id_map = {getattr(item, 'name'): item for item in list}
        results = []
        ref = request.ref if request.ref else board_mapper.gen_ref(session=session)
        for value, positions in value_positions.items():
            item_id = value_id_map.get(value)
            for row, col in positions:
                results.append(Board(sid=item_id.id, ref=ref, row=row, col=col))
        board_mapper.batch_save(session=session, list=results)
    return {'status': 'ok'}

@v2_api_router.get('/keyboard')
async def keyboard(s:Optional[str] = None):
    with SqlSession() as session:
        array_2d = board_mapper.fetch_2d_array_by_ref(session=session, ref=s)
    return {'page_list': array_2d}
