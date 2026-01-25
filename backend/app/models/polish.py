"""
波兰文本处理任务模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.core.database import Base


class PolishTask(Base):
    """波兰文本处理任务模型"""
    __tablename__ = "polish_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    original_text = Column(Text, nullable=False)
    polished_text = Column(Text, nullable=True)
    status = Column(String(20), default="pending")  # pending, processing, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<PolishTask(id={self.id}, status={self.status})>"
