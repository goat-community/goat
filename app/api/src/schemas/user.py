from typing import List, Optional

from pydantic import EmailStr

from src.db import models


class UserBase(models.UserBase):
    roles: List[str] = []
    study_areas: List[int] = []


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    name: Optional[str] = None
    surname: Optional[str] = None
    email: EmailStr = None
    password: Optional[str] = None
    organization_id: Optional[int] = None
    roles: Optional[List[str]] = None
    study_areas: Optional[List[int]] = None


"""
Body of the request
"""
request_examples = {
    "create": {
        "name": "John",
        "surname": "Doe",
        "email": "john.doe@email.com",
        "password": "secret",
        "roles": ["superuser", "user"],
        "study_areas": [1],
        "active_study_area": 1,
        "organization_id": 1,
        "active_data_upload_ids": [],
        "is_active": True,
        "storage": 500000,
    },
    "update": {
        "name": "Kevin",
        "surname": "Cross",
        "email": "kevin.cross@email.com",
        "password": "updated_secret",
        "roles": ["user"],
        "study_areas": [],
        "active_study_area": 1,
        "organization_id": 1,
        "is_active": False,
        "storage": 1500000,
    },
}
