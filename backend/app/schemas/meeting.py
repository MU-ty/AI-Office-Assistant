"""
会议相关的数据验证模型
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class ProcessTranscriptionRequest(BaseModel):
    """转录处理请求模型"""
    meeting_id: int
    text: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "meeting_id": 1,
                "text": "会议转录内容..."
            }
        }


class GenerateMinutesRequest(BaseModel):
    """生成纪要请求模型"""
    meeting_id: int
    formats: List[str] = ["markdown", "json"]  # markdown, pdf, docx, json
    
    class Config:
        json_schema_extra = {
            "example": {
                "meeting_id": 1,
                "formats": ["markdown", "json"]
            }
        }


class SendEmailRequest(BaseModel):
    """发送邮件请求模型"""
    meeting_id: int
    recipients: List[str]
    format: str = "markdown"
    
    class Config:
        json_schema_extra = {
            "example": {
                "meeting_id": 1,
                "recipients": ["user@example.com"],
                "format": "markdown"
            }
        }


class ShareRequest(BaseModel):
    """分享请求模型"""
    meeting_id: int
    share_targets: List[str]  # weixin, dingtalk, lark, email
    
    class Config:
        json_schema_extra = {
            "example": {
                "meeting_id": 1,
                "share_targets": ["weixin", "email"]
            }
        }


class MeetingCreate(BaseModel):
    """创建会议请求模型"""
    title: str
    description: Optional[str] = None
    date: Optional[str] = None
    participants: Optional[List[str]] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Q1产品规划会",
                "description": "讨论Q1产品规划",
                "date": "2026-01-25",
                "participants": ["王总", "李建"]
            }
        }


class MeetingResponse(BaseModel):
    """会议响应模型"""
    id: int
    title: str
    description: Optional[str] = None
    date: str
    status: str  # draft, ongoing, completed
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Q1产品规划会",
                "description": "讨论Q1产品规划",
                "date": "2026-01-25",
                "status": "completed",
                "created_at": "2026-01-25T10:00:00",
                "updated_at": "2026-01-25T12:00:00"
            }
        }
