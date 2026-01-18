from typing import Any, Optional
from pydantic import BaseModel, ConfigDict
from ..models.task import TaskStatus, TaskType


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    task_type: TaskType
    input_data: Optional[str] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    input_data: Optional[str] = None
    output_data: Optional[str] = None
    error_message: Optional[str] = None


class TaskInDB(TaskBase):
    id: int
    user_id: int
    status: TaskStatus
    output_data: Optional[str] = None
    error_message: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class Task(TaskInDB):
    pass
