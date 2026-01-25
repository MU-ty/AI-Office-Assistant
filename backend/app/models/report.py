"""
周报模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.core.database import Base


class WeeklyReport(Base):
    """周报模型"""
    __tablename__ = "weekly_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    week = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<WeeklyReport(id={self.id}, week={self.week})>"
