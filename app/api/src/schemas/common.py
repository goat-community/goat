from enum import Enum
from typing import List

from pydantic import UUID4, BaseModel


class OrderEnum(str, Enum):
    ascendent = "ascendent"
    descendent = "descendent"


class ContentIdList(BaseModel):
    ids: List[UUID4]