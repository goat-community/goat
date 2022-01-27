from typing import Optional

from pydantic import BaseModel


# Shared properties
class CustomizationBase(BaseModel):
    type: str
    default_setting: dict

# Properties to receive via API on creation
class CustomizationCreate(CustomizationBase):
    role_name: str
    pass

# Properties to receive via API on update
class CustomizationUpdate(CustomizationBase):
    pass
