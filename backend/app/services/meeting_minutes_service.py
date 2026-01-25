"""
会议纪要处理服务 - 整合所有功能的核心服务
处理音视频上传、转录、NLP分析、纪要生成等完整流程

基于流程图 - 按顺序处理各个阶段
"""

from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile
import os

from app.utils.logger import get_logger
from app.services.nlp_service import nlp_service
from app.services.document_generation_service import document_generation_service
from app.core.config import settings

logger = get_logger(__name__)


class MeetingMinutesService:
    """会议纪要处理服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.nlp = nlp_service
        self.doc_gen = document_generation_service
    
    # ============================================================
    # 第1-3步：上传和转录
    # ============================================================
    
    async def upload_and_transcribe(
        self,
        meeting_id: str,
        file: UploadFile
    ) -> Dict:
        """
        上传音视频并开始转录
        
        Args:
            meeting_id: 会议ID
            file: 上传的音视频文件
            
        Returns:
            包含上传信息和转录任务的响应
        """
        try:
            # 1. 验证文件
            if not self._validate_file(file.filename):
                return {"error": "不支持的文件类型"}
            
            # 2. 保存文件
            save_path = await self._save_upload_file(meeting_id, file)
            logger.info(f"文件保存成功: {save_path}")
            
            # 3. 触发异步转录任务（实际项目中应使用Celery）
            transcription_task_id = await self._start_transcription_task(
                meeting_id,
                save_path
            )
            
            return {
                "meeting_id": meeting_id,
                "file_path": save_path,
                "transcription_task_id": transcription_task_id,
                "status": "transcribing",
                "message": "转录任务已启动"
            }
            
        except Exception as e:
            logger.error(f"上传和转录失败: {e}")
            return {"error": str(e)}
    
    def _validate_file(self, filename: str) -> bool:
        """验证上传的文件类型"""
        allowed_extensions = ['mp3', 'wav', 'm4a', 'webm', 'mp4']
        return any(filename.lower().endswith(f'.{ext}') for ext in allowed_extensions)
    
    async def _save_upload_file(self, meeting_id: str, file: UploadFile) -> str:
        """保存上传的文件"""
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{meeting_id}_{timestamp}_{file.filename}"
        save_path = os.path.join(settings.UPLOAD_DIR, filename)
        
        content = await file.read()
        with open(save_path, 'wb') as f:
            f.write(content)
        
        return save_path
    
    async def _start_transcription_task(self, meeting_id: str, file_path: str) -> str:
        """启动转录任务（实际项目应使用Celery）"""
        # TODO: 集成Whisper或其他转录API
        # 这里返回任务ID，实际应异步处理
        task_id = f"task_{meeting_id}_{datetime.now().timestamp()}"
        logger.info(f"转录任务已启动: {task_id}")
        return task_id
    
    # ============================================================
    # 第4-9步：NLP文本处理和分析
    # ============================================================
    
    async def process_transcription(
        self,
        meeting_id: str,
        transcription_text: str
    ) -> Dict:
        """
        处理转录文本，提取各类信息
        
        Args:
            meeting_id: 会议ID
            transcription_text: 转录的文本
            
        Returns:
            包含各类提取信息的字典
        """
        try:
            logger.info(f"开始处理转录文本: {meeting_id}")
            
            # 4. 文本分句和分段
            sentences = self.nlp.split_sentences(transcription_text)
            paragraphs = self.nlp.split_paragraphs(transcription_text)
            logger.info(f"文本分句完成: {len(sentences)}句")
            
            # 5. 提取关键词
            keywords = self.nlp.extract_keywords(transcription_text, top_k=15)
            logger.info(f"关键词提取完成: {len(keywords)}个")
            
            # 6. 提取关键句
            key_sentences = self.nlp.extract_key_sentences(transcription_text, top_k=10)
            logger.info(f"关键句提取完成: {len(key_sentences)}句")
            
            # 7. 实体识别（日期、时间等）
            entities = self.nlp.extract_entities(transcription_text)
            logger.info(f"实体识别完成: {entities}")
            
            # 8. 话题划分（使用主题聚类或LLM）
            topics = await self._identify_topics(transcription_text)
            logger.info(f"话题划分完成: {len(topics)}个话题")
            
            # 9. 提取议程、决议、Action Items（使用LLM或规则）
            meeting_components = await self._extract_meeting_components(
                transcription_text,
                sentences,
                topics
            )
            
            return {
                "meeting_id": meeting_id,
                "sentences": sentences,
                "paragraphs": paragraphs,
                "keywords": keywords,
                "key_sentences": key_sentences,
                "entities": entities,
                "topics": topics,
                **meeting_components,
                "text_stats": self.nlp.get_text_stats(transcription_text)
            }
            
        except Exception as e:
            logger.error(f"文本处理失败: {e}")
            return {"error": str(e)}
    
    async def _identify_topics(self, text: str) -> List[str]:
        """
        识别文本中的话题
        
        可选：使用LDA、聚类或调用Qwen-plus API
        """
        # 简化版本：使用关键词作为话题指示
        keywords = self.nlp.extract_keywords(text, top_k=5)
        topics = [kw[0] if isinstance(kw, tuple) else kw for kw in keywords]
        return topics
    
    async def _extract_meeting_components(
        self,
        text: str,
        sentences: List[str],
        topics: List[str]
    ) -> Dict:
        """
        提取会议的各个组件：议程、决议、Action Items等
        
        实际项目应调用Qwen-plus API或其他LLM
        """
        # 这里是简化的规则提取
        # 实际项目应使用LLM API获取更准确的结果
        
        return {
            "agendas": [f"议题: {topic}" for topic in topics[:3]],
            "decisions": [f"决议: {sentence}" for sentence in self.nlp.extract_key_sentences(text, top_k=3)],
            "action_items": [
                {
                    "content": f"Action Item: {sentence}",
                    "owner": "待定",
                    "due_date": "待定"
                }
                for sentence in self.nlp.extract_key_sentences(text, top_k=3)
            ],
            "key_points": [f"关键点: {sentence}" for sentence in self.nlp.extract_key_sentences(text, top_k=5)]
        }
    
    # ============================================================
    # 第10-19步：生成纪要
    # ============================================================
    
    async def generate_meeting_minutes(
        self,
        meeting_id: str,
        meeting_data: Dict,
        formats: List[str] = None
    ) -> Dict:
        """
        生成会议纪要（支持多种格式）
        
        Args:
            meeting_id: 会议ID
            meeting_data: 处理后的会议数据
            formats: 输出格式列表，支持: markdown, pdf, docx, json
            
        Returns:
            包含各格式纪要的响应
        """
        if formats is None:
            formats = ['markdown', 'json']
        
        try:
            title = f"会议纪要 - {meeting_data.get('title', meeting_id)}"
            result = {
                "meeting_id": meeting_id,
                "title": title,
                "formats": {}
            }
            
            # 生成Markdown格式
            if 'markdown' in formats:
                md_content = self.doc_gen.generate_markdown(title, meeting_data)
                md_path = self._save_markdown(meeting_id, md_content)
                result["formats"]["markdown"] = {
                    "content": md_content,
                    "path": md_path
                }
                logger.info(f"Markdown纪要已生成: {md_path}")
            
            # 生成PDF格式
            if 'pdf' in formats:
                pdf_path = os.path.join(settings.UPLOAD_DIR, f"{meeting_id}_minutes.pdf")
                success = self.doc_gen.generate_pdf(title, meeting_data, pdf_path)
                if success:
                    result["formats"]["pdf"] = {"path": pdf_path}
                    logger.info(f"PDF纪要已生成: {pdf_path}")
            
            # 生成Word格式
            if 'docx' in formats:
                docx_path = os.path.join(settings.UPLOAD_DIR, f"{meeting_id}_minutes.docx")
                success = self.doc_gen.generate_docx(title, meeting_data, docx_path)
                if success:
                    result["formats"]["docx"] = {"path": docx_path}
                    logger.info(f"Word纪要已生成: {docx_path}")
            
            # 生成JSON格式
            if 'json' in formats:
                json_content = self.doc_gen.generate_json(meeting_data)
                json_path = self._save_json(meeting_id, json_content)
                result["formats"]["json"] = {
                    "content": json_content,
                    "path": json_path
                }
                logger.info(f"JSON纪要已生成: {json_path}")
            
            return result
            
        except Exception as e:
            logger.error(f"纪要生成失败: {e}")
            return {"error": str(e)}
    
    def _save_markdown(self, meeting_id: str, content: str) -> str:
        """保存Markdown格式的纪要"""
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        path = os.path.join(settings.UPLOAD_DIR, f"{meeting_id}_minutes.md")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return path
    
    def _save_json(self, meeting_id: str, content: str) -> str:
        """保存JSON格式的纪要"""
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        path = os.path.join(settings.UPLOAD_DIR, f"{meeting_id}_minutes.json")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return path
    
    # ============================================================
    # 第20-23步：邮件和分享
    # ============================================================
    
    async def export_minutes(
        self,
        meeting_id: str,
        format: str = "markdown"
    ) -> Dict:
        """
        导出会议纪要
        
        Args:
            meeting_id: 会议ID
            format: 导出格式 (markdown, pdf, docx)
            
        Returns:
            导出的纪要信息
        """
        # TODO: 从数据库获取会议数据并重新生成
        logger.info(f"导出会议纪要: {meeting_id} (格式: {format})")
        pass
    
    async def send_minutes_email(
        self,
        meeting_id: str,
        recipients: List[str],
        format: str = "pdf"
    ) -> Dict:
        """
        通过邮件发送会议纪要
        
        Args:
            meeting_id: 会议ID
            recipients: 收件人列表
            format: 附件格式
            
        Returns:
            发送状态
        """
        # TODO: 使用smtplib或yagmail发送邮件
        logger.info(f"发送会议纪要邮件: {meeting_id} -> {recipients}")
        pass
    
    async def share_minutes(
        self,
        meeting_id: str,
        share_targets: Dict
    ) -> Dict:
        """
        分享会议纪要
        
        Args:
            meeting_id: 会议ID
            share_targets: 分享目标 (邮件、企业微信、钉钉等)
            
        Returns:
            分享状态
        """
        # TODO: 实现多平台分享
        logger.info(f"分享会议纪要: {meeting_id} -> {share_targets}")
        pass


# 服务工厂函数，而不是在模块级创建全局实例
def get_meeting_minutes_service(db: AsyncSession) -> MeetingMinutesService:
    """
    获取会议纪要服务实例

    使用时通过依赖注入或手动传入 db 会话：
        service = get_meeting_minutes_service(db)
    """
    return MeetingMinutesService(db)
