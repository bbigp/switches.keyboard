from loguru import logger
from starlette.config import Config


config = Config('.env')
MYSQL_HOST = config('MYSQL_HOST', default='127.0.0.1')
MYSQL_PORT = int(config('MYSQL_PORT', default=3306))
MYSQL_USER = config('MYSQL_USER', default='root')
MYSQL_PASSWORD = config('MYSQL_PASSWORD', default='')
MYSQL_NAME = config('MYSQL_NAME', default='crow')
PDL_table_name=config('PDL_TABLE', default='pdl_record')
CONFIG_table_name=config('CONFIG_TBALE', default='config_d')
LABEL_table_name = config('LABEL_TABLE', default='label')

from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, Text, BIGINT
from sqlalchemy.orm import  sessionmaker
from sqlalchemy.ext.declarative import declarative_base


db_url = f'sqlite:///axial.db'
engine = create_engine(db_url, echo=False)
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

    def execute(self, sql, params=None):
        logger.debug('==>  Preparing: {}', sql)
        logger.debug('==>  Parameters: {}', sql.compile().params)
        r = self.conn.execute(sql, params=params)
        logger.info('<====>  Total: {}', r.rowcount)
        return r.rowcount

    def fetchall(self, sql, clz, params=None):
        logger.debug('==>  Preparing: {}', sql)
        logger.debug('==>  Parameters: {}', sql.compile().params)
        result = self.conn.execute(sql, params=params).fetchall()
        return parse_list_dict_2_model(result, clz)

    def fetchone(self, sql, clz, params=None):
        result = self.conn.execute(sql, params=params).fetchone()
        if result is None:
            return None
        return clz.parse_obj(result)

    def count(self, sql, params=None):
        result = self.conn.execute(sql, params=params).fetchone()
        return list(result.values())[0]

def parse_list_dict_2_model(list: list, claz) -> list:
    return [claz.parse_obj(i) for i in list]
