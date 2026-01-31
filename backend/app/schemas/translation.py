"""
翻译模块 Schema
"""

from typing import Optional
from pydantic import BaseModel, Field


class TranslationCreateRequest(BaseModel):
    source_language: Optional[str] = Field(None, description="源语言，留空为自动检测")
    target_language: str = Field(..., description="目标语言")
    input_text: str = Field(..., description="待翻译文本")
    domain: Optional[str] = Field(None, description="领域")


class TranslationUpdateRequest(BaseModel):
    input_text: Optional[str] = Field(None, description="待翻译文本")


class TranslationRateRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="评分 1-5")
    feedback: Optional[str] = Field(None, description="反馈")


class TranslationExportRequest(BaseModel):
    format: str = Field("json", description="导出格式: json/txt")


class TerminologyCreateRequest(BaseModel):
    original_term: str = Field(..., description="术语原文")
    translation: str = Field(..., description="术语译文")
    domain: str = Field(..., description="术语领域")
