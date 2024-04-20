from datetime import datetime
from typing import Optional

from fastapi import Query, APIRouter
from sqlalchemy import select, insert, func, and_, or_, update, desc, text
from starlette.responses import JSONResponse

from app.core.database import SqlSession
from app.core.internal import generate_random_string, paginate_info
from app.core.snowflake_id import id_worker
from app.model.assembler import convert_vo, convert_keywrod_sqlm
from app.model.domain import sqlm_keyword, Keyword, sqlm_keyboard_switch, KeyboardSwitch
from app.model.request import KeywordRequest
from app.model.vo import MksVO, KeywordVO
from app.web.stats import count_stash
import numpy

api_router = APIRouter(prefix='/api')

@api_router.get('/mkstable')
async def mkstable(
        stash: Optional[str]=None,
        search: str=Query(alias='search', default=None),
):
    with SqlSession() as session:
        stmt = select(sqlm_keyboard_switch).where(sqlm_keyboard_switch.c.deleted == 0).order_by(desc(sqlm_keyboard_switch.columns.update_time)).limit(100)
        if stash is not None:
            stmt = stmt.where(sqlm_keyboard_switch.c.stash == stash)
        if search is not None:
            s = '%' + search + '%'
            stmt = stmt.where(
                or_(
                    sqlm_keyboard_switch.columns.name.like(s),
                    sqlm_keyboard_switch.columns.studio.like(s),
                    sqlm_keyboard_switch.columns.manufacturer.like(s),
                    sqlm_keyboard_switch.columns.tag.like(s),
                    sqlm_keyboard_switch.columns.logo.like(s)
                )
            )
        list = session.fetchall(
            stmt,
            KeyboardSwitch
        )
        _u = [ {'name': item.name + '(' + item.studio + ')', 'pic': item.pic } for item in list]
        if len(list) % 10 > 0:
            for i in range(10 - len(list) % 10):
                _u.append({'name': '', 'pic': ''})
        result = numpy.array(_u).reshape(-1, 10).tolist()
        return {'status': 'ok', 'data': result, 'recordsTotal': 100, 'recordsFiltered': 100}

@api_router.get('/copymks')
async def copymks(id: int):
    with SqlSession() as session:
        mks = session.fetchone(
            select(sqlm_keyboard_switch).where(sqlm_keyboard_switch.c.id==id),
            KeyboardSwitch
        )
        if mks is None:
            return {'status': 'error', 'msg': '轴体不存在'}
        now = datetime.now().timestamp()
        mks.name=mks.name + '副本' + generate_random_string(4)
        mks.id = id_worker.next_id()
        mks.create_time = now
        mks.update_time = now
        mks.stash = ''
        mks.quantity = 0
        session.execute(insert(sqlm_keyboard_switch).values(mks.dict()))
        return {'status': 'ok'}

@api_router.delete('/mks')
async def delete(id: int):
    with SqlSession() as session:
        row = session.execute(
            update(sqlm_keyboard_switch).values(deleted=1, update_time=datetime.now().timestamp())
            .where(sqlm_keyboard_switch.c.id==id)
        )
        if row > 0:
            return {'status': 'ok'}
        else:
            return {'status': 'error', 'msg': '删除失败'}


def build_search_condition(search):
    delimiter = ' or ' if ' or ' in search else ' and '
    search_terms = search.split(delimiter)

    sql_params = {}
    str_list = []
    for i, term in enumerate(search_terms):
        conditions = " or ".join(f"{field} like :search_{i}" for field in ['name', 'studio', 'manufacturer', 'tag', 'logo'])
        str_list.append(f"({conditions})")
        sql_params[f'search_{i}'] = f'%{term.strip()}%'

    sql_text = text(f" {delimiter} ".join(str_list)).bindparams(**sql_params)
    return sql_text, sql_params

def build_or_condition(field, condition):
    cond_list = condition.split(',')
    list = []
    params = {}
    for i, _c in enumerate(cond_list):
        list.append(f"{field} = :bsearch_{i}")
        params[f'bsearch_{i}'] = _c.strip()
    return text('or'.join(list)).bindparams(**params)

def build_where(stmt_list_base, stmt_count_base, where_condtion):
    return stmt_list_base.where(where_condtion), stmt_count_base.where(where_condtion)

def filter(start: Optional[int]=0,
        length: Optional[int]=10,
        search: str=Query(alias='s', default=None),
        stash: Optional[str]=None,
        manufacturer: Optional[str]=None,
        is_available: Optional[bool]=None):
    stmt_list = select('*') \
        .select_from(text('keyboard_switch')) \
        .where(text('deleted = 0')) \
        .order_by(text('update_time desc')) \
        .limit(length) \
        .offset(start)
    stmt_count = select(func.count('*')).select_from(text('keyboard_switch')).where(text('deleted = 0'))
    if search is not None:
        sql_text, _ = build_search_condition(search)
        stmt_list, stmt_count = build_where(stmt_list, stmt_count, sql_text)
    if manufacturer:
        sql_text = build_or_condition('manufacturer', manufacturer)
        stmt_list, stmt_count = build_where(stmt_list, stmt_count, sql_text)
    print(f'have: {is_available}')
    if is_available is None:
        pass
    elif is_available is True:
        sql_text = text("stash != '' and stash is not null")
        stmt_list, stmt_count = build_where(stmt_list, stmt_count, sql_text)
    else:
        sql_text = text("(stash = '' or stash is null)")
        stmt_list, stmt_count = build_where(stmt_list, stmt_count, sql_text)
    if stash is not None:
        stash = stash if stash != '-1' else ''
        stmt_list = stmt_list.where(sqlm_keyboard_switch.c.stash == stash)
        stmt_count = stmt_count.where(sqlm_keyboard_switch.c.stash == stash)
    return stmt_list, stmt_count

@api_router.get(('/filter'))
@api_router.get('/mkslist')
async def mkslist(
        draw: Optional[int]=None,
        start: Optional[int]=0,
        length: Optional[int]=10,
        search: str=Query(alias='s', default=None),
        stash: Optional[str]=None,
        manufacturer: Optional[str]=None,
        is_available: Optional[bool]=None
):
    with SqlSession() as session:
        stmt_list, stmt_count = filter(start, length, search, stash, manufacturer, is_available)
        list = session.fetchall(stmt_list, KeyboardSwitch)
        mkslist = [convert_vo(i) for i in list]
        total = session.count(stmt_count)
    return {
        'draw': draw,
        'page_list': mkslist,
        'recordsTotal': total,
        'recordsFiltered': total,
        'page': paginate_info(total, start / length +1, length)
    }

@api_router.post('/mks', response_class=JSONResponse)
async def save_mks(req: MksVO):
    now = datetime.now().timestamp()
    id = req.id
    is_update = True
    if req.id == '':
        is_update = False
        id = id_worker.next_id()
    keyboard_switch = KeyboardSwitch(
        name=req.name, studio=req.studio, manufacturer=req.manufacturer, type=req.type,
        pic=req.pic, tag=req.tag, quantity=req.quantity, price=req.price, desc=req.desc,
        specs=req.specs.json(),
        create_time=now, update_time=now, id=id, stash=req.stash,
        logo=req.logo, variation=req.variation, deleted=0
    )
    if keyboard_switch.studio == '':
        return {'status': 'error', 'msg': '工作室为空'}
    with SqlSession() as session:
        save_or_ignore_keyword(keyboard_switch.studio, 'studio', session)
        save_or_ignore_keyword(keyboard_switch.logo, 'logo', session)
        _ks = session.fetchone(
            select(sqlm_keyboard_switch)
                .where(sqlm_keyboard_switch.columns.name == keyboard_switch.name),
            KeyboardSwitch
        )
        if is_update:
            if _ks is not None and _ks.id != keyboard_switch.id and _ks.deleted == 0:
                return {'status': 'error', 'msg': '轴体名字重复'}
            else:
                session.execute(
                    update(sqlm_keyboard_switch).values(manufacturer=keyboard_switch.manufacturer,
                                                        studio=keyboard_switch.studio,
                                                        pic=keyboard_switch.pic,
                                                        type=keyboard_switch.type,
                                                        tag=keyboard_switch.tag,
                                                        specs=keyboard_switch.specs,
                                                        quantity=keyboard_switch.quantity,
                                                        price=keyboard_switch.price,
                                                        desc=keyboard_switch.desc,
                                                        update_time=keyboard_switch.update_time,
                                                        name=keyboard_switch.name,
                                                        stash=keyboard_switch.stash,
                                                        logo=keyboard_switch.logo,
                                                        variation=keyboard_switch.variation,
                                                        deleted=0)
                        .where(sqlm_keyboard_switch.columns.id == id)
                )
                return {'status': 'ok'}
        else:
            if _ks is None:
                session.execute(insert(sqlm_keyboard_switch).values(keyboard_switch.dict()))
                return {'status': 'ok'}
            else:
                return {'status': 'error', 'msg': '轴体名字已存在!'}


def save_or_ignore_keyword(word: str, type: str, session):
    now = datetime.now().timestamp()
    kw = session.fetchone(
        select(sqlm_keyword)
            .where(sqlm_keyword.columns.word==word,
                   sqlm_keyword.columns.type==type),
        Keyword
    )
    if kw is not None:
        return
    session.execute(
        insert(sqlm_keyword).values(Keyword(word=word, type=type, rank=0, deleted=0,
                                                create_time=now, update_time=now).dict())
    )


@api_router.get("/keyword", response_class=JSONResponse)
async def keyword(
        draw: Optional[int]=None,
        start: Optional[int]=None,
        length: Optional[int]=None,
        search: str=Query(alias='s', default=None),
        type: str=Query(alias='t', default=None)
):
    with SqlSession() as session:
        as_stmt = select(func.count(sqlm_keyboard_switch.c.name))
        if type == 'switch_type':
            as_stmt = as_stmt.where(sqlm_keyboard_switch.c.type==sqlm_keyword.c.word, sqlm_keyboard_switch.c.deleted==0)
        elif type == 'studio':
            as_stmt = as_stmt.where(sqlm_keyboard_switch.c.studio==sqlm_keyword.c.word, sqlm_keyboard_switch.c.deleted==0)
        elif type == 'manufacturer':
            as_stmt = as_stmt.where(sqlm_keyboard_switch.c.manufacturer==sqlm_keyword.c.word, sqlm_keyboard_switch.c.deleted==0)
        elif type == 'logo':
            as_stmt = as_stmt.where(sqlm_keyboard_switch.c.logo==sqlm_keyword.c.word, sqlm_keyboard_switch.c.deleted==0)
        else:
            as_stmt = select(-1)
        stmt_list = select(sqlm_keyword, as_stmt.label('count'))\
            .where(sqlm_keyword.columns.type==type, sqlm_keyword.columns.deleted==0)\
            .order_by(desc(sqlm_keyword.columns.create_time))
        stmt_count = select(func.count(sqlm_keyword.columns.word))\
            .where(sqlm_keyword.columns.type==type, sqlm_keyword.columns.deleted==0)
        if search is not None:
            stmt_list = stmt_list.where(sqlm_keyword.columns.word.like('%' + search + '%'))
            stmt_count = stmt_count.where(sqlm_keyword.columns.word.like('%' + search + '%'))
        list = session.fetchall(stmt_list.offset(start).limit(length), KeywordVO)
        total = session.count(stmt_count)
        if type == 'stash':
            scount = count_stash()
            for item in list:
                item.count = scount[item.word] if scount.keys().__contains__(item.word) else 0
        return {'draw': draw, 'page_list': list, 'recordsTotal': total, 'recordsFiltered': total}

@api_router.post('/keyword', response_class=JSONResponse)
async def save_keyword(req: KeywordRequest):
    with SqlSession() as session:
        if req.id is None or req.id == '':
            dd = convert_keywrod_sqlm(req).dict()
            session.execute(insert(sqlm_keyword).values(dd))
            return {'status': 'ok'}
        else:
            now = int(datetime.now().timestamp())
            _old = session.fetchone(
                select(sqlm_keyword)
                .where(sqlm_keyword.columns.word == req.id, sqlm_keyword.columns.type == req.type),
                Keyword
            )
            if _old is None:
                return {'status': 'error', 'msg': '数据不存在'}
            session.execute(
                update(sqlm_keyword)
                    .values(word=req.word, rank=req.rank, update_time=now, deleted=0, memo=req.memo)
                    .where(sqlm_keyword.columns.word==req.id, sqlm_keyword.columns.type==req.type)
            )
            switcher = {
                'stash': update(sqlm_keyboard_switch).values(stash=req.word).where(sqlm_keyboard_switch.c.stash==req.id),
                'studio': update(sqlm_keyboard_switch).values(studio=req.word).where(sqlm_keyboard_switch.c.studio==req.id),
                'manufacturer': update(sqlm_keyboard_switch).values(manufacturer=req.word).where(sqlm_keyboard_switch.c.manufacturer==req.id),
                'logo': update(sqlm_keyboard_switch).values(logo=req.word).where(sqlm_keyboard_switch.c.logo==req.id),
                'switch_type': update(sqlm_keyboard_switch).values(type=req.word).where(sqlm_keyboard_switch.c.type==req.id)
            }
            stmt = switcher.get(req.type)
            if stmt is None:
                return {'status': 'ok'}
            session.execute(stmt)
            return {'status': 'ok'}

@api_router.delete('/keyword', response_class=JSONResponse)
async def delete_keyword(req: KeywordRequest):
    with SqlSession() as session:
        switcher = {
            'stash': select(func.count(sqlm_keyboard_switch.columns.id)).where(sqlm_keyboard_switch.c.stash == req.word),
            'studio':  select(func.count(sqlm_keyboard_switch.columns.id)).where(sqlm_keyboard_switch.c.studio == req.word),
            'manufacturer':  select(func.count(sqlm_keyboard_switch.columns.id)).where(sqlm_keyboard_switch.c.manufacturer == req.word),
            'logo':  select(func.count(sqlm_keyboard_switch.columns.id)).where(sqlm_keyboard_switch.c.logo == req.word),
            'switch_type':  select(func.count(sqlm_keyboard_switch.columns.id)).where(sqlm_keyboard_switch.c.type == req.word)
        }
        stmt = switcher.get(req.type)
        if stmt is None:
            return {'status': 'error', 'msg': '参数错误'}
        if session.count(stmt) > 0:
            return {'status': 'error', 'msg': '数据还在使用,无法删除'}
        session.execute(
            update(sqlm_keyword)
                .values(deleted=1)
                .where(sqlm_keyword.columns.word==req.word, sqlm_keyword.columns.type==req.type)
        )
    return {'status': 'ok'}
