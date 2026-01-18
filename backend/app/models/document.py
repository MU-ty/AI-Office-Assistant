"""文档模型"""

from sqlalchemy import Column, String, Text, Integer, ForeignKey
from .base import BaseModel


class Document(BaseModel):
    """文档数据模型"""
    
    __tablename__ = "documents"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=True)
    document_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=True)
    source_url = Column(String(500), nullable=True)
    
    def __repr__(self):
        return f"<Document {self.id}: {self.title}>"
