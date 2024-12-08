from datetime import datetime
from typing import Optional, List

from sqlalchemy import text, insert, select, func, update
from sqlalchemy.dialects import sqlite

from app.core.database import SqlSession
from app.model.domain import T_switches, Switches


def get_by_id(id: int):
    return text(f'select * from switches where id = {id}')

def get_by_name(name: str):
    return text(f'select * from switches where name = :name and deleted = 0').bindparams(name=name)

def save(s: Switches):
    stmt = insert(T_switches).values(s.dict())
    compiled = stmt.compile(dialect=sqlite.dialect(), compile_kwargs={'literal_binds': True})
    return str(compiled)

def delete_by_id(id):
    return text(f'update switches set deleted = 1, update_time = {int(datetime.now().timestamp())} where id = {id}')


def update_keyword(field, new_value, old_value):
    # type studio manufacturer mark stor_loc_box
    return text(f"update switches set {field} = '{new_value}' where {field} = '{old_value}' ")

def count():
    return text('select count(*) from switches where deleted = 0')

def group_by_type(type):
    # stor_loc_box studio manufacturer mark type
    return text(f'select {type} as key, count(*) as count from switches where deleted = 0 group by {type}')

def count_by_field(field, value):
    return text(f'select count(*) from switches where {field} = :value and deleted = 0').bindparams(value=value)

def update_by_id(s: Switches, id: int):
    stmt = update(T_switches).values(manufacturer=s.manufacturer, studio=s.studio, name=s.name,
                                     pic=s.pic, type=s.type, mark=s.mark, num=s.num, price=s.price, desc=s.desc,
                                     update_time=s.update_time, deleted=0,
                                     top_mat=s.top_mat, bottom_mat=s.bottom_mat, stem_mat=s.stem_mat, spring=s.spring,
                                     actuation_force=s.actuation_force, actuation_force_tol=s.actuation_force_tol,
                                     bottom_force=s.bottom_force, bottom_force_tol=s.bottom_force_tol,
                                     pre_travel=s.pre_travel, pre_travel_tol=s.pre_travel_tol,
                                     total_travel=s.total_travel, total_travel_tol=s.total_travel_tol,
                                     light_style=s.light_style, pins=s.pins,
                                     stor_loc_box=s.stor_loc_box, stor_loc_row=s.stor_loc_row,
                                     stor_loc_col=s.stor_loc_col)\
    .where(T_switches.c.id == id)
    compiled = stmt.compile(dialect=sqlite.dialect(), compile_kwargs={'literal_binds': True})
    return str(compiled)

def list(session):
    return session.fetchall(text(f"select * from switches where deleted = 0"), Switches)

def list_by_names(session, names):
    filter_names = ','.join(f"'{name}'" for name in names)
    return session.fetchall(text(f"select * from switches where deleted = 0 and name in ({filter_names})"), Switches)

def fetch_hot(session, size:int=2):
    return session.fetchall(text(f"select * from switches where deleted = 0 and "
                                 f"stor_loc_box != '' and stor_loc_box is not null "
                                 f"ORDER BY RANDOM() limit {size}"), Switches)

def fetch_switches_by_studios(session: SqlSession, studios: List[str]) -> List[Switches]:
    s = ','.join(f"'{item}'" for item in studios)
    return session.fetchall(f"select * from switches where deleted=0 and studio in ({s})", Switches)

def filter(start: Optional[int]=0,
           length: Optional[int]=10,
           search: Optional[str]=None,
           stor_box: Optional[str]=None,
           manufacturer: Optional[str]=None,
           is_available: Optional[bool]=None,
           type: Optional[str]=None,
           studio: Optional[str]=None,
           stem: Optional[str]=None,
           top_mat: Optional[str] = None,
           bottom_mat: Optional[str] = None,
min_travel: Optional[int]=None,
                          max_travel: Optional[int]=None,
                          min_total_travel: Optional[int]=None,
                          max_total_travel: Optional[int]=None,
min_force: Optional[int]=None,
                          max_force: Optional[int]=None,
                          min_total_force: Optional[int]=None,
                          max_total_force: Optional[int]=None
           ):
    base = select('*') \
        .select_from(text('switches')) \
        .where(text('deleted = 0')) \
        .order_by(text('update_time desc')) \
        .limit(length) \
        .offset(start)
    count = select(func.count('*')).select_from(text('switches')).where(text('deleted = 0'))

    filter = Filter(base, count) \
        .or_build('manufacturer', manufacturer) \
        .search_build(['name', 'studio', 'manufacturer', 'mark'], search)

    if studio is not None and studio != '':
        filter.append_where(text(f"studio = '{studio}' "))

    if min_travel is not None:
        filter.append_where(f"pre_travel >= {min_travel / 10} ")
    if max_travel is not None:
        filter.append_where(f"pre_travel <= {max_travel / 10} ")
    if min_total_travel is not None:
        filter.append_where(f"total_travel >= {min_total_travel / 10} ")
    if max_total_travel is not None:
        filter.append_where(f"total_travel <= {max_total_travel / 10} ")
    if min_force is not None:
        filter.append_where(f"actuation_force >= {min_force}")
    if max_force is not None:
        filter.append_where(f"actuation_force <= {max_force}")
    if min_total_force is not None:
        filter.append_where(f"bottom_force >= {min_total_force}")
    if max_total_force is not None:
        filter.append_where(f"bottom_force <= {max_total_force}")

    if stem is not None and stem != '':
        _list = []
        for s in stem.split(','):
            _list.extend(s.split('.'))
        filter.or_build('stem_mat', ','.join(_list), like=True)

    if top_mat is not None and top_mat != '':
        _list = []
        for s in top_mat.split(','):
            _list.extend(s.split('.'))
        filter.or_build('top_mat', ','.join(_list), like=True)

    if bottom_mat is not None and bottom_mat != '':
        _list = []
        for s in bottom_mat.split(','):
            _list.extend(s.split('.'))
        filter.or_build('bottom_mat', ','.join(_list), like=True)

    if is_available is None:
        pass
    elif is_available is True:
        filter.append_where(text("stor_loc_box != '' and stor_loc_box is not null"))
    else:
        filter.append_where(text("(stor_loc_box = '' or stor_loc_box is null)"))

    if stor_box is not None and stor_box != '':
        filter.append_where(text(f"stor_loc_box = '{stor_box}'"))
    if type is not None and type != '':
        filter.append_where(text(f"type = '{type}' "))
    return filter.build()



class Filter():
    def __init__(self, base=None, count=None):
        self.base = base
        self.count = count

    def limit(self, limit):
        self.base = self.base.limit(limit)
        return self

    def offset(self, offset):
        self.base = self.base.offset(offset)
        return self

    def search_build(self, fields, search):
        if search is None or search == '':
            return self
        delimiter = ' or ' if ' or ' in search else ' and '
        search_terms = search.split(delimiter)

        sql_params = {}
        str_list = []
        for i, term in enumerate(search_terms):
            conditions = " or ".join(f"{field} like :search_{i}" for field in fields)
            str_list.append(f"({conditions})")
            sql_params[f'search_{i}'] = f'%{term.strip()}%'

        sql_text = text(f" {delimiter} ".join(str_list)).bindparams(**sql_params)
        return self.append_where(sql_text)

    def or_build(self, field: str, cond_str: str, like: bool=False):
        """
        build or语句
        Args:
            field: 字段名字
            cond_str: 进行or的条件，用,分割
            like: 是否进行like匹配

        Returns:
            filter
        """
        if cond_str is None or cond_str == '':
            return self
        cond_list = cond_str.split(',')
        condition_list = []
        params = {}
        for i, _c in enumerate(cond_list):
            if like:
                condition_list.append(f"{field} like '%{_c}%'")
            else:
                condition_list.append(f"{field} = '{_c}' ")
        or_condition = ' OR '.join(condition_list)
        return self.append_where(text(f'({or_condition})'))

    def append_where(self, condtion):
        if isinstance(condtion, str):
            condtion = text(condtion)
        if self.base is not None:
            self.base = self.base.where(condtion)
        if self.count is not None:
            self.count = self.count.where(condtion)
        return self

    def build(self):
        return self.base, self.count