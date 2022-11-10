from lib2to3.pytree import Base
from pydantic import BaseModel
from src.resources.enums import SystemStatus


class SystemStatusModel(BaseModel):
    status: SystemStatus
