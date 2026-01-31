"""
周报和工作日志数据模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class WorkLog(Base):
    """工作日志模型"""
    __tablename__ = "work_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)  # 用户ID，可选
    work_type = Column(String(100), nullable=False)  # 工作类型（会议、编码、文档等）
    task_description = Column(Text, nullable=False)  # 任务描述
    hours_spent = Column(Float, nullable=False)  # 花费的小时数
    log_date = Column(DateTime, default=datetime.utcnow)  # 日志日期
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<WorkLog(id={self.id}, work_type={self.work_type}, hours_spent={self.hours_spent})>"


class ReportStatus(str, enum.Enum):
    """周报状态枚举"""
    DRAFT = "draft"  # 草稿
    SUBMITTED = "submitted"  # 已提交
    APPROVED = "approved"  # 已批准
    REJECTED = "rejected"  # 已驳回


class WeeklyReport(Base):
    """周报模型"""
    __tablename__ = "weekly_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)  # 用户ID，可选
    title = Column(String(255), nullable=True)  # 周报标题
    week_start_date = Column(DateTime, nullable=False)  # 周开始日期
    week_end_date = Column(DateTime, nullable=False)  # 周结束日期
    week = Column(String(50), nullable=False, index=True)  # 周号标识（如 2025-W04）
    summary = Column(Text, nullable=True)  # 周报摘要
    content = Column(Text, nullable=True)  # 周报详细内容
    status = Column(Enum(ReportStatus), default=ReportStatus.DRAFT)  # 周报状态
    total_hours = Column(Float, default=0.0)  # 总工作小时数
    review_feedback = Column(Text, nullable=True)  # 审核反馈
    reviewer_id = Column(Integer, nullable=True)  # 审核人ID
    reviewed_at = Column(DateTime, nullable=True)  # 审核时间
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<WeeklyReport(id={self.id}, week={self.week}, status={self.status})>"
