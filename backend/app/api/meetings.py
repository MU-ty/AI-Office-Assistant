"""
会议纪要处理模块 API

Complete endpoints with full implementation based on architecture diagram.

Endpoints:
  POST   /api/v1/meetings                               - 创建会议
  GET    /api/v1/meetings                               - 获取会议列表
  GET    /api/v1/meetings/{meeting_id}                  - 获取会议详情
  PUT    /api/v1/meetings/{meeting_id}                  - 更新会议
  DELETE /api/v1/meetings/{meeting_id}                  - 删除会议
  POST   /api/v1/meetings/{meeting_id}/upload           - 上传音视频 + 开始转录
  POST   /api/v1/meetings/{meeting_id}/transcribe       - 触发转录
  POST   /api/v1/meetings/{meeting_id}/process          - 处理转录文本 + 提取信息
  POST   /api/v1/meetings/{meeting_id}/generate-minutes - 生成纪要（多格式）
  GET    /api/v1/meetings/{meeting_id}/minutes          - 获取纪要
  POST   /api/v1/meetings/{meeting_id}/export           - 导出纪要
  POST   /api/v1/meetings/{meeting_id}/send-email       - 邮件发送纪要
  POST   /api/v1/meetings/{meeting_id}/share            - 分享纪要
  GET    /api/v1/meetings/{meeting_id}/participants     - 获取参与人
  GET    /api/v1/meetings/{meeting_id}/agendas          - 获取议程
  GET    /api/v1/meetings/{meeting_id}/decisions        - 获取决议
  GET    /api/v1/meetings/{meeting_id}/action-items     - 获取Action Items

实现说明：
- 表格标黄部分已独立成服务模块，可复用
- NLPService: 处理分句、分段、关键词提取、实体识别等
- DocumentGenerationService: 生成Markdown、PDF、Word等格式
- MeetingMinutesService: 整合所有功能的核心处理服务
"""

from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.services.meeting_service import MeetingService
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["meetings"])


# ============================================================
# 数据模型
# ============================================================

class MeetingCreate(BaseModel):
    """创建会议请求"""
    title: str = Field(..., description="会议标题")
    meeting_type: str = Field(..., description="会议类型")
    start_time: str = Field(..., description="开始时间")
    location: Optional[str] = Field(None, description="会议地点")


class ProcessTranscriptionRequest(BaseModel):
    """处理转录文本请求"""
    transcription_text: str = Field(..., description="转录的文本内容")


class GenerateMinutesRequest(BaseModel):
    """生成纪要请求"""
    meeting_data: dict = Field(..., description="会议数据")
    formats: List[str] = Field(
        default=["markdown", "json"],
        description="输出格式: markdown, pdf, docx, json"
    )


class SendEmailRequest(BaseModel):
    """邮件发送请求"""
    recipients: List[str] = Field(..., description="收件人列表")
    format: str = Field(default="pdf", description="附件格式: markdown, pdf, docx")


class ShareRequest(BaseModel):
    """分享请求"""
    share_targets: dict = Field(..., description="分享目标（邮件、企业微信、钉钉等）")


class TaskStatusResponse(BaseModel):
    """任务状态响应"""
    task_id: str
    meeting_id: str
    step: int
    is_completed: bool
    content: Optional[str] = None
    status: Optional[str] = None


# ============================================================
# 基础CRUD端点
# ============================================================

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_meeting(
    meeting_data: MeetingCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建新会议
    
    - 初始化会议记录
    - 状态: created
    """
    service = MeetingService(db)
    return await service.create_meeting(meeting_data.dict())


@router.get("/", response_model=List[dict])
async def list_meetings(
    skip: int = 0,
    limit: int = 10,
    meeting_status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    获取会议列表
    
    - 支持状态过滤: created, transcribing, processing, completed
    """
    service = MeetingService(db)
    return await service.list_meetings(skip, limit, meeting_status)


@router.get("/{meeting_id}", response_model=dict)
async def get_meeting(
    meeting_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取会议详情"""
    service = MeetingService(db)
    return await service.get_meeting(meeting_id)


@router.put("/{meeting_id}", response_model=dict)
async def update_meeting(
    meeting_id: str,
    meeting_data: MeetingCreate,
    db: AsyncSession = Depends(get_db)
):
    """更新会议信息"""
    service = MeetingService(db)
    return await service.update_meeting(meeting_id, meeting_data.dict())


@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meeting(
    meeting_id: str,
    db: AsyncSession = Depends(get_db)
):
    """删除会议"""
    service = MeetingService(db)
    await service.delete_meeting(meeting_id)


# ============================================================
# 流程图第1-3步：上传和转录
# ============================================================

@router.post("/{meeting_id}/upload", response_model=dict)
async def upload_meeting_media(
    meeting_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    上传会议音视频 - 触发转录
    
    流程图第1-3步：
    1. 上传音视频
    2. 调用转录API (Whisper/Qwen-audio等)
    3. 获取转录文本
    
    支持格式: mp3, wav, m4a, webm, mp4
    """
    service = MeetingService(db)
    return await service.upload_media(meeting_id, file)


@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """查询任务状态，供前端轮询展示流程进度"""
    service = MeetingService(db)
    return await service.get_task_status(task_id)


@router.post("/{meeting_id}/transcribe", response_model=dict)
async def transcribe_meeting(
    meeting_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    手动触发转录
    
    用于已上传但未转录的音视频
    """
    service = MeetingService(db)
    return await service.start_transcription(meeting_id)


# ============================================================
# 流程图第4-9步：NLP处理
# ============================================================

@router.post("/{meeting_id}/process", response_model=dict)
async def process_meeting_transcription(
    meeting_id: str,
    request: ProcessTranscriptionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    处理转录文本 - 提取各类信息
    
    流程图第4-9步的集中处理：
    4. 分句与分段
    5. 提取关键词 (TF-IDF)
    6. 完整转录保存
    7. 语言检测和优化
    8. 议程提取
    9. 话题划分 & 决议识别 & Action Items提取
    
    返回：
    - sentences: 分句结果
    - keywords: 关键词
    - entities: 命名实体
    - topics: 话题列表
    - agendas: 议程
    - decisions: 决议
    - action_items: Action Items
    - text_stats: 文本统计
    """
    service = MeetingService(db)
    return await service.process_transcription(
        meeting_id,
        request.transcription_text
    )


# ============================================================
# 流程图第10-19步：生成纪要
# ============================================================

@router.post("/{meeting_id}/generate-minutes", response_model=dict)
async def generate_meeting_minutes(
    meeting_id: str,
    request: GenerateMinutesRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    生成会议纪要 - 多格式支持
    
    流程图第10-19步的集中处理：
    10. 议程文本生成
    11. 决议文本生成
    12. 参与人统计
    13. 总结生成
    14. TextRank抽取重要句子
    15. 数据准备
    16. 用户分组和发送管理
    17. 导出文件生成
    18. 数据库存储
    19. 返回最终结果
    
    支持格式：
    - markdown: 可编辑的Markdown格式
    - pdf: 专业的PDF文档（使用reportlab）
    - docx: Microsoft Word格式（使用python-docx）
    - json: 结构化数据格式
    """
    service = MeetingService(db)
    return await service.generate_minutes(
        meeting_id,
        request.meeting_data,
        request.formats
    )


@router.get("/{meeting_id}/minutes", response_model=dict)
async def get_meeting_minutes(
    meeting_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    获取已生成的会议纪要
    
    返回：
    - 执行摘要
    - 议程与决议
    - Action Items
    - 完整内容（可选）
    """
    service = MeetingService(db)
    return await service.get_minutes(meeting_id)


@router.post("/{meeting_id}/export", response_model=dict)
async def export_meeting_minutes(
    meeting_id: str,
    format: str = "markdown",
    db: AsyncSession = Depends(get_db)
):
    """
    导出会议纪要
    
    支持格式: markdown, pdf, docx
    
    Returns:
    - 文件路径
    - 文件内容（某些格式）
    """
    service = MeetingService(db)
    return await service.export_minutes(meeting_id, format)


# ============================================================
# 流程图第20-23步：邮件和分享
# ============================================================

@router.post("/{meeting_id}/send-email", response_model=dict)
async def send_minutes_email(
    meeting_id: str,
    request: SendEmailRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    通过邮件发送会议纪要
    
    流程图第20步：邮件发送
    
    - 支持SMTP配置
    - 支持多收件人
    - 支持多种附件格式
    """
    service = MeetingService(db)
    return await service.send_minutes_email(
        meeting_id,
        request.recipients,
        request.format
    )


@router.post("/{meeting_id}/share", response_model=dict)
async def share_meeting_minutes(
    meeting_id: str,
    request: ShareRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    分享会议纪要
    
    流程图第21-23步：分享给相关人员和平台
    
    支持目标：
    - email: 邮件
    - wechat: 企业微信
    - dingtalk: 钉钉
    - lark: 飞书
    """
    service = MeetingService(db)
    return await service.share_minutes(meeting_id, request.share_targets)


# ============================================================
# 查询端点 - 获取纪要中的特定信息
# ============================================================

@router.get("/{meeting_id}/participants", response_model=List[dict])
async def get_meeting_participants(
    meeting_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取会议参与人列表"""
    service = MeetingService(db)
    return await service.get_participants(meeting_id)


@router.get("/{meeting_id}/agendas", response_model=List[dict])
async def get_meeting_agendas(
    meeting_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    获取会议议程
    
    从处理结果中提取的议程列表
    """
    service = MeetingService(db)
    return await service.get_agendas(meeting_id)


@router.get("/{meeting_id}/decisions", response_model=List[dict])
async def get_meeting_decisions(
    meeting_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    获取会议决议
    
    从处理结果中提取的决议列表
    """
    service = MeetingService(db)
    return await service.get_decisions(meeting_id)


@router.get("/{meeting_id}/action-items", response_model=List[dict])
async def get_meeting_action_items(
    meeting_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    获取Action Items
    
    包含：
    - content: 任务内容
    - owner: 负责人
    - due_date: 截止日期
    - status: 完成状态
    """
    service = MeetingService(db)
    return await service.get_action_items(meeting_id)
