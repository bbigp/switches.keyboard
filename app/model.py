from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, Text, BIGINT
from app.core.database import metadata

from pydantic.main import BaseModel


class KeyboardSwitch(BaseModel):
    id: int = None
    name: str
    manufacturer: str = ''
    studio: str = ''
    pic: str = ''
    type: str = ''
    tag: str = ''
    specs: str = None
    quantity: int = 0
    price: str = ''
    desc: str = ''
    create_time: int = None
    update_time: int = None
    # buy_address: str=None 购买地址


class Keyword(BaseModel):
    word: str
    type: str
    rank: int

class Etd(BaseModel):
    id: str
    data: str=None
    error: str=None
    create_time: int = None
    update_time: int = None

sqlm_etd = Table('e_t_d', metadata,
                 Column('id', String(50), primary_key=True),
                 Column('data', Text()),
                 Column('error', Text()),
                 Column('create_time', BIGINT()),
                 Column('update_time', BIGINT()))

sqlm_keyboard_switch = Table('keyboard_switch', metadata,
                 Column('id', BIGINT()),
                 Column('name', String(20), primary_key=True),
                 Column('manufacturer', String(50)),
                 Column('studio', String(50)),
                 Column('pic', String(200)),
                 Column('type', String(10)),
                 Column('tag', String(50)),
                 Column('specs', String(200)),
                 Column('quantity', Integer()),
                 Column('price', String()),
                 Column('desc', Text()),
                 Column('create_time', BIGINT()),
                 Column('update_time', BIGINT()),
                 )
# specs  actuation bottom travel distance
#       operating bottom force
#       top housing top color bottom stem pins
# switch type

sqlm_keyword = Table('keyword', metadata,
                Column('word', String(50), primary_key=True),
                Column('type', String(10)),
                Column('rank', Integer())
                )
