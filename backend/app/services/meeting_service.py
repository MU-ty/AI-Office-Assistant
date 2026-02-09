"""
会议纪要服务层
提供会议处理相关业务逻辑，集成NLP和文档生成服务
"""

import json
from typing import List, Optional, Dict, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from fastapi import UploadFile, HTTPException
from datetime import datetime

from app.utils.logger import get_logger
from app.models.meeting import Meeting, MeetingMinutes
from app.services.meeting_minutes_service import MeetingMinutesService
from app.services.stream_service import StreamService, StreamProvider
from app.core.config import settings

logger = get_logger(__name__)


class MeetingService:
    """会议纪要服务 - 管理会议生命周期"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.minutes_service = MeetingMinutesService(db)
    
    async def create_meeting(self, meeting_data: Dict, user_id: int) -> dict:
        """
        创建会议
        
        Args:
            meeting_data: 包含title, meeting_type, start_time等信息
            user_id: 用户ID
            
        Returns:
            创建的会议信息
        """
        try:
            logger.info(f"创建会议: {meeting_data.get('title')}, user_id={user_id}")
            
            meeting = Meeting(
                user_id=user_id,
                title=meeting_data.get("title") or "未命名会议",
                description=meeting_data.get("description"),
                date=meeting_data.get("date") or datetime.now().isoformat(),
                status="created",
                transcription=meeting_data.get("transcription")
            )
            self.db.add(meeting)
            await self.db.commit()
            await self.db.refresh(meeting)
            
            logger.info(f"会议创建成功: id={meeting.id}")
            return self._format_meeting(meeting)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"创建会议失败: {e}")
            raise
    
    async def list_meetings(
        self, skip: int, limit: int, status: Optional[str], user_id: int
    ) -> List[dict]:
        """
        获取会议列表
        
        Args:
            skip: 分页偏移
            limit: 分页大小
            status: 过滤状态（created, processing, completed）
            user_id: 用户ID
            
        Returns:
            会议列表
        """
        try:
            logger.info(f"查询会议列表: skip={skip}, limit={limit}, status={status}, user_id={user_id}")
            
            query = select(Meeting).where(Meeting.user_id == user_id)
            
            if status:
                query = query.where(Meeting.status == status)
            
            query = query.order_by(Meeting.created_at.desc()).offset(skip).limit(limit)
            
            result = await self.db.execute(query)
            meetings = result.scalars().all()
            
            return [self._format_meeting(m) for m in meetings]
        except Exception as e:
            logger.error(f"查询会议列表失败: {e}")
            return []
    
    async def get_meeting(self, meeting_id: int, user_id: int) -> dict:
        """
        获取会议详情
        
        Args:
            meeting_id: 会议ID
            user_id: 用户ID
            
        Returns:
            会议详情
        """
        try:
            logger.info(f"获取会议详情: meeting_id={meeting_id}, user_id={user_id}")
            
            query = select(Meeting).where(
                and_(Meeting.id == meeting_id, Meeting.user_id == user_id)
            )
            result = await self.db.execute(query)
            meeting = result.scalars().first()
            
            if not meeting:
                raise ValueError("会议不存在或无权访问")
            
            return self._format_meeting(meeting)
        except Exception as e:
            logger.error(f"获取会议详情失败: {e}")
            raise
    
    async def update_meeting(self, meeting_id: int, meeting_data: Dict, user_id: int) -> dict:
        """
        更新会议信息
        
        Args:
            meeting_id: 会议ID
            meeting_data: 更新的数据
            user_id: 用户ID
            
        Returns:
            更新后的会议信息
        """
        try:
            logger.info(f"更新会议: meeting_id={meeting_id}, user_id={user_id}")
            
            query = select(Meeting).where(
                and_(Meeting.id == meeting_id, Meeting.user_id == user_id)
            )
            result = await self.db.execute(query)
            meeting = result.scalars().first()
            
            if not meeting:
                raise ValueError("会议不存在或无权访问")
            
            # 更新允许的字段
            if "title" in meeting_data:
                meeting.title = meeting_data["title"]
            if "description" in meeting_data:
                meeting.description = meeting_data["description"]
            if "status" in meeting_data:
                meeting.status = meeting_data["status"]
            if "transcription" in meeting_data:
                meeting.transcription = meeting_data["transcription"]
            
            meeting.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(meeting)
            
            logger.info(f"会议更新成功: id={meeting.id}")
            return self._format_meeting(meeting)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"更新会议失败: {e}")
            raise
    
    async def delete_meeting(self, meeting_id: int, user_id: int) -> None:
        """
        删除会议
        
        Args:
            meeting_id: 会议ID
            user_id: 用户ID
        """
        try:
            logger.info(f"删除会议: meeting_id={meeting_id}, user_id={user_id}")
            
            query = select(Meeting).where(
                and_(Meeting.id == meeting_id, Meeting.user_id == user_id)
            )
            result = await self.db.execute(query)
            meeting = result.scalars().first()
            
            if not meeting:
                raise ValueError("会议不存在或无权访问")
            
            await self.db.delete(meeting)
            await self.db.commit()
            
            logger.info(f"会议删除成功: id={meeting_id}")
        except Exception as e:
            await self.db.rollback()
            logger.error(f"删除会议失败: {e}")
            raise
    
    # 注意：以下方法需要重构，暂不可用
    # 这些方法原本依赖于已弃用的MEETING_STORE内存存储
    # TODO: 使用数据库重新实现流式生成、导出、邮件等功能
    
    async def upload_media(self, meeting_id: str, file: UploadFile, user_id: int) -> dict:
        """
        上传会议音视频
        
        流程图第1-3步：
        1. 上传音视频
        2. 调用转录API
        3. 获取转录文本
        
        Args:
            meeting_id: 会议ID
            file: 上传的媒体文件
            
        Returns:
            上传和转录信息
        """
        await self._require_meeting_access(meeting_id, user_id)
        return await self.minutes_service.upload_and_transcribe(meeting_id, file)
    
    async def start_transcription(self, meeting_id: str, user_id: int) -> dict:
        """
        启动音频转录
        
        Args:
            meeting_id: 会议ID
            
        Returns:
            转录任务信息
        """
        try:
            logger.info(f"启动转录: {meeting_id}")
            await self._require_meeting_access(meeting_id, user_id)
            # TODO: 触发异步转录任务
            return {"meeting_id": meeting_id, "status": "transcribing"}
        except Exception as e:
            logger.error(f"启动转录失败: {e}")
            return {"error": str(e)}

    async def get_task_status(self, task_id: str) -> dict:
        """查询任务状态，供前端轮询"""
        return await self.minutes_service.get_task_status(task_id)
    
    # ============================================================
    # 流程图第4-9步：NLP处理
    # ============================================================
    
    async def process_transcription(
        self,
        meeting_id: str,
        transcription_text: str,
        user_id: int
    ) -> dict:
        """
        处理转录文本，提取各类信息
        
        流程图第4-9步：
        4. 分句与分段
        5. 提取关键词
        6. 完整转录
        7. 使用到分析
        8. 议程提取
        9. 话题划分 + 决议识别
        
        Args:
            meeting_id: 会议ID
            transcription_text: 转录的文本
            
        Returns:
            处理后的会议数据
        """
        await self._require_meeting_access(meeting_id, user_id)
        return await self.minutes_service.process_transcription(
            meeting_id,
            transcription_text
        )
    
    # ============================================================
    # 流程图第10-19步：生成纪要
    # ============================================================
    
    async def get_minutes(self, meeting_id: str, user_id: int) -> dict:
        """
        获取会议纪要（所有格式）
        
        返回:
        - 执行摘要
        - 议程与决议
        - Action Items
        - 完整内容
        
        Args:
            meeting_id: 会议ID
            
        Returns:
            会议纪要
        """
        logger.info(f"获取会议纪要: {meeting_id}")
        await self._require_meeting_access(meeting_id, user_id)
        return await self.minutes_service.get_minutes_by_meeting(meeting_id)
    
    async def generate_minutes(
        self,
        meeting_id: str,
        meeting_data: Dict,
        formats: List[str] = None,
        user_id: int = 0
    ) -> dict:
        """
        生成会议纪要（支持多种格式）
        
        流程图第10-19步的集中处理
        
        Args:
            meeting_id: 会议ID
            meeting_data: 会议数据
            formats: 输出格式 (markdown, pdf, docx, json)
            
        Returns:
            生成的纪要信息
        """
        await self._require_meeting_access(meeting_id, user_id)
        return await self.minutes_service.generate_meeting_minutes(
            meeting_id,
            meeting_data,
            formats
        )
    
    async def export_minutes(self, meeting_id: str, format: str = "markdown", user_id: int = 0) -> dict:
        """
        导出会议纪要
        
        格式支持: markdown, pdf, docx
        
        Args:
            meeting_id: 会议ID
            format: 导出格式
            
        Returns:
            导出信息
        """
        await self._require_meeting_access(meeting_id, user_id)
        return await self.minutes_service.export_minutes(meeting_id, format)

    # ============================================================
    # SSE：逐字/逐token 流式生成纪要
    # ============================================================

    def get_llm_stream(
        self, meeting_id: str, meeting_data: Dict, user_id: int
    ) -> AsyncGenerator[str, None]:
        """返回一个 async generator，每次 yield 一段文本（token/chunk）。

        由 /minutes/stream SSE 端点消费，并包装成 {status: streaming, chunk, content}。
        """

        # Access check is async; callers should validate before invoking this stream.
        transcription = (
            meeting_data.get("transcription_text")
            or meeting_data.get("transcription")
            or meeting_data.get("content")
            or ""
        )
        title = meeting_data.get("title") or f"会议纪要 - {meeting_id}"

        system_prompt = (
            "你是一个专业的会议纪要助手。请根据会议转录内容生成结构清晰的中文会议纪要。\n"
            "要求：\n"
            "1) 使用 Markdown 输出（包含标题、基本信息、关键点、决议、Action Items 等）\n"
            "2) 内容准确、条理清晰、适合直接发给参会人员\n"
            "3) 不要输出 JSON，不要输出多余解释\n"
        )
        user_prompt = (
            f"会议标题：{title}\n\n"
            "会议转录如下（可能较长）：\n\n"
            f"{transcription[:60000]}"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        async def _gen() -> AsyncGenerator[str, None]:
            # 优先走 Qwen（DashScope compatible-mode），如果没配置则降级为模拟输出
            if not settings.QWEN_API_KEY:
                fallback_text = "（未配置 QWEN_API_KEY，无法流式生成纪要。请在后端 .env 中配置后重试。）\n"
                for i in range(0, len(fallback_text), 8):
                    yield fallback_text[i : i + 8]
                return

            api_url = settings.QWEN_BASE_URL.rstrip("/") + "/chat/completions"
            stream_service = StreamService(logger=logger)

            async for sse_line in stream_service.stream(
                provider=StreamProvider.QWEN,
                messages=messages,
                question="生成会议纪要",
                api_url=api_url,
                api_key=settings.QWEN_API_KEY,
                model_name=settings.QWEN_MODEL_NAME,
                temperature=0.2,
                top_p=0.9,
                max_tokens=2048,
            ):
                if not sse_line or not sse_line.startswith("data: "):
                    continue

                payload = sse_line[6:].strip()
                try:
                    obj = json.loads(payload)
                except Exception:
                    continue

                try:
                    delta = obj.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content", "")
                except Exception:
                    content = ""

                if content:
                    yield content

        return _gen()
    
    # ============================================================
    # 流程图第20-23步：邮件和分享
    # ============================================================
    
    async def send_minutes_email(
        self,
        meeting_id: str,
        recipients: List[str],
        format: str = "pdf",
        user_id: int = 0
    ) -> dict:
        """
        通过邮件发送会议纪要
        
        流程图第20步：邮件发送
        
        Args:
            meeting_id: 会议ID
            recipients: 收件人列表
            format: 附件格式
            
        Returns:
            发送状态
        """
        await self._require_meeting_access(meeting_id, user_id)
        return await self.minutes_service.send_minutes_email(
            meeting_id,
            recipients,
            format
        )
    
    async def share_minutes(
        self,
        meeting_id: str,
        share_targets: Dict,
        user_id: int = 0
    ) -> dict:
        """
        分享会议纪要
        
        流程图第21-23步：分享给相关人员和平台
        
        Args:
            meeting_id: 会议ID
            share_targets: 分享目标（邮件、企业微信、钉钉等）
            
        Returns:
            分享状态
        """
        await self._require_meeting_access(meeting_id, user_id)
        return await self.minutes_service.share_minutes(meeting_id, share_targets)
    
    # ============================================================
    # 查询端点
    # ============================================================
    
    async def get_participants(self, meeting_id: str, user_id: int) -> List[dict]:
        """获取会议参与人列表"""
        try:
            logger.info(f"获取参与人: {meeting_id}")
            await self._require_meeting_access(meeting_id, user_id)
            # 获取原始结构化数据
            data = self.minutes_service.get_minutes_data(meeting_id)
            if not data:
                logger.info(f"未找到会议数据 (meeting_id={meeting_id})，返回空列表")
                return []
                
            participants = data.get("participants", [])
            # 格式化为对象列表
            return [{"name": p, "role": "participant"} for p in participants]
        except Exception as e:
            logger.error(f"获取参与人失败: {e}")
            return []
    
    async def get_agendas(self, meeting_id: str, user_id: int) -> List[dict]:
        """获取会议议程"""
        try:
            logger.info(f"获取议程: {meeting_id}")
            await self._require_meeting_access(meeting_id, user_id)
            # 获取原始结构化数据
            data = self.minutes_service.get_minutes_data(meeting_id)
            if not data:
                return []
                
            agendas = data.get("agendas", [])
            # 格式化为对象列表
            formatted_agendas = []
            for a in agendas:
                if isinstance(a, dict):
                    formatted_agendas.append({
                        "content": a.get("title", "") + ": " + a.get("description", ""),
                        "status": "pending"
                    })
                else:
                    formatted_agendas.append({"content": str(a), "status": "pending"})
            return formatted_agendas
        except Exception as e:
            logger.error(f"获取议程失败: {e}")
            return []
    
    async def get_decisions(self, meeting_id: str, user_id: int) -> List[dict]:
        """获取会议决议"""
        try:
            logger.info(f"获取决议: {meeting_id}")
            await self._require_meeting_access(meeting_id, user_id)
            # 获取原始结构化数据
            data = self.minutes_service.get_minutes_data(meeting_id)
            if not data:
                return []
                
            decisions = data.get("decisions", [])
            # 格式化为对象列表
            return [{"content": d, "status": "approved"} for d in decisions]
        except Exception as e:
            logger.error(f"获取决议失败: {e}")
            return []
    
    async def get_action_items(self, meeting_id: str, user_id: int) -> List[dict]:
        """获取Action Items"""
        try:
            logger.info(f"获取Action Items: {meeting_id}")
            await self._require_meeting_access(meeting_id, user_id)
            # 获取原始结构化数据
            data = self.minutes_service.get_minutes_data(meeting_id)
            if not data:
                return []
                
            action_items = data.get("action_items", [])
            
            # 格式化为对象列表
            formatted_items = []
            for item in action_items:
                if isinstance(item, dict):
                    formatted_items.append({
                        "content": item.get("content", ""),
                        "owner": item.get("owner", "待定"),
                        "due_date": item.get("due_date", "待定"),
                        "status": item.get("status", "pending")
                    })
                else:
                    formatted_items.append({
                        "content": str(item),
                        "owner": "待定",
                        "due_date": "待定",
                        "status": "pending"
                    })
            return formatted_items
        except Exception as e:
            logger.error(f"获取Action Items失败: {e}")
            return []

    def _format_meeting(self, meeting: Meeting) -> dict:
        """格式化会议对象为字典"""
        return {
            "id": meeting.id,
            "user_id": meeting.user_id,
            "title": meeting.title,
            "description": meeting.description,
            "date": meeting.date,
            "status": meeting.status,
            "transcription": meeting.transcription,
            "created_at": meeting.created_at.isoformat() if meeting.created_at else None,
            "updated_at": meeting.updated_at.isoformat() if meeting.updated_at else None,
        }

    def _normalize_meeting_id(self, meeting_id: str | int) -> int:
        if isinstance(meeting_id, int):
            return meeting_id
        if isinstance(meeting_id, str):
            if meeting_id.isdigit():
                return int(meeting_id)
            if meeting_id.startswith("meeting_") and meeting_id[8:].isdigit():
                return int(meeting_id[8:])
        raise HTTPException(status_code=400, detail="无效的会议ID")

    async def _require_meeting_access(self, meeting_id: str | int, user_id: int) -> Meeting:
        normalized_id = self._normalize_meeting_id(meeting_id)
        query = select(Meeting).where(
            and_(Meeting.id == normalized_id, Meeting.user_id == user_id)
        )
        result = await self.db.execute(query)
        meeting = result.scalars().first()
        if not meeting:
            raise HTTPException(status_code=404, detail="会议不存在或无权访问")
        return meeting
