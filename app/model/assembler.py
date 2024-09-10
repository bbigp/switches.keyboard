import json
import re
from datetime import datetime

import markdown

from app.model.domain import KeyboardSwitch, Keyword, Switches
from app.model.request import KeywordRequest
from app.model.vo import MksVO, KeywordVO, SwitchVO


def convert_vo(model: Switches) -> SwitchVO:
    if model.pic is None or model.pic == '':
        model.pic = '/bfs/fs/dummy_image.jpg'
    images, html_content = _markdown_html(model.desc)
    return SwitchVO(id=str(model.id),
                    name=model.name,
                    studio=model.studio,
                    manufacturer=model.manufacturer,
                    pic=model.pic,
                    num=model.num,
                    type=model.type,
                    mark=model.mark,
                    top_mat=model.top_mat,
                    bottom_mat=model.bottom_mat,
                    stem_mat=model.stem_mat,
                    spring=model.spring,
                    actuation_force=model.actuation_force,
                    actuation_force_tol=model.actuation_force_tol,
                    bottom_force=model.bottom_force,
                    bottom_force_tol=model.bottom_force_tol,
                    pre_travel=model.pre_travel,
                    pre_travel_tol=model.pre_travel_tol,
                    total_travel=model.total_travel,
                    total_travel_tol=model.total_travel_tol,
                    light_style=model.light_style,
                    pins=model.pins,
                    stor_loc_box=model.stor_loc_box,
                    stor_loc_row=model.stor_loc_row,
                    stor_loc_col=model.stor_loc_col,
                    price=model.price,
                    desc=model.desc,
                    create_time=model.create_time,
                    update_time=model.update_time,
                    deleted=model.deleted,
                    html_desc=html_content,
                    images=images
                    )

def _markdown_html(md_text):
    image_pattern = r'!\[.*?\]\((.*?)\)'
    images = re.findall(image_pattern, md_text)
    md_without_images = re.sub(image_pattern, '', md_text)
    html_content = markdown.markdown(md_without_images)
    return images, html_content

def convert_sqlm(mks: MksVO) -> KeyboardSwitch:
    pass

def convert_keywrod_sqlm(v: KeywordRequest) -> Keyword:
    now = datetime.now().timestamp()
    return Keyword(word=v.word, type=v.type, rank=v.rank, deleted=0, create_time=now, update_time=now, memo=v.memo)



def convert_swtiches(model: KeyboardSwitch) -> Switches:
    specs=json.loads(model.specs)
    pins = None
    if specs['pin'] == '三脚':
        pins = 3
    elif specs['pin'] == '五脚':
        pins = 5

    act_force = format_base_value(specs['actuation_force'])
    bot_force = format_base_value(specs['end_force'])
    act_dist = format_base_value(specs['pre_travel'])
    total_dist = format_base_value(specs['total_travel'])

    act_force_tol = append_add_sub(specs['actuation_force_p'])
    bot_force_tol = append_add_sub(specs['end_force_p'])
    act_dist_tol = append_add_sub(specs['pre_travel_p'])
    total_dist_tol = append_add_sub(specs['total_travel_p'])

    if is_whole_fomart(specs['actuation_force']):
        act_force, act_force_tol = format_base_value_tol(specs['actuation_force'])
    if is_whole_fomart(specs['end_force']):
        bot_force, bot_force_tol = format_base_value_tol(specs['end_force'])
    if is_whole_fomart(specs['pre_travel']):
        bot_force, bot_force_tol = format_base_value_tol(specs['pre_travel'])
    if is_whole_fomart(specs['total_travel']):
        bot_force, bot_force_tol = format_base_value_tol(specs['total_travel'])

    print(f'{act_force} {bot_force} {act_dist} {total_dist} {act_force_tol}  {bot_force_tol}  {act_dist_tol} {total_dist_tol}')
    return Switches(
        id=model.id,
        name=model.name, studio=model.studio, manufacturer=model.manufacturer,
        pic=model.pic, num=model.quantity, type=model.type, mark=model.logo,
        top_mat=specs['top'], bottom_mat=specs['bottom'], stem_mat=specs['stem'], spring=specs['spring'],
        actuation_force=act_force, actuation_force_tol=act_force_tol,
        bottom_force=bot_force, bottom_force_tol=bot_force_tol,
        pre_travel=act_dist, pre_travel_tol=act_dist_tol,
        total_travel=total_dist, total_travel_tol=total_dist_tol,
        light_style=specs['light_pipe'], pins=pins,
        stor_loc_box=model.stash, price=model.price,
        desc=model.desc,
        create_time=model.create_time, update_time=model.update_time, deleted=model.deleted
    )

def is_whole_fomart(d1):
    if '-' in d1:
        return True
    if len(d1) >= 3 and '.' not in d1:
        return True
    else:
        return False

def format_base_value_tol(data):
    if '.' not in data:
        return float(data[:2]), data[2:]
    else:
        return float(data[:3]), data[3:]

def format_base_value(data):
    if data == '' or data is None:
        return None
    elif len(data) >= 3 and '.' not in data:
        print(f'=======> {data}')
    elif '-' in data:
        print(f'======> -{data}')
    else:
        return float(data)

def append_add_sub(data):
    if data == '' or data is None:
        return ''
    else:
        return '±' + data