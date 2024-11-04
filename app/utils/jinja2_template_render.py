import gzip
import os
import re
from typing import Optional

from fastapi import Query, Depends
from jinja2 import FileSystemLoader, Environment
from starlette.requests import Request

from app.core.database import SqlSession
from app.core.internal import paginate_info
from app.service import switches_mapper, keyword_mapper
from app.model.assembler import convert_vo
from app.model.domain import Switches, Material
from app.utils.jinja2_filters import format_with_tolerance, format_studio_with_manufacturer


template_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'ui', 'v2')
env = Environment(loader=FileSystemLoader(template_path))
env.filters['format_with_tolerance'] = format_with_tolerance
env.filters['format_studio_with_manufacturer'] = format_studio_with_manufacturer

def determine_page_size(request: Request, size: int=Query(None)) -> int:
    user_agent = request.headers.get("User-Agent", "")
    if size is not None:
        return size
    mobile_pattern = re.compile(r"Mobi|Android|iPhone|iPad|iPod|Windows Phone", re.I)
    return 8 if bool(mobile_pattern.search(user_agent)) else 15

def render_switches_wrapper(session, page: Optional[int]=1,
        size: int=Depends(determine_page_size),
        search: str=Query(default=None, alias='s'),
        type: str=Query(default=None, alias='t'),
        stor_box: Optional[str]=None,
        manufacturer: Optional[str]=None,
        is_available: Optional[int]=1,
                            studio: Optional[str]=None, stem: Optional[str]=None,
                            top_mat: Optional[str] = None,
                            bottom_mat: Optional[str] = None
                            ):
    if is_available == 1:
        available = True
    elif is_available == 2:
        available = False
    else:
        available = None
    stmt_list, stmt_count = switches_mapper.filter((page - 1) * size, size, search, stor_box, manufacturer,
                                                       available, type=type, studio=studio, stem=stem,
                                                   top_mat=top_mat, bottom_mat=bottom_mat)
    list = session.fetchall(stmt_list, Switches)
    total = session.count(stmt_count)

    active_list_mode = False
    if (stem is not None and stem !='') or (top_mat is not None and top_mat != '') or (bottom_mat is not None and bottom_mat != ''):
        active_list_mode = True

    template = env.get_template('new/switches_wrapper.html')
    rendered_html = template.render(list=[convert_vo(i).dict() for i in list],
        page=paginate_info(total, page, size), search=search, active_list_mode=active_list_mode)
    return rendered_html
    # compressed_content = gzip.compress(rendered_html.encode('utf-8'))
    # return compressed_content

def render_switches_filter(session, request: Request):
    types, manufacturers, _, studios = keyword_mapper.fetch_text(session)
    stem_mats, top_mats, bottom_mats = init_material()
    template = env.get_template('new/switches_filter.html')
    return template.render(request=request, manufacturers=manufacturers, switches_types=types, stem_tops=stem_mats,
                           top_mats=top_mats, bottom_mats=bottom_mats)

def render_studios(session: SqlSession, request: Request):
    search = request.query_params.get('search')
    studios = keyword_mapper.fetch_random_studios(session, search, 5)
    switches = switches_mapper.fetch_switches_by_studios(session, [item.word for item in studios])

    map = {}
    for item in switches:
        map.setdefault(item.studio, []).append(convert_vo(item))

    for item in studios:
        item.switches = map.get(item.word)

    template = env.get_template('new/studios_wrapper.html')
    return template.render(request=request, studios=[studio.dict() for studio in studios])



pok = Material(id='POK', desc='POK')
pom = Material(id='POM', desc='POM')
upe = Material(id='UPE', desc='UPE')
ly = Material(id='LY', desc='LY')
pbt = Material(id='PBT', desc='PBT')
pa66 = Material(id='PA66', desc='PA66')
pc = Material(id='PC', desc='PC')
pa_all = Material(id='尼龙.PA', desc='尼龙')
def init_material():
    stem_mats = [pom, upe, pok, ly, Material(id='Y3', desc='Y3(旭华)'),
                 Material(id='P3', desc='P3(JWK)'),
                 Material(id='HPE', desc='HPE(TEC)'), Material(id='MPE', desc='MPE'),
                 Material(id='U2.U3.U4', desc='U2-U4(JJK)'), Material(id='L3.L4', desc='L3-L4(JJK)'),
                 Material(id='T2.T3.T4.T5', desc='T2-T5(HMX)')]

    top_mats = [pom, pc, upe, pa_all]
    bottom_mats = [pom, pc, upe, pa_all, pok, pbt, pa66]
    return stem_mats, top_mats, bottom_mats