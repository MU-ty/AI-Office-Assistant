"""
PPT模块 Schema
"""

from typing import Optional
from pydantic import BaseModel, Field


class PPTCreateRequest(BaseModel):
    title: str = Field(..., description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")
    source_content: str = Field(..., description="输入内容")
    theme: Optional[str] = Field(None, description="主题模板")
    theme_palette: Optional[dict] = Field(None, description="自定义配色")


class PPTUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")
    theme: Optional[str] = Field(None, description="主题模板")
    theme_palette: Optional[dict] = Field(None, description="自定义配色")


class PPTGenerateRequest(BaseModel):
    tone: Optional[str] = Field("professional", description="表达风格")
    theme: Optional[str] = Field(None, description="主题模板")
    theme_palette: Optional[dict] = Field(None, description="自定义配色")


class PPTExportRequest(BaseModel):
    format: str = Field("pptx", description="导出格式")
