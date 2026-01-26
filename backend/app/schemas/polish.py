"""
学术润色请求和响应的Pydantic模型
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class PolishIssueBase(BaseModel):
    """润色问题基础模型"""
    issue_type: str = Field(..., description="problem type: terminology/tense/style/thesis")
    severity: str = Field(default="medium", description="minor/medium/major")
    original_content: str = Field(..., description="original text")
    suggested_content: str = Field(..., description="suggested correction")
    reason: Optional[str] = Field(None, description="reason for the suggestion")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="confidence score")


class PolishIssueResponse(PolishIssueBase):
    """润色问题响应模型"""
    id: int
    task_id: int
    location: Dict[str, Any] = Field(..., description="position in text")
    status: str = Field(default="pending", description="pending/accepted/rejected")
    rule_id: Optional[str] = None
    accepted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PolishTaskCreate(BaseModel):
    """创建润色任务请求"""
    original_text: str = Field(..., min_length=1, max_length=50000, description="text to polish")
    polish_level: str = Field(default="standard", description="standard/academic/formal")
    auto_fix_enabled: bool = Field(default=False, description="auto fix issues")
    document_id: Optional[int] = Field(None, description="related document ID")


class PolishTaskUpdate(BaseModel):
    """更新润色任务请求"""
    original_text: Optional[str] = Field(None, description="update original text")
    polish_level: Optional[str] = None
    auto_fix_enabled: Optional[bool] = None


class PolishTaskResponse(BaseModel):
    """润色任务响应模型"""
    id: int
    document_id: Optional[int]
    original_text: str
    polished_text: Optional[str]
    status: str
    polish_level: str
    
    # 问题统计
    total_issues: int
    fixed_issues: int
    accuracy: float
    
    # 问题列表
    terminology_issues: Optional[List[PolishIssueResponse]] = None
    tense_issues: Optional[List[PolishIssueResponse]] = None
    style_issues: Optional[List[PolishIssueResponse]] = None
    thesis_issues: Optional[List[PolishIssueResponse]] = None
    
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PolishTaskListResponse(BaseModel):
    """润色任务列表响应"""
    id: int
    status: str
    polish_level: str
    total_issues: int
    fixed_issues: int
    accuracy: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AcceptSuggestionRequest(BaseModel):
    """接受建议请求"""
    issue_id: int = Field(..., description="issue ID to accept")
    feedback: Optional[str] = Field(None, description="optional feedback")


class RejectSuggestionRequest(BaseModel):
    """拒绝建议请求"""
    issue_id: int = Field(..., description="issue ID to reject")
    reason: Optional[str] = Field(None, description="reason for rejection")


class ExportResultRequest(BaseModel):
    """导出结果请求"""
    format: str = Field(default="docx", description="export format: docx/pdf/txt/html")
    include_comments: bool = Field(default=True, description="include edit comments")


class PolishStatistics(BaseModel):
    """润色统计信息"""
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    average_accuracy: float
    total_issues_found: int
    total_issues_fixed: int
    by_issue_type: Dict[str, int] = Field(default_factory=dict, description="issues count by type")
    by_severity: Dict[str, int] = Field(default_factory=dict, description="issues count by severity")
