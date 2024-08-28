from datetime import datetime
from typing import Optional

from fastapi import Query, APIRouter
from sqlalchemy import select, insert, func, and_, or_, update, desc, text
from starlette.responses import JSONResponse

from app.core.database import SqlSession
from app.core.internal import generate_random_string, paginate_info
from app.core.snowflake_id import id_worker
from app.crud import keyword_mapper, switches_mapper
from app.model.assembler import convert_vo, convert_keywrod_sqlm
from app.model.domain import sqlm_keyword, Keyword, sqlm_keyboard_switch, KeyboardSwitch
from app.model.request import KeywordRequest
from app.model.vo import MksVO, KeywordVO
from app.web.stats import count_stash

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
        result = []
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



@api_router.get(('/filter'))
@api_router.get('/mkslist')
async def mkslist(
        draw: Optional[int]=None,
        start: Optional[int]=0,
        length: Optional[int]=10,
        search: str=Query(default='', alias='s'),
        stash: Optional[str]='',
        manufacturer: Optional[str]=None,
        is_available: Optional[bool]=None
):
    with SqlSession() as session:
        stmt_list, stmt_count = switches_mapper.filter(start, length, search, stash, manufacturer, is_available)
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
    kw = session.fetchone(keyword_mapper.get_by_word(word, type), Keyword)
    if kw is not None:
        return
    session.execute(keyword_mapper.save(word, type))


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
