"""任务/工作项模型"""

from sqlalchemy import Column, String, Text, Integer, ForeignKey, Enum
from enum import Enum as PyEnum
from .base import BaseModel


class TaskStatus(str, PyEnum):
    """任务状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskType(str, PyEnum):
    """任务类型"""
    MEETING_MINUTES = "meeting_minutes"
    LITERATURE_SUMMARY = "literature_summary"
    PAPER_POLISH = "paper_polish"
    TRANSLATION = "translation"
    PPT_GENERATION = "ppt_generation"
    WEEKLY_REPORT = "weekly_report"


class Task(BaseModel):
    """任务数据模型"""
    
    __tablename__ = "tasks"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    task_type = Column(String(50), nullable=False, index=True)
    status = Column(String(50), default=TaskStatus.PENDING, nullable=False, index=True)
    input_data = Column(Text, nullable=True)
    output_data = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<Task {self.id}: {self.title}>"
