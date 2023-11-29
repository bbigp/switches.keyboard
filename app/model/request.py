from pydantic.main import BaseModel


class KeywordRequest(BaseModel):
    word: str=''
    type: str=''
    rank: int=0
    memo: str=''