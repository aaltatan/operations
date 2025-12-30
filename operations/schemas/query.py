from pydantic import BaseModel


class BaseQueryParams(BaseModel):
    q: str = ""
    offset: int = 0
    limit: int = 10
