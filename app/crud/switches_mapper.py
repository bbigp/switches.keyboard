from datetime import datetime
from typing import Optional

from sqlalchemy import text, insert, select, func, update

from app.model.domain import T_switches, Switches


def get_by_id(id: int):
    return text(f'select * from switches where id = {id}')

def get_by_name(name: str):
    return text(f'select * from switches where name = :name and deleted = 0').bindparams(name=name)

def save(s: Switches):
    return insert(T_switches).values(s.dict())

def delete_by_id(id):
    return text(f'update switches set deleted = 1, update_time = {int(datetime.now().timestamp())} where id = {id}')


def update_keyword(field, new_value, old_value):
    # type studio manufacturer mark stor_loc_box
    return text(f'update switches set {field} = :new_value where {field} = :old_value').bindparams(new_value=new_value, old_value=old_value)

def count():
    return text('select count(*) from switches where deleted = 0')

def group_by_type(type):
    # stor_loc_box studio manufacturer mark type
    return text(f'select {type} as key, count(*) as count from switches where deleted = 0 group by {type}')

def count_by_field(field, value):
    return text(f'select count(*) from switches where {field} = :value and deleted = 0').bindparams(value=value)

def update_by_id(s: Switches, id: int):
    return update(T_switches).values(manufacturer=s.manufacturer, studio=s.studio, name=s.name,
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

def list(session):
    return session.fetchall(text(f"select * from switches where deleted = 0"), Switches)

def fetch_hot(session, size:int=2):
    return session.fetchall(text(f"select * from switches where deleted = 0 ORDER BY RANDOM() limit {size}"), Switches)

def filter(start: Optional[int]=0,
           length: Optional[int]=10,
           search: Optional[str]=None,
           stor_box: Optional[str]=None,
           manufacturer: Optional[str]=None,
           is_available: Optional[bool]=None,
           type: Optional[str]=None):
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

    def or_build(self, field, cond_str):
        if cond_str is None or cond_str == '':
            return self
        cond_list = cond_str.split(',')
        condition_list = []
        params = {}
        for i, _c in enumerate(cond_list):
            param_name = f'bsearch_{i}'
            condition_list.append(f"{field} = :{param_name}")
            params[param_name] = _c.strip()
        or_condition = ' OR '.join(condition_list)
        cond = text(f'({or_condition})').bindparams(**params)
        return self.append_where(cond)

    def append_where(self, condtion):
        if self.base is not None:
            self.base = self.base.where(condtion)
        if self.count is not None:
            self.count = self.count.where(condtion)
        return self

    def build(self):
        return self.base, self.count