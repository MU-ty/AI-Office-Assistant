"""
文献摘要模块 Schema
"""

from typing import Optional
from pydantic import BaseModel, Field


class DocumentCreateText(BaseModel):
    title: Optional[str] = Field(None, description="文档标题")
    content: str = Field(..., description="文档文本内容")
    kb_id: Optional[str] = Field(None, description="知识库ID")


class DocumentCreateUrl(BaseModel):
    title: Optional[str] = Field(None, description="文档标题")
    url: str = Field(..., description="网页URL")
    kb_id: Optional[str] = Field(None, description="知识库ID")


class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, description="文档标题")
    category: Optional[str] = Field(None, description="文档分类")


class DocumentSummaryRequest(BaseModel):
    summary_level: str = Field("paragraph", description="摘要级别")


class DocumentSearchRequest(BaseModel):
    query: str = Field(..., description="搜索文本")
    knowledge_base_ids: list[str] = Field(default=[], description="知识库ID列表")
    limit: int = Field(10, ge=1, le=100, description="返回数量")
