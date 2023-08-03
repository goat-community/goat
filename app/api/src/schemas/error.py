from pydantic import BaseModel
class HTTPError(BaseModel):
    detail: str
    status_code: int
