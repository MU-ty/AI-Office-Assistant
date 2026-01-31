"""
文档数据库模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from app.core.database import Base


class Document(Base):
    """文档模型"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    document_type = Column(String(50), nullable=False)  # source, summary, etc.
    source_type = Column(String(50), nullable=False, default="file")  # file, text, url
    source_url = Column(String(500), nullable=True)
    file_path = Column(String(500), nullable=True)
    meta_info = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Document(id={self.id}, title={self.title})>"


class DocumentSummary(Base):
    """文档摘要模型"""
    __tablename__ = "document_summaries"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    summary_level = Column(String(50), nullable=False)  # one_liner, paragraph, full
    summary_text = Column(Text, nullable=False)
    quality_score = Column(Float, nullable=True)
    model_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<DocumentSummary(id={self.id}, document_id={self.document_id})>"
