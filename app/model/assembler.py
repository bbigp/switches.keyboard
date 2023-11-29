import json
from datetime import datetime

from app.model.domain import KeyboardSwitch, Keyword
from app.model.request import KeywordRequest
from app.model.vo import MksVO, KeywordVO


def convert_vo(model: KeyboardSwitch) -> MksVO:
    return MksVO(
        id=str(model.id), name=model.name, pic=model.pic, studio=model.studio, manufacturer=model.manufacturer,
        type=model.type, tag=model.tag, quantity=model.quantity, price=model.price, desc=model.desc,
        specs=json.loads(model.specs), create_time=model.create_time, update_time=model.update_time,
        stash=model.stash, logo=model.logo, variation=model.variation
    )

def convert_sqlm(mks: MksVO) -> KeyboardSwitch:
    pass

def convert_keywrod_sqlm(v: KeywordRequest) -> Keyword:
    now = datetime.now().timestamp()
    return Keyword(word=v.word, type=v.type, rank=v.rank, deleted=0, create_time=now, update_time=now, memo=v.memo)

