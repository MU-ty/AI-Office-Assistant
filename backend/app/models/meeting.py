"""
会议数据库模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.core.database import Base


class Meeting(Base):
    """会议模型"""
    __tablename__ = "meetings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # 关联用户
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    date = Column(String(50), nullable=False)
    status = Column(String(20), default="draft")  # draft, ongoing, completed
    transcription = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Meeting(id={self.id}, title={self.title}, status={self.status})>"


class MeetingMinute(Base):
    """会议纪要模型"""
    __tablename__ = "meeting_minutes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # 关联用户
    meeting_id = Column(Integer, nullable=False, index=True)
    content = Column(Text, nullable=False)
    format_type = Column(String(20), nullable=False)  # markdown, pdf, docx, json
    file_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<MeetingMinute(id={self.id}, meeting_id={self.meeting_id}, format={self.format_type})>"
