from pydantic import BaseModel


class TaskResultRequest(BaseModel):
    task_id: str
