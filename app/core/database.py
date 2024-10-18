import datetime

from loguru import logger
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import app_config

engine = create_engine(app_config.db_dir, echo=False)
base = declarative_base(engine)
session = sessionmaker(bind=engine)
metadata = MetaData()

class SqlSession(object):

    def __init__(self, begin=False):
        self.b = begin

    def __enter__(self):
        # close_with_result=True
        self.conn = engine.connect()
        if self.b:
            self.transaction = self.conn.begin()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.b:
            if exc_type is not None:
                self.transaction.rollback()
            else:
                self.transaction.commit()
        else:
            pass

    def execute(self, sql):
        logger.debug('==>  Preparing: {}', sql)
        r = self.conn.execute(sql)
        logger.info('<====>  Total: {}', r.rowcount)
        s = self.conn.execute(f"insert into integration (sql_script, applied_at, status) values (?, ?, ?)",
                          (str(sql), datetime.datetime.now().timestamp(), 0))
        logger.info('<====>  Inserted integration: {}', s.rowcount)
        return r.rowcount

    def fetchall(self, sql, clz, params=None):
        logger.debug('==>  Preparing: {}', sql)
        result = self.conn.execute(sql, params=params).fetchall()
        return parse_list_dict_2_model(result, clz)

    def fetchone(self, sql, clz, params=None):
        logger.debug('==>  Preparing: {}', sql)
        result = self.conn.execute(sql, params=params).fetchone()
        if result is None:
            return None
        return clz.parse_obj(result)

    def count(self, sql, params=None):
        result = self.conn.execute(sql, params=params).fetchone()
        return list(result.values())[0]

def parse_list_dict_2_model(list: list, claz) -> list:
    if claz == str:
        return [row[0] for row in list]
    return [claz.parse_obj(i) for i in list]
