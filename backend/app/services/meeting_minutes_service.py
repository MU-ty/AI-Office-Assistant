"""
会议纪要处理服务 - 整合所有功能的核心服务
处理音视频上传、转录、NLP分析、纪要生成等完整流程

基于流程图 - 按顺序处理各个阶段
"""

import asyncio  # 添加这行 - 在文件顶部导入 asyncio
from typing import Dict, List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile, HTTPException
import os

from app.utils.logger import get_logger
from app.services.nlp_service import nlp_service
from app.services.document_generation_service import document_generation_service
from app.core.config import settings

logger = get_logger(__name__)

# 简易任务状态存储，方便前端轮询。生产环境请替换为持久化/队列。
TASK_STATE: Dict[str, dict] = {}


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
            task_id = await self._start_transcription_task(
                meeting_id,
                save_path
            )

            return {
                "meeting_id": meeting_id,
                "file_path": save_path,
                "task_id": task_id,
                "step": 0,
                "is_completed": False,
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
        task_id = f"task_{meeting_id}_{int(datetime.now().timestamp())}"
        logger.info(f"转录任务已启动: {task_id}")

        # 初始化任务状态，后续轮询时根据时间推进模拟流程
        created_at = datetime.now(timezone.utc)
        TASK_STATE[task_id] = {
            "task_id": task_id,
            "meeting_id": meeting_id,
            "step": 0,
            "is_completed": False,
            "status": "transcribing",
            "content": "上传成功，开始转录...",
            "created_at": created_at,
        }

        # 异步触发处理流程
        import asyncio
        asyncio.create_task(self._process_full_workflow(task_id, meeting_id, file_path))

        return task_id

    async def _process_full_workflow(self, task_id: str, meeting_id: str, file_path: str) -> None:
        """
        完整的处理流程：模拟转录 → NLP分析 → 生成纪要
        
        这里用 asyncio.sleep 模拟各个阶段的耗时
        """
        try:
            # 第1步：转录（模拟）
            await asyncio.sleep(2)
            TASK_STATE[task_id]["step"] = 1
            TASK_STATE[task_id]["content"] = "✓ 音视频转录完成\n→ 正在进行语义分析..."
            logger.info(f"[{task_id}] 步骤1: 转录完成")

            # 生成模拟转录文本
            transcription_text = self._get_demo_transcription()
            TASK_STATE[task_id]["transcription"] = transcription_text

            # 第2步：NLP处理（语义分析、实体识别等）
            await asyncio.sleep(2)
            TASK_STATE[task_id]["step"] = 2
            TASK_STATE[task_id]["content"] = "✓ 音视频转录完成\n✓ 语义分析完成\n→ 正在提取议程和决议..."
            logger.info(f"[{task_id}] 步骤2: NLP分析完成")

            # NLP处理转录文本
            nlp_result = await self.process_transcription(meeting_id, transcription_text)
            TASK_STATE[task_id]["nlp_result"] = nlp_result

            # 第3步：提取关键信息（议程、决议、Action Items）
            await asyncio.sleep(2)
            TASK_STATE[task_id]["step"] = 3
            TASK_STATE[task_id]["content"] = "✓ 音视频转录完成\n✓ 语义分析完成\n✓ 议程提取完成\n→ 正在生成纪要文档..."
            logger.info(f"[{task_id}] 步骤3: 关键信息提取完成")

            # 第4步：生成最终纪要
            await asyncio.sleep(2)
            meeting_data = {
                "title": f"会议纪要 - {meeting_id}",
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "participants": ["参与者1", "参与者2", "参与者3"],
                **nlp_result,
            }

            generate_result = await self.generate_meeting_minutes(
                meeting_id,
                meeting_data,
                formats=["markdown", "json"]
            )

            TASK_STATE[task_id]["step"] = 4
            TASK_STATE[task_id]["is_completed"] = True
            TASK_STATE[task_id]["status"] = "completed"
            TASK_STATE[task_id]["minutes"] = generate_result.get("formats", {}).get("markdown", {}).get("content")
            TASK_STATE[task_id]["summary"] = self._generate_summary(nlp_result)
            TASK_STATE[task_id]["content"] = "✓ 会议纪要已生成！"

            logger.info(f"[{task_id}] 步骤4: 纪要生成完成，任务完成")

        except Exception as e:
            logger.error(f"处理流程出错 [{task_id}]: {e}", exc_info=True)
            TASK_STATE[task_id]["status"] = "failed"
            TASK_STATE[task_id]["content"] = f"处理出错: {str(e)}"

    def _get_demo_transcription(self) -> str:
        """返回演示用的转录文本"""
        return """各位好，今天的会议主要讨论Q1季度的工作计划和重点项目。

首先，我们来看市场部的工作进展。上个月完成了三个大客户的合作谈判，签约额达到500万。今月的目标是继续扩大客户群体，计划再拓展5个新客户。

其次，技术部报告了新产品开发的进展。目前已完成需求评审，进入开发阶段。预计下月底可以完成核心功能的开发。这个项目的重点是保证质量和按时交付。

关于人力资源方面，HR部表示需要招聘5名技术人员来支持新项目。招聘流程预计在2周内启动。同时，公司计划在本季度进行一次员工培训。

最后，财务部汇报了Q4的财务业绩，整体表现良好，利润同比增长15%。

关键决议：
1. 批准新产品项目的开发预算500万元
2. 同意技术部的人员招聘计划
3. 4月底前完成新客户拓展目标

Action Items：
1. 市场部制定详细的客户拓展方案，负责人：张三，截止：3月15日
2. 技术部完成API接口设计文档，负责人：李四，截止：3月10日
3. HR部启动招聘流程，负责人：王五，截止：3月5日
4. 财务部编制Q1预算详表，负责人：赵六，截止：3月8日"""

    def _generate_summary(self, nlp_result: Dict) -> str:
        """基于NLP结果生成执行摘要"""
        keywords = nlp_result.get("keywords", [])
        key_points = nlp_result.get("key_points", [])

        summary = "## 执行摘要\n\n"
        summary += "**关键议题**: " + "、".join([kw[0] if isinstance(kw, tuple) else kw for kw in keywords[:5]]) + "\n\n"

        if key_points:
            summary += "**核心内容**: \n"
            for point in key_points[:3]:
                summary += f"- {point}\n"

        return summary
    
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

    async def get_task_status(self, task_id: str) -> Dict:
        """供前端轮询的任务状态查询"""
        state = TASK_STATE.get(task_id)
        if not state:
            raise HTTPException(status_code=404, detail="task_not_found")

        # 根据任务的 step_progress 返回当前状态
        return {
            "task_id": task_id,
            "meeting_id": state.get("meeting_id"),
            "step": state.get("step", 0),
            "is_completed": state.get("is_completed", False),
            "content": state.get("content", ""),
            "status": state.get("status", "processing"),
            "summary": state.get("summary"),  # 纪要摘要
            "minutes": state.get("minutes"),  # 完整纪要
        }
    
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
    
    def _ensure_upload_dir(self) -> str:
        """
        确保上传目录存在
        
        Returns:
            上传目录路径
        
        Raises:
            OSError: 当目录无法创建且不存在时抛出
        """
        upload_dir = settings.UPLOAD_DIR
        try:
            os.makedirs(upload_dir, exist_ok=True)
        except OSError as e:
            # 如果目录不存在且无法创建，则记录错误并抛出异常
            if not os.path.isdir(upload_dir):
                logger.error(f"创建上传目录失败: {upload_dir} - {e}")
                raise
        return upload_dir
    
    def _save_markdown(self, meeting_id: str, content: str) -> str:
        """保存Markdown格式的纪要"""
        upload_dir = self._ensure_upload_dir()
        path = os.path.join(upload_dir, f"{meeting_id}_minutes.md")
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
        except (OSError, IOError) as e:
            logger.error(f"保存Markdown纪要失败: meeting_id={meeting_id}, path={path}, error={e}")
            raise
        return path
    
    def _save_json(self, meeting_id: str, content: str) -> str:
        """保存JSON格式的纪要"""
        upload_dir = self._ensure_upload_dir()
        path = os.path.join(upload_dir, f"{meeting_id}_minutes.json")
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
        except (OSError, IOError) as e:
            logger.error(f"保存JSON纪要失败: meeting_id={meeting_id}, path={path}, error={e}")
            raise
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
