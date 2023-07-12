from typing import List, Optional

from pydantic import BaseModel, EmailStr

from src.db import models
from src.resources.enums import LanguageEnum


class UserBase(models.user.UserBase):
    roles: List[str] = []
    study_areas: List[int] = []


class UserCreate(UserBase):
    password: str
    is_active: bool = False
    language_preference: Optional[LanguageEnum] = LanguageEnum.de
    newsletter: bool = False
    occupation: Optional[str]
    domain: Optional[str]


class UserCreateDemo(BaseModel):
    name: str
    surname: str
    email: EmailStr
    password: str
    newsletter: bool = False
    occupation: str
    domain: str
    language_preference: Optional[LanguageEnum] = LanguageEnum.de

    class Config:
        extra = "forbid"


class UserUpdate(UserBase):
    name: Optional[str] = None
    surname: Optional[str] = None
    email: EmailStr = None
    password: Optional[str] = None
    organization_id: Optional[int] = None
    roles: Optional[List[str]] = None
    study_areas: Optional[List[int]] = None
    is_active: bool = False


class UserStudyAreaList(BaseModel):
    id: int
    name: str


class UserPreference(BaseModel):
    language_preference: Optional[LanguageEnum]
    active_study_area_id: Optional[int]

    class Config:
        extra = "forbid"


"""
Body of the request
"""
request_examples = {
    "create": {
        "name": "John",
        "surname": "Doe",
        "email": "john.doe@email.com",
        "password": "secret",
        "roles": ["user"],
        "study_areas": [91620000],  # muenchen
        "active_study_area_id": 91620000,
        "organization_id": 4,
        "active_data_upload_ids": [],
        "newsletter": False,
        "occupation": "Student",
        "domain": "Urban Planning",
        "is_active": True,
        "storage": 512000,
        "limit_scenarios": 50,
        "language_preference": "de",
    },
    "update": {
        "name": "Kevin",
        "surname": "Cross",
        "email": "kevin.cross@email.com",
        "password": "secret",
        "roles": ["user"],
        "study_areas": [91620000],
        "active_study_area_id": 91620000,
        "organization_id": 4,
        "active_data_upload_ids": [],
        "is_active": True,
        "storage": 512000,
        "limit_scenarios": 50,
        "language_preference": "de",
    },
    "create_demo_user": {
        "name": "John",
        "surname": "Doe",
        "email": "john.doe@email.com",
        "password": "secret",
        "newsletter": False,
        "occupation": "Student",
        "domain": "Urban Planning",
        "language_preference": "de",
    },
    "update_user_preference": {
        "language_preference": {
            "summary": "Update language preference",
            "value": {
                "language_preference": "en",
            },
        },
        "study_area_preference": {
            "summary": "Update study area preference",
            "value": {
                "active_study_area_id": 1,
            },
        },
        "language_study_area_preference": {
            "summary": "Both language and study area preferences",
            "value": {
                "language_preference": "en",
                "active_study_area_id": 1,
            },
        },
    },
}
