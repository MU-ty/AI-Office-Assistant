"""
学术润色任务模型 - 学术规范化处理
根据流程图第2.3.3学术规范化子模块设计
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Float
from app.core.database import Base


class PolishTask(Base):
    """学术润色任务模型"""
    __tablename__ = "polish_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, nullable=True, comment="关联的文档ID")
    original_text = Column(Text, nullable=False, comment="原始文本")
    polished_text = Column(Text, nullable=True, comment="润色后的文本")
    
    # 处理状态和类型
    status = Column(String(20), default="pending", comment="pending/processing/completed/failed")
    polish_level = Column(String(20), default="standard", comment="standard/academic/formal")
    
    # 学术规范化检查结果
    terminology_issues = Column(JSON, nullable=True, comment="术语替换问题列表")
    tense_issues = Column(JSON, nullable=True, comment="时态调整问题列表")
    style_issues = Column(JSON, nullable=True, comment="风格一致性问题列表")
    thesis_issues = Column(JSON, nullable=True, comment="论文规范问题列表")
    
    # 统计信息
    total_issues = Column(Integer, default=0, comment="总问题数")
    fixed_issues = Column(Integer, default=0, comment="已修复问题数")
    accuracy = Column(Float, default=0.0, comment="准确率")
    
    # 处理配置
    auto_fix_enabled = Column(String(5), default="false", comment="是否启用自动修复")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")
    
    def __repr__(self):
        return f"<PolishTask(id={self.id}, status={self.status}, polish_level={self.polish_level})>"


class PolishIssue(Base):
    """学术润色问题记录"""
    __tablename__ = "polish_issues"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, nullable=False, comment="关联的任务ID")
    
    # 问题信息
    issue_type = Column(String(50), nullable=False, comment="terminology/tense/style/thesis")
    severity = Column(String(20), default="medium", comment="minor/medium/major")
    location = Column(JSON, nullable=False, comment="位置信息: {start, end, line, column}")
    
    # 原始内容与建议
    original_content = Column(Text, nullable=False, comment="原始内容")
    suggested_content = Column(Text, nullable=False, comment="建议修改内容")
    reason = Column(Text, nullable=True, comment="修改原因说明")
    
    # 处理状态
    status = Column(String(20), default="pending", comment="pending/accepted/rejected/ignored")
    accepted_at = Column(DateTime, nullable=True, comment="接受时间")
    
    # 规范信息
    rule_id = Column(String(100), nullable=True, comment="应用的规范规则ID")
    confidence = Column(Float, default=0.0, comment="建议的置信度")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<PolishIssue(id={self.id}, task_id={self.task_id}, type={self.issue_type})>"
