from datetime import datetime
from typing import Optional

from fastapi import Query, APIRouter
from sqlalchemy import select, insert, func, and_, or_, update, desc, text
from starlette.responses import JSONResponse

from app.core.database import SqlSession
from app.core.snowflake_id import id_worker
from app.model.assembler import convert_vo, convert_keywrod_sqlm
from app.model.domain import sqlm_keyword, Keyword, sqlm_keyboard_switch, KeyboardSwitch
from app.model.request import KeywordRequest
from app.model.vo import MksVO, KeywordVO
from app.web.stats import count_stash
import numpy

api_router = APIRouter(prefix='/api')

@api_router.get('/mkstable')
async def mkstable(stash: Optional[str]=None):
    if stash is None:
        return {'status': 'ok', 'data': [], 'recordsTotal': 100, 'recordsFiltered': 100}
    with SqlSession() as session:
        list = session.fetchall(
            select(sqlm_keyboard_switch).where(sqlm_keyboard_switch.c.stash==stash),
            KeyboardSwitch
        )
        _u = [ item.name + '(' + item.studio + ')' for item in list]
        if len(list) % 10 > 0:
            for i in range(10 - len(list) % 10):
                _u.append('')
        result = numpy.array(_u).reshape(-1, 10).tolist()
        return {'status': 'ok', 'data': result, 'recordsTotal': 100, 'recordsFiltered': 100}

@api_router.get('/mkslist')
async def mkslist(
        draw: Optional[int]=None,
        start: Optional[int]=0,
        length: Optional[int]=10,
        search: str=Query(alias='s', default=None),
        stash: Optional[str]=None
):
    with SqlSession() as session:
        stmt_list = select(sqlm_keyboard_switch).offset(start).limit(length).order_by(desc(sqlm_keyboard_switch.columns.update_time))
        stmt_count = select(func.count(sqlm_keyboard_switch.columns.id))
        if search is not None:
            s = '%' + search + '%'
            search_expression = and_(
                or_(
                    sqlm_keyboard_switch.columns.name.like(s),
                    sqlm_keyboard_switch.columns.studio.like(s),
                    sqlm_keyboard_switch.columns.manufacturer.like(s),
                    sqlm_keyboard_switch.columns.tag.like(s)
                )
            )
            stmt_list = stmt_list.where(search_expression)
            stmt_count = stmt_count.where(search_expression)
        if stash is not None:
            stash = stash if stash != '-1' else ''
            stmt_list =  stmt_list.where(sqlm_keyboard_switch.c.stash==stash)
            stmt_count = stmt_count.where(sqlm_keyboard_switch.c.stash==stash)
        list = session.fetchall(stmt_list, KeyboardSwitch)
        mkslist = [convert_vo(i) for i in list]
        total = session.count(stmt_count)
    return {'draw': draw, 'page_list': mkslist, 'recordsTotal': total, 'recordsFiltered': total}

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
        logo=req.logo, variation=req.variation
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
            if _ks is not None and _ks.id != keyboard_switch.id:
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
                                                        variation=keyboard_switch.variation)
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
        if type == 'switch_type':
            as_stmt = select(func.count(sqlm_keyboard_switch.c.name)).where(sqlm_keyboard_switch.c.type==sqlm_keyword.c.word)
        elif type == 'studio':
            as_stmt = select(func.count(sqlm_keyboard_switch.c.name)).where(sqlm_keyboard_switch.c.studio==sqlm_keyword.c.word)
        elif type == 'manufacturer':
            as_stmt = select(func.count(sqlm_keyboard_switch.c.name)).where(sqlm_keyboard_switch.c.manufacturer==sqlm_keyword.c.word)
        elif type == 'logo':
            as_stmt = select(func.count(sqlm_keyboard_switch.c.name)).where(sqlm_keyboard_switch.c.logo==sqlm_keyword.c.word)
        else:
            as_stmt = select(-1)
        stmt_list = select(sqlm_keyword, as_stmt.label('count')).where(sqlm_keyword.columns.type==type, sqlm_keyword.columns.deleted==0).order_by(desc(sqlm_keyword.columns.create_time))
        stmt_count = select(func.count(sqlm_keyword.columns.word)).where(sqlm_keyword.columns.type==type, sqlm_keyword.columns.deleted==0)
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
        _k = session.fetchone(
            select(sqlm_keyword)
                .where(sqlm_keyword.columns.word==req.word, sqlm_keyword.columns.type==req.type),
            Keyword
        )
        if _k is None:
            dd = convert_keywrod_sqlm(req).dict()
            session.execute(insert(sqlm_keyword).values(dd))
            return {'status': 'ok'}
        else:
            now = int(datetime.now().timestamp())
            session.execute(
                update(sqlm_keyword)
                    .values(rank=req.rank, update_time=now, deleted=0, memo=req.memo)
                    .where(sqlm_keyword.columns.word==req.word, sqlm_keyword.columns.type==req.type)
            )
            return {'status': 'ok'}

@api_router.delete('/keyword', response_class=JSONResponse)
async def delete_keyword(req: KeywordRequest):
    with SqlSession() as session:
        session.execute(
            update(sqlm_keyword)
                .values(deleted=1)
                .where(sqlm_keyword.columns.word==req.word, sqlm_keyword.columns.type==req.type)
        )
    return {'status': 'ok'}
