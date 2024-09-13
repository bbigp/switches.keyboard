from datetime import datetime

from sqlalchemy import text, insert, select, desc, func, update

from app.crud.switches_mapper import Filter
from app.model.domain import T_keyword, Keyword


def get_by_word(word: str, type: str):
    return text(f"select * from keyword where word = '{word}' and type = '{type}'")

def save(word: str, type: str, memo: str='', rank: int=0):
    now = int(datetime.now().timestamp())
    return insert(T_keyword).values(Keyword(word=word, type=type, rank=rank, deleted=0, memo=memo,
                                        create_time=now, update_time=now).dict())

def update_by_word_and_type(keyword, key, type):
    now = int(datetime.now().timestamp())
    return update(T_keyword)\
        .values(word=keyword.word, rank=keyword.rank, update_time=now, deleted=0, memo=keyword.memo)\
        .where(text('word = :key and type = :type').bindparams(key=key, type=type))

def delete(word, type):
    return text('update keyword set deleted = 1 where word = :word and type = :type').bindparams(word=word, type=type)

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