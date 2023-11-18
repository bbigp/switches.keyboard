from pydantic.main import BaseModel



class Specs(BaseModel):
    actuation_force: str=''
    actuation_force_p: str=''
    end_force: str=''
    end_force_p: str=''
    pre_travel: str=''
    pre_travel_p: str=''
    total_travel: str=''
    total_travel_p: str=''
    pin: str=''
    top: str=''
    bottom: str=''
    stem: str=''
    spring: str=''
    light_pipe: str=''

class MksVO(BaseModel):
    id: str=''
    name: str
    pic: str=''
    studio: str=''
    manufacturer: str=''
    type: str=''
    tag: str=''
    quantity: int=0
    price: str=''
    desc: str=''
    specs: Specs=''
    create_time: int=None
    update_time: int=None
    stash: str=''
    logo: str=''
    variation: str=''

class KeywordVO(BaseModel):
    word: str=''
    type: str=''
    rank: int=0
    memo: str=''