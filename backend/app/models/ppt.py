"""
PPT项目模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.core.database import Base


class PPTProject(Base):
    """PPT项目模型"""
    __tablename__ = "ppt_projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    outline_json = Column(Text, nullable=True)
    slides_json = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=True)
    theme = Column(String(50), nullable=True)
    theme_palette = Column(Text, nullable=True)
    status = Column(String(20), default="draft")  # draft, reviewing, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<PPTProject(id={self.id}, title={self.title})>"
