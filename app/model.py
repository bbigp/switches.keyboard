from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, Text, BIGINT
from app.config.database import metadata

from pydantic.main import BaseModel


class Axial(BaseModel):
    id: int=None
    name: str
    foundry: str=None
    studio: str=None
    pic: str=None
    type: str=None
    remark: str=None
    operating_force: str=None
    pre_travel: str=None
    end_force: str=None
    full_travel: str=None
    upper: str=None
    bottom: str=None
    shaft: str=None
    light_pipe: str=None
    price: int=None
    desc: str=None
    create_time: int=None
    update_time: int=None
    # buy_address: str=None 购买地址

class Option(BaseModel):
    name: str
    option_type: str


class ScTable:
    axioal = Table('axial', metadata,
                      Column('id', BIGINT()),
                      Column('name', String(20), primary_key=True),
                      Column('foundry', String(50)),
                      Column('studio', String(50)),
                      Column('pic', String(200)),
                      Column('type', String(10)),
                      Column('remark', String(50)),
                      Column('operating_force', String(10)),
                      Column('pre_travel', String(10)),
                      Column('end_force', String(10)),
                      Column('full_travel', String(10)),
                      Column('upper', String(10)),
                      Column('bottom', String(10)),
                      Column('shaft', String(10)),
                      Column('light_pipe', String(10)),
                      Column('price', Integer()),
                      Column('desc', Text()),
                      Column('create_time', BIGINT()),
                      Column('update_time', BIGINT()),
                      )

    option = Table('option', metadata,
                    Column('name', String(50), primary_key=True),
                    Column('option_type', String(10))
                    )