"""
翻译任务模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.core.database import Base


class TranslationTask(Base):
    """翻译任务模型"""
    __tablename__ = "translation_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    source_text = Column(Text, nullable=False)
    source_language = Column(String(20), nullable=False)
    target_language = Column(String(20), nullable=False)
    translated_text = Column(Text, nullable=True)
    status = Column(String(20), default="pending")  # pending, processing, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<TranslationTask(id={self.id}, source={self.source_language}, target={self.target_language})>"
