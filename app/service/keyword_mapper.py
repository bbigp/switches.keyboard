from datetime import datetime
from typing import List

from sqlalchemy import text, insert, select, desc, func, update
from sqlalchemy.dialects import sqlite

from app.core.database import SqlSession
from app.service.switches_mapper import Filter
from app.model.domain import T_keyword, Keyword
from app.model.vo import KeywordVO, StudioVO


def get_by_word(word: str, type: str):
    return text(f"select * from keyword where word = '{word}' and type = '{type}'")

def save(word: str, type: str, memo: str='', rank: int=0):
    now = int(datetime.now().timestamp())
    stmt = insert(T_keyword).values(Keyword(word=word, type=type, rank=rank, deleted=0, memo=memo,
                                        create_time=now, update_time=now).dict())
    compiled = stmt.compile(dialect=sqlite.dialect(), compile_kwargs={'literal_binds': True})
    return str(compiled)

def update_by_word_and_type(keyword, key, type):
    now = int(datetime.now().timestamp())
    return text(f"update keyword set word = '{keyword.word}', rank = {keyword.rank}, update_time = {now}, "
                f"deleted = 0, memo = '{keyword.memo}' "
                f"where word = '{key}' and type = '{type}' ")

def delete(word, type):
    return text(f"update keyword set deleted = 1 where word = '{word}' and type = '{type}' ")

def count_by_type(type: str):
    return text('select count(*) from keyword where type = :type').bindparams(type=type)

def list_by_type(type: str, offset=None, limit=None, search=None):
    filter = Filter(select('*').select_from(text('keyword')).where(text('deleted = 0')).order_by(text('word desc')))
    if limit:
        filter.limit(limit)
    if offset:
        filter.offset(offset)
    if search:
        filter.append_where(text('word like :search').bindparams(search=f'%{search}%'))
    base, _ =filter.append_where(text('type = :type').bindparams(type=type)).build()
    return base

def list_by_types(types):
    type = ",".join(["'" + t + "'" for t in types])
    return text(f"select * from keyword where deleted = 0 and type in ({type}) order by word desc")

def fetch_random_studios(session: SqlSession, search: str, limit: int) -> List[StudioVO]:
    query = f"select * from keyword where deleted = 0 and type = 'studio' "
    if search is not None and search != '':
        query += f" and word like '%{search}%' "
    query += f" ORDER BY RANDOM() limit {limit} "
    return session.fetchall(query, StudioVO)

def fetch_text(session):
    list = session.fetchall(list_by_types(['type', 'manufacturer', 'mark', 'studio']), KeywordVO)
    map = {}
    for item in list:
        map.setdefault(item.type, []).append(item)
    # switch_types = []
    # manufacturers = []
    # marks = []
    # studios = []
    # for item in list:
    #     if item.type == 'type':
    #         switch_types.append(item)
    #     elif item.type == 'manufacturer':
    #         manufacturers.append(item)
    #     elif item.type == 'mark':
    #         marks.append(item.word)
    #     elif item.type == 'studio':
    #         studios.append(item.word)
    #     else:
    #         pass
    # return switch_types, manufacturers, marks, studios
    return map.get('type'), map.get('manufacturer'), map.get('mark'), map.get('studio')


def fetch_keyboard(session):
    return session.fetchall(text(f"select * from keyword where deleted = 0 and type = 'stor_loc_box' and word like 'D.%' "), KeywordVO)