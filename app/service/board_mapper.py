from typing import List

from sqlalchemy import text

from app.core.database import SqlSession
from app.core.internal import generate_random_string
from app.model.domain import Board
from app.model.vo import SwitchVO


def exists_ref(session: SqlSession, ref: str) -> bool:
    m = session.fetchone(text(f"select * from board where ref = '{ref}' "), Board)
    return m is not None

def gen_ref(session: SqlSession) -> str:
    ref = generate_random_string(2).upper()
    exists = exists_ref(session, ref)
    if not exists:
        return  ref
    return gen_ref(session)

def fetch_all_ref(session: SqlSession) -> List[str]:
    return session.fetchall(text(f"select distinct ref from board"), str)

def fetch_by_ref(session: SqlSession, ref: str) -> List[SwitchVO]:
    return session.fetchall(text(f"select s.*, b.row, b.col from board b "
                                 f"inner join switches s on s.id = b.sid and s.deleted = 0 "
                                 f"where b.ref = '{ref}' "), SwitchVO)


def fetch_2d_array_by_ref(session: SqlSession, ref: str):
    list = fetch_by_ref(session, ref)
    return generate_2d_array(list)

def generate_2d_array(data: List[SwitchVO]):
    # 查找数据中的最大行和列索引
    max_row = max((item.row for item in data if item.row is not None), default=0)
    max_column = max((item.col for item in data if item.col is not None), default=0)

    # 初始化一个空的二维数组
    array_2d = [[None for _ in range(max_column)] for _ in range(max_row)]

    # 填充二维数组
    for item in data:
        if item.row is not None and item.col is not None:
            row = item.row
            column = item.col
            array_2d[row-1][column-1] = item.dict()

    return array_2d

def batch_save(session: SqlSession, list: List[Board]):
    values_list = []
    for item in list:
        values_list.append(f"({item.sid}, {item.row}, {item.col}, '{item.ref}' ) ")

    values = ",".join(values_list)
    return session.execute(text(f"INSERT INTO board (sid, row, col, ref) VALUES {values}"
                f"ON CONFLICT(ref, row, col) DO UPDATE SET "
                f"sid = excluded.sid"))
