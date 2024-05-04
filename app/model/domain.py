from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, Text, BIGINT, Numeric
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
    stash: str=''
    logo: str=''
    variation: str=''
    deleted: int=0
    # buy_address: str=None 购买地址


class Keyword(BaseModel):
    word: str
    type: str
    rank: int
    deleted: int=0
    create_time: int
    update_time: int
    memo: str=''

class Etd(BaseModel):
    id: str
    data: str=None
    error: str=None
    create_time: int = None
    update_time: int = None

class KeyCountBO(BaseModel):
    key: str
    count: int=0

class Switches(BaseModel):
    id: int=None
    name: str
    studio: str
    manufacturer: str=''
    pic: str = ''
    num: int=0
    type: str=''
    mark: str=''
    top_mat: str=''
    bottom_mat: str=''
    stem_mat: str=''
    spring: str=''
    actuation_force: float=None
    actuation_force_tol: str=''
    bottom_force: float=None
    bottom_force_tol: str=''
    pre_travel: float=None
    pre_travel_tol: str=''
    total_travel: float=None
    total_travel_tol: str=''
    light_style: str=''
    pins: int=None
    stor_loc_box: str=''
    stor_loc_row: int=None
    stor_loc_col: int=None
    price: str=''
    desc: str=''

    create_time: int=None
    update_time: int=None
    deleted: int=0


T_switches = Table('switches',
                 metadata,
                 Column('id', BIGINT()),
                 Column('name', String(30), primary_key=True),
                 Column('manufacturer', String(50)),
                 Column('studio', String(50)),
                 Column('pic', String(200)),
                 Column('num', Integer()),
                 Column('type', String(10)),
                 Column('mark', String(50)),

                 Column('top_mat', String(10)),
                 Column('bottom_mat', String(10)),
                 Column('stem_mat', String(10)),
                 Column('spring', String(10)),

                 Column('actuation_force', Numeric(5, 2)),
                 Column('actuation_force_tol', String(10)),
                 Column('bottom_force', Numeric(5, 2)),
                 Column('bottom_force_tol', String(10)),
                 Column('pre_travel', Numeric(5, 2)),
                 Column('pre_travel_tol', String(10)),
                 Column('total_travel', Numeric(5, 2)),
                 Column('total_travel_tol', String(10)),

                 Column('light_style', String(10)),
                 Column('pins', Integer()),
                 Column('stor_loc_box', String(10)),
                 Column('stor_loc_row', Integer()),
                 Column('stor_loc_col', Integer()),
                 Column('price', String(20)),
                 Column('desc', Text()),
                 Column('create_time', BIGINT()),
                 Column('update_time', BIGINT()),
                 Column('deleted', Integer())
                 )

# class Box(BaseModel):
#     id: int
#     ks_id: int
#     name: str
#     create_time: int = None
#     update_time: int = None
#     deleted: int=0
#
# sqlm_box = Table('box', metadata,
#                  Column('id', BIGINT()),
#                  Column('ks_id', BIGINT()),
#                  Column('name', String(50)),
#                  Column('create_time', BIGINT()),
#                  Column('update_time', BIGINT()),
#                  Column('deleted', Integer()))

sqlm_etd = Table('e_t_d', metadata,
                 Column('id', String(50), primary_key=True),
                 Column('data', Text()),
                 Column('error', Text()),
                 Column('create_time', BIGINT()),
                 Column('update_time', BIGINT()))

sqlm_keyboard_switch = Table('keyboard_switch', metadata,
                 Column('id', BIGINT()),
                 Column('name', String(30), primary_key=True),
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
                Column('stash', String(10)),
                             Column('logo', String(20)),
                             Column('variation', String(50)),
                             Column('deleted', Integer())
                 )
# specs  actuation bottom travel distance
#       operating bottom force
#       top housing top color bottom stem pins
# switch type

sqlm_keyword = Table('keyword', metadata,
                Column('word', String(50), primary_key=True),
                Column('type', String(10)),
                Column('rank', Integer()),
                Column('create_time', BIGINT()),
                Column('update_time', BIGINT()),
                Column('deleted', Integer()),
                     Column('memo', String(50))
                )

T_keyword = sqlm_keyword
