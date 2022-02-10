from typing import Any, List, Optional

from pydantic import BaseModel, EmailStr


# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    organization_id: int = None
    is_active: Optional[bool] = True
    name: Optional[str] = None
    surname: Optional[str] = None
    roles: List[Any] = []
    study_areas: List[Any] = []


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str
    email: EmailStr


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDBBase(UserBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str
