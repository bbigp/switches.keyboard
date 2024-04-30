from datetime import datetime

from sqlalchemy import text, insert

from app.model.domain import T_keyword, Keyword


def get_by_word(word: str, type: str):
    return text(f'select * from keyword where word = {word} and type = {type}')

def save(word: str, type: str):
    now = datetime.now().timestamp()
    return insert(T_keyword).values(Keyword(word=word, type=type, rank=0, deleted=0,
                                        create_time=now, update_time=now).dict())