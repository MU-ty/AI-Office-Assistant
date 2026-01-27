"""
会议纪要服务层
提供会议处理相关业务逻辑，集成NLP和文档生成服务
"""

from typing import List, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile, HTTPException
from datetime import datetime

from app.utils.logger import get_logger
from app.services.meeting_minutes_service import MeetingMinutesService

# 简易的内存存储，便于跑通流程。生产环境请替换为数据库持久化。
MEETING_STORE: Dict[str, dict] = {}

logger = get_logger(__name__)


class MeetingService:
    """会议纪要服务 - 管理会议生命周期"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.minutes_service = MeetingMinutesService(db)
    
    async def create_meeting(self, meeting_data: Dict) -> dict:
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
                **meeting_data,
            }
            MEETING_STORE[meeting_id] = meeting
            return meeting
        except Exception as e:
            logger.error(f"创建会议失败: {e}")
            return {"error": str(e)}
    
    async def list_meetings(self, skip: int, limit: int, status: Optional[str]) -> List[dict]:
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
            meetings = list(MEETING_STORE.values())
            if status:
                meetings = [m for m in meetings if m.get("status") == status]
            return meetings[skip: skip + limit]
        except Exception as e:
            logger.error(f"查询会议列表失败: {e}")
            return []
    
    async def get_meeting(self, meeting_id: str) -> dict:
        """
        获取会议详情
        
        Args:
            meeting_id: 会议ID
            
        Returns:
            会议详情
        """
        try:
            logger.info(f"获取会议详情: {meeting_id}")
            return MEETING_STORE.get(meeting_id, {"error": "meeting_not_found"})
        except Exception as e:
            logger.error(f"获取会议详情失败: {e}")
            return {"error": str(e)}
    
    async def update_meeting(self, meeting_id: str, meeting_data: Dict) -> dict:
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
            if meeting_id not in MEETING_STORE:
                return {"error": "meeting_not_found"}
            MEETING_STORE[meeting_id].update(meeting_data)
            return {"id": meeting_id, **MEETING_STORE[meeting_id]}
        except Exception as e:
            logger.error(f"更新会议失败: {e}")
            return {"error": str(e)}
    
    async def delete_meeting(self, meeting_id: str) -> None:
        """
        删除会议
        
        Args:
            meeting_id: 会议ID
        """
        try:
            logger.info(f"删除会议: {meeting_id}")
            MEETING_STORE.pop(meeting_id, None)
        except Exception as e:
            logger.error(f"删除会议失败: {e}")
    
    # ============================================================
    # 流程图第1-3步：上传和转录
    # ============================================================
    
    async def upload_media(self, meeting_id: str, file: UploadFile) -> dict:
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
        return await self.minutes_service.upload_and_transcribe(meeting_id, file)
    
    async def start_transcription(self, meeting_id: str) -> dict:
        """
        启动音频转录
        
        Args:
            meeting_id: 会议ID
            
        Returns:
            转录任务信息
        """
        try:
            logger.info(f"启动转录: {meeting_id}")
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
        transcription_text: str
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
        return await self.minutes_service.process_transcription(
            meeting_id,
            transcription_text
        )
    
    # ============================================================
    # 流程图第10-19步：生成纪要
    # ============================================================
    
    async def get_minutes(self, meeting_id: str) -> dict:
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
        return await self.minutes_service.get_minutes_by_meeting(meeting_id)
    
    async def generate_minutes(
        self,
        meeting_id: str,
        meeting_data: Dict,
        formats: List[str] = None
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
        return await self.minutes_service.generate_meeting_minutes(
            meeting_id,
            meeting_data,
            formats
        )
    
    async def export_minutes(self, meeting_id: str, format: str = "markdown") -> dict:
        """
        导出会议纪要
        
        格式支持: markdown, pdf, docx
        
        Args:
            meeting_id: 会议ID
            format: 导出格式
            
        Returns:
            导出信息
        """
        return await self.minutes_service.export_minutes(meeting_id, format)
    
    # ============================================================
    # 流程图第20-23步：邮件和分享
    # ============================================================
    
    async def send_minutes_email(
        self,
        meeting_id: str,
        recipients: List[str],
        format: str = "pdf"
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
        return await self.minutes_service.send_minutes_email(
            meeting_id,
            recipients,
            format
        )
    
    async def share_minutes(
        self,
        meeting_id: str,
        share_targets: Dict
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
        return await self.minutes_service.share_minutes(meeting_id, share_targets)
    
    # ============================================================
    # 查询端点
    # ============================================================
    
    async def get_participants(self, meeting_id: str) -> List[dict]:
        """获取会议参与人列表"""
        try:
            logger.info(f"获取参与人: {meeting_id}")
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
    
    async def get_agendas(self, meeting_id: str) -> List[dict]:
        """获取会议议程"""
        try:
            logger.info(f"获取议程: {meeting_id}")
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
    
    async def get_decisions(self, meeting_id: str) -> List[dict]:
        """获取会议决议"""
        try:
            logger.info(f"获取决议: {meeting_id}")
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
    
    async def get_action_items(self, meeting_id: str) -> List[dict]:
        """获取Action Items"""
        try:
            logger.info(f"获取Action Items: {meeting_id}")
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
