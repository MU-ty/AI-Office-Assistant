"""
文档数据库模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Document(Base):
    """文档模型"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    document_type = Column(String(50), nullable=False)  # source, summary, etc.
    source_type = Column(String(50), nullable=False, default="file")  # file, text, url
    source_url = Column(String(500), nullable=True)
    file_path = Column(String(500), nullable=True)
    meta_info = Column(Text, nullable=True)
    
    # WeKnora 关联
    weknora_knowledge_id = Column(String(100), nullable=True)  # WeKnora 中的知识 ID
    weknora_kb_id = Column(String(100), nullable=True)         # WeKnora 中的知识库 ID
    
    # 知识库管理系统关联
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id"), nullable=True)
    directory_id = Column(Integer, ForeignKey("directories.id"), nullable=True)
    
    # 状态与版本
    status = Column(String(20), nullable=False, default="pending")  # processing status: pending, processing, completed, failed
    review_status = Column(String(20), default="draft")  # review status: draft, pending_review, published, rejected
    current_version = Column(Integer, default=1)
    
    error_message = Column(Text, nullable=True)
    processing_progress = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    user = relationship("User", back_populates="documents")
    knowledge_base = relationship("KnowledgeBase", back_populates="documents")
    directory = relationship("Directory", back_populates="documents")
    tags = relationship("Tag", secondary="document_tags", back_populates="documents")
    versions = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="document", cascade="all, delete-orphan")
    summaries = relationship("DocumentSummary", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Document(id={self.id}, title={self.title})>"


class DocumentSummary(Base):
    """文档摘要模型"""
    __tablename__ = "document_summaries"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    summary_level = Column(String(50), nullable=False)  # one_liner, paragraph, full
    summary_text = Column(Text, nullable=False)
    quality_score = Column(Float, nullable=True)
    model_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="summaries")

    def __repr__(self):
        return f"<DocumentSummary(id={self.id}, document_id={self.document_id})>"
