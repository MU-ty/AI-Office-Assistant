"""
会议纪要处理模块 API

Endpoints:
  POST   /api/v1/meetings                          - 创建会议
  GET    /api/v1/meetings                          - 获取会议列表
  GET    /api/v1/meetings/{meeting_id}             - 获取会议详情
  PUT    /api/v1/meetings/{meeting_id}             - 更新会议
  DELETE /api/v1/meetings/{meeting_id}             - 删除会议
  POST   /api/v1/meetings/{meeting_id}/upload      - 上传音视频
  POST   /api/v1/meetings/{meeting_id}/transcribe  - 转录音频
  GET    /api/v1/meetings/{meeting_id}/minutes     - 获取纪要
  POST   /api/v1/meetings/{meeting_id}/export      - 导出纪要
  GET    /api/v1/meetings/{meeting_id}/participants     - 获取参与人
  GET    /api/v1/meetings/{meeting_id}/agendas         - 获取议程
  GET    /api/v1/meetings/{meeting_id}/decisions       - 获取决议
  GET    /api/v1/meetings/{meeting_id}/action-items    - 获取Action Items
"""

from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.services.meeting_service import MeetingService
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_meeting(
    title: str,
    meeting_type: str,
    start_time: str,
    db: AsyncSession = Depends(get_db)
):
    """创建新会议"""
    service = MeetingService(db)
    return await service.create_meeting({
        "title": title,
        "meeting_type": meeting_type,
        "start_time": start_time
    })


@router.get("/")
async def list_meetings(
    skip: int = 0,
    limit: int = 10,
    status: str = None,
    db: AsyncSession = Depends(get_db)
):
    """获取会议列表"""
    service = MeetingService(db)
    return await service.list_meetings(skip, limit, status)


@router.get("/{meeting_id}")
async def get_meeting(
    meeting_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取会议详情"""
    service = MeetingService(db)
    return await service.get_meeting(meeting_id)


@router.put("/{meeting_id}")
async def update_meeting(
    meeting_id: str,
    title: str = None,
    db: AsyncSession = Depends(get_db)
):
    """更新会议信息"""
    service = MeetingService(db)
    return await service.update_meeting(meeting_id, {"title": title})


@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meeting(
    meeting_id: str,
    db: AsyncSession = Depends(get_db)
):
    """删除会议"""
    service = MeetingService(db)
    await service.delete_meeting(meeting_id)


@router.post("/{meeting_id}/upload")
async def upload_meeting_media(
    meeting_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """上传会议音视频"""
    service = MeetingService(db)
    return await service.upload_media(meeting_id, file)


@router.post("/{meeting_id}/transcribe")
async def transcribe_meeting(
    meeting_id: str,
    db: AsyncSession = Depends(get_db)
):
    """触发会议音频转录"""
    service = MeetingService(db)
    return await service.start_transcription(meeting_id)


@router.get("/{meeting_id}/minutes")
async def get_meeting_minutes(
    meeting_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取会议纪要"""
    service = MeetingService(db)
    return await service.get_minutes(meeting_id)


@router.post("/{meeting_id}/export")
async def export_meeting_minutes(
    meeting_id: str,
    format: str = "markdown",
    db: AsyncSession = Depends(get_db)
):
    """导出会议纪要"""
    service = MeetingService(db)
    return await service.export_minutes(meeting_id, format)


@router.get("/{meeting_id}/participants")
async def get_meeting_participants(
    meeting_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取会议参与人"""
    service = MeetingService(db)
    return await service.get_participants(meeting_id)


@router.get("/{meeting_id}/agendas")
async def get_meeting_agendas(
    meeting_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取会议议程"""
    service = MeetingService(db)
    return await service.get_agendas(meeting_id)


@router.get("/{meeting_id}/decisions")
async def get_meeting_decisions(
    meeting_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取会议决议"""
    service = MeetingService(db)
    return await service.get_decisions(meeting_id)


@router.get("/{meeting_id}/action-items")
async def get_meeting_action_items(
    meeting_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取会议Action Items"""
    service = MeetingService(db)
    return await service.get_action_items(meeting_id)
