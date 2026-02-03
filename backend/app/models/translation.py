"""
翻译任务模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from app.core.database import Base


class TranslationTask(Base):
    """翻译任务模型"""
    __tablename__ = "translation_tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    source_text = Column(Text, nullable=False)
    source_language = Column(String(20), nullable=False)
    target_language = Column(String(20), nullable=False)
    translated_text = Column(Text, nullable=True)
    domain = Column(String(50), nullable=True)
    status = Column(String(20), default="pending")  # pending, processing, completed
    quality_score = Column(Float, nullable=True)
    rating = Column(Integer, nullable=True)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<TranslationTask(id={self.id}, source={self.source_language}, target={self.target_language})>"


class TranslationTerminology(Base):
    """术语库"""
    __tablename__ = "translation_terminology"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    original_term = Column(String(200), nullable=False)
    translation = Column(String(200), nullable=False)
    domain = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<TranslationTerminology(id={self.id}, term={self.original_term})>"
