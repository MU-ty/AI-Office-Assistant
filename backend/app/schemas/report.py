"""
周报和工作日志相关的数据验证模型
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


# ============================================================
# 工作日志 Schema
# ============================================================

class WorkLogCreate(BaseModel):
    """创建工作日志请求模型"""
    work_type: str = Field(..., min_length=1, max_length=100, description="工作类型")
    task_description: str = Field(..., min_length=1, description="任务描述")
    hours_spent: float = Field(..., gt=0, le=24, description="花费的小时数")
    log_date: Optional[datetime] = Field(default=None, description="日志日期")


class WorkLogUpdate(BaseModel):
    """更新工作日志请求模型"""
    work_type: Optional[str] = Field(None, max_length=100)
    task_description: Optional[str] = None
    hours_spent: Optional[float] = Field(None, gt=0, le=24)


class WorkLogResponse(BaseModel):
    """工作日志响应模型"""
    id: int
    user_id: Optional[int] = None
    work_type: str
    task_description: str
    hours_spent: float
    log_date: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================
# 周报 Schema
# ============================================================

class WeeklyReportCreate(BaseModel):
    """创建周报请求模型"""
    title: Optional[str] = Field(None, max_length=255, description="周报标题")
    week_start_date: datetime = Field(..., description="周开始日期")
    week_end_date: datetime = Field(..., description="周结束日期")
    ai_polish: Optional[bool] = Field(False, description="是否使用AI扩写润色")


class WeeklyReportUpdate(BaseModel):
    """更新周报请求模型"""
    title: Optional[str] = Field(None, max_length=255)
    summary: Optional[str] = None
    content: Optional[str] = None


class WeeklyReportReview(BaseModel):
    """周报审核请求模型"""
    status: str = Field(..., description="审核状态 (approved/rejected)")
    review_feedback: Optional[str] = Field(None, description="审核反馈")


class WeeklyReportResponse(BaseModel):
    """周报响应模型"""
    id: int
    user_id: Optional[int] = None
    title: Optional[str] = None
    week: str
    week_start_date: datetime
    week_end_date: datetime
    summary: Optional[str] = None
    status: str
    total_hours: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WeeklyReportDetailResponse(WeeklyReportResponse):
    """周报详情响应模型"""
    content: Optional[str] = None
    review_feedback: Optional[str] = None
    reviewer_id: Optional[int] = None
    reviewed_at: Optional[datetime] = None


class WeeklyReportListResponse(BaseModel):
    """周报列表响应模型"""
    total: int
    skip: int
    limit: int
    items: list[WeeklyReportResponse]
