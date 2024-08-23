from pydantic.main import BaseModel


class KeywordRequest(BaseModel):
    word: str=''
    type: str=''
    rank: int=0
    memo: str=''
    id: str=''

class IcgbRequest(BaseModel):
    title: str=''
    href: str=''
    icgb_day: str=''
    id: int