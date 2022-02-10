from typing import Optional

from pydantic import BaseModel


# Properties to receive via API on creation
class CustomizationCreate(BaseModel):
    type: str
    default_setting: dict
    role_id: int
    pass

class CustomizationUpdate(BaseModel):
    pass;
