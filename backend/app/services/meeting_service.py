"""
会议纪要服务层
提供会议处理相关业务逻辑，集成NLP和文档生成服务
"""

import json
from typing import List, Optional, Dict, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile, HTTPException
from datetime import datetime

from app.utils.logger import get_logger
from app.services.meeting_minutes_service import MeetingMinutesService
from app.services.stream_service import StreamService, StreamProvider
from app.core.config import settings

# 简易的内存存储，便于跑通流程。生产环境请替换为数据库持久化。
MEETING_STORE: Dict[str, dict] = {}

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
            
        Returns:
            创建的会议信息
        """
        try:
            logger.info(f"创建会议: {meeting_data.get('title')}")
            meeting_id = meeting_data.get("id") or f"meeting_{int(datetime.now().timestamp())}"
            meeting = {
                "id": meeting_id,
                "status": "created",
                "user_id": user_id,
                **meeting_data,
            }
            MEETING_STORE[meeting_id] = meeting
            return meeting
        except Exception as e:
            logger.error(f"创建会议失败: {e}")
            return {"error": str(e)}
    
    async def list_meetings(
        self, skip: int, limit: int, status: Optional[str], user_id: int
    ) -> List[dict]:
        """
        获取会议列表
        
        Args:
            skip: 分页偏移
            limit: 分页大小
            status: 过滤状态（created, transcribing, processing, completed）
            
        Returns:
            会议列表
        """
        try:
            logger.info(f"查询会议列表: skip={skip}, limit={limit}, status={status}")
            meetings = [m for m in MEETING_STORE.values() if m.get("user_id") == user_id]
            if status:
                meetings = [m for m in meetings if m.get("status") == status]
            return meetings[skip: skip + limit]
        except Exception as e:
            logger.error(f"查询会议列表失败: {e}")
            return []
    
    async def get_meeting(self, meeting_id: str, user_id: int) -> dict:
        """
        获取会议详情
        
        Args:
            meeting_id: 会议ID
            
        Returns:
            会议详情
        """
        try:
            logger.info(f"获取会议详情: {meeting_id}")
            return self._require_meeting_access(meeting_id, user_id)
        except Exception as e:
            logger.error(f"获取会议详情失败: {e}")
            return {"error": str(e)}
    
    async def update_meeting(self, meeting_id: str, meeting_data: Dict, user_id: int) -> dict:
        """
        更新会议信息
        
        Args:
            meeting_id: 会议ID
            meeting_data: 更新的数据
            
        Returns:
            更新后的会议信息
        """
        try:
            logger.info(f"更新会议: {meeting_id}")
            meeting = self._require_meeting_access(meeting_id, user_id)
            meeting.update(meeting_data)
            return {"id": meeting_id, **meeting}
        except Exception as e:
            logger.error(f"更新会议失败: {e}")
            return {"error": str(e)}
    
    async def delete_meeting(self, meeting_id: str, user_id: int) -> None:
        """
        删除会议
        
        Args:
            meeting_id: 会议ID
        """
        try:
            logger.info(f"删除会议: {meeting_id}")
            self._require_meeting_access(meeting_id, user_id)
            MEETING_STORE.pop(meeting_id, None)
        except Exception as e:
            logger.error(f"删除会议失败: {e}")
    
    # ============================================================
    # 流程图第1-3步：上传和转录
    # ============================================================
    
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
        self._require_meeting_access(meeting_id, user_id)
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
            self._require_meeting_access(meeting_id, user_id)
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
        self._require_meeting_access(meeting_id, user_id)
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
        self._require_meeting_access(meeting_id, user_id)
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
        self._require_meeting_access(meeting_id, user_id)
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
        self._require_meeting_access(meeting_id, user_id)
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

        self._require_meeting_access(meeting_id, user_id)
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
        self._require_meeting_access(meeting_id, user_id)
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
        self._require_meeting_access(meeting_id, user_id)
        return await self.minutes_service.share_minutes(meeting_id, share_targets)
    
    # ============================================================
    # 查询端点
    # ============================================================
    
    async def get_participants(self, meeting_id: str, user_id: int) -> List[dict]:
        """获取会议参与人列表"""
        try:
            logger.info(f"获取参与人: {meeting_id}")
            self._require_meeting_access(meeting_id, user_id)
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
            self._require_meeting_access(meeting_id, user_id)
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
            self._require_meeting_access(meeting_id, user_id)
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
            self._require_meeting_access(meeting_id, user_id)
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

    def _require_meeting_access(self, meeting_id: str, user_id: int) -> dict:
        meeting = MEETING_STORE.get(meeting_id)
        if not meeting:
            raise HTTPException(status_code=404, detail="会议不存在")
        if meeting.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="无权限访问该会议")
        return meeting
