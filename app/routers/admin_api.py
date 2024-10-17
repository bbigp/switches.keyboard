import os
import shutil
from datetime import datetime
from typing import Optional, List

from aiohttp import ClientSession
from fastapi import Query, APIRouter, UploadFile
from pydantic.main import BaseModel
from sqlalchemy import select, text
from starlette.responses import JSONResponse

from app import config
from app.config import app_config
from app.core.database import SqlSession
from app.core.internal import generate_random_string, paginate_info, ImageProcessor
from app.core.snowflake_id import id_worker
from app.crud import keyword_mapper, switches_mapper, icgb_mapper, board_mapper
from app.crud.switches_mapper import Filter
from app.model.assembler import convert_vo
from app.model.domain import Keyword, Switches, Icgb, \
    Board
from app.model.request import KeywordRequest, IcgbRequest, SqliteRequest
from app.routers.page import get_keyword_counts

admin_api_router = APIRouter()

class BoardRequest(BaseModel):
    matrix: List[List[str]]
    ref: str=''

@admin_api_router.get('/api/v2/switches/copy')
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

@admin_api_router.delete('/api/v2/switches')
async def delete(id: int):
    with SqlSession() as session:
        row = session.execute(switches_mapper.delete_by_id(id))
        if row > 0:
            return {'status': 'ok'}
        else:
            return {'status': 'error', 'msg': '删除失败'}

@admin_api_router.get('/api/v2/switches/filter')
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

@admin_api_router.post('/api/v2/switches', response_class=JSONResponse)
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

@admin_api_router.get("/api/v2/keyword", response_class=JSONResponse)
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

@admin_api_router.post('/api/v2/keyword', response_class=JSONResponse)
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

@admin_api_router.delete('/api/v2/keyword', response_class=JSONResponse)
async def delete_keyword(req: KeywordRequest):
    with SqlSession() as session:
        if session.count(switches_mapper.count_by_field(req.type, req.word)) > 0:
            return {'status': 'error', 'msg': '数据还在使用,无法删除'}
        session.execute(keyword_mapper.delete(req.word, req.type))
    return {'status': 'ok'}

@admin_api_router.post('api/v2/icgb', response_class=JSONResponse)
async def update_icgb(req: IcgbRequest):
    with SqlSession() as session:
        session.execute(
            icgb_mapper.update_very_useful(title=req.title, href=req.href, icgb_day=req.icgb_day, id=req.id, usefulness=1)
        )
        return {'status': 'ok'}

@admin_api_router.get('/api/v2/icgb/unuseful')
async def update_unuseful(id: str):
    with SqlSession() as session:
        session.execute(icgb_mapper.update_unuseful(id))
    return {'status': 'ok'}

@admin_api_router.get('/api/v2/icgb', response_class=JSONResponse)
async def list_icgb(day: str=None, usefulness: int=1):
    with SqlSession() as session:
        list = session.fetchall(icgb_mapper.list_by_day(day=day, usefulness=usefulness), Icgb)
    return {'page_list': list}

@admin_api_router.get('/api/v2/gen-icgb', response_class=JSONResponse)
async def gen_icgb(index: int):
    icgblist, day = icgb_mapper.gen_icgb(index)
    if len(icgblist) == 0:
        return {'status': 'error', 'msg': day}
    with SqlSession() as session:
        session.execute(icgb_mapper.batch_save_or_update(icgblist))
        list = session.fetchall(icgb_mapper.list_by_day(day=day), Icgb)
    return {'status': 'ok', 'page_list': list}

@admin_api_router.get('/api/v2/done_icgblist', response_class=JSONResponse)
async def done_icgblist(day: str):
    with SqlSession() as session:
        done_icgblist = session.fetchall(icgb_mapper.list_by_icgb_day(day), Icgb)
    return {'page_list': done_icgblist}


@admin_api_router.post('/api/v2/sqlite', response_class=JSONResponse)
async def sqlite(req: SqliteRequest):
    with SqlSession() as session:
        session.execute(text(f"{req.sql}"))
        # session.execute(text(f"CREATE TABLE IF NOT EXISTS icgb (id INTEGER PRIMARY KEY, title TEXT NOT NULL, href TEXT, icgb_day TEXT, day TEXT, text TEXT, unique_title TEXT, url TEXT NOT NULL, create_time INTEGER, update_time INTEGER, deleted INTEGER DEFAULT 0, usefulness INTEGER DEFAULT 0, UNIQUE(unique_title, url));"))
    return {'status': 'ok'}

@admin_api_router.post('/api/v2/keyboard', response_class=JSONResponse)
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

@admin_api_router.get('/api/v2/keyboard')
async def keyboard(s:Optional[str] = None):
    with SqlSession() as session:
        array_2d = board_mapper.fetch_2d_array_by_ref(session=session, ref=s)
    return {'page_list': array_2d}

class DownloadRequest(BaseModel):
    url: str
@admin_api_router.post('/api/direct_use_pic', response_class=JSONResponse)
async def direct_use(req: DownloadRequest):
    if not req.url.startswith('/bfs/t/'):
        return {'status': 'error', 'mgs': '非法链接'}
    u = req.url.replace('/bfs/t/', '')
    _from = app_config.temp_dir + u
    temp_image_id = str(id_worker.next_id())
    _to = app_config.file_dir + temp_image_id + '.jpg'
    shutil.copy(_from, _to)
    return {'status': 'ok', 'data': '/bfs/fs/' + temp_image_id + '.jpg' }

@admin_api_router.post('/api/download_pic', response_class=JSONResponse)
async def download_pic(req: DownloadRequest):
    temp_image_id = str(id_worker.next_id())
    # https://blog.csdn.net/e5pool/article/details/131014343  https://blog.csdn.net/wq10_12/article/details/133944658 使用代理
    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'}
    async with ClientSession(headers=headers) as session:
        async with session.get(req.url) as response:
            with open(app_config.temp_dir + temp_image_id + '.jpg', 'wb') as f:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    f.write(chunk)
    return {'status': 'ok', 'data': '/bfs/t/' + temp_image_id + '.jpg' }

@admin_api_router.post('/api/upload_pic')
async def upload_pic(image: UploadFile):
    image_id = str(id_worker.next_id())
    with open(app_config.file_dir + image_id + '.jpg', 'wb') as f:
        f.write(await image.read())
    return {'status': 'ok', 'data': '/bfs/fs/' + image_id + '.jpg'}

@admin_api_router.post('/api/upload_temp_pic')
async def upload_pic(image: UploadFile):
    image_id = str(id_worker.next_id())
    with open(app_config.temp_dir + image_id + '.jpg', 'wb') as f:
        f.write(await image.read())
    return {'status': 'ok', 'data': '/bfs/t/' + image_id + '.jpg'}

@admin_api_router.get('/api/page_temp_image')
async def page_temp_image():
    path = config.options.temp_dir
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    latest_files = sorted(files)[-20:]
    return latest_files[::-1]

@admin_api_router.get('/api/process_image')
async def process_image():
    path = config.options.file_dir
    processor = ImageProcessor(ImageProcessor.CONVERT_WEBP)
    count = 0
    for file in os.listdir(path):
        _, exists = processor.process(os.path.join(path, file), config.options.image_cache_path)
        if not exists:
            count += 1
    return {'status': 'ok', 'data': count}

def save_or_ignore_keyword(word: str, type: str, session):
    if word is None or word == '':
        return
    kw = session.fetchone(keyword_mapper.get_by_word(word, type), Keyword)
    if kw is not None:
        return
    session.execute(keyword_mapper.save(word, type))