"""
文献摘要服务层
提供文档处理和摘要生成逻辑
"""

from typing import List, Optional, Dict
from datetime import datetime
import json
import os
import re
import uuid

import aiohttp
import pdfplumber
from docx import Document as DocxDocument
from fastapi import UploadFile
from sqlalchemy import select, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.document import Document, DocumentSummary
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DocumentService:
    """文献文档服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_document(self, title: str, file: UploadFile, user_id: int) -> dict:
        """
        创建文档

        1. 验证文件类型 (PDF, TXT, DOCX)
        2. 保存文件
        3. 解析文档内容
        4. 提取元数据 (标题、作者、发表日期等)
        5. 创建文档记录
        """
        logger.info(f"创建文档: {title}")

        filename = file.filename or "document"
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext not in {"pdf", "txt", "docx"}:
            raise ValueError("仅支持 PDF/TXT/DOCX 文件")

        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        safe_name = f"doc_{uuid.uuid4().hex}.{ext}"
        save_path = os.path.join(settings.UPLOAD_DIR, safe_name)

        content = await file.read()
        if not content:
            raise ValueError("文件内容为空")

        with open(save_path, "wb") as f:
            f.write(content)

        parsed_text = self._parse_file(save_path, ext)
        if not parsed_text.strip():
            raise ValueError("未解析到有效文本")

        doc_title = title or os.path.splitext(filename)[0]
        meta_info = {
            "filename": filename,
            "size": len(content),
            "ext": ext,
        }

        doc = Document(
            user_id=user_id,
            title=doc_title,
            content=parsed_text,
            document_type="source",
            source_type="file",
            source_url=None,
            file_path=save_path,
            meta_info=json.dumps(meta_info, ensure_ascii=False),
        )
        self.db.add(doc)
        await self.db.commit()
        await self.db.refresh(doc)

        return self._format_document(doc)

    async def create_document_from_text(self, title: str, content: str, user_id: int) -> dict:
        """从文本创建文档"""
        if not content or not content.strip():
            raise ValueError("文本不能为空")

        doc = Document(
            user_id=user_id,
            title=title or "文本输入",
            content=content.strip(),
            document_type="source",
            source_type="text",
            source_url=None,
            file_path=None,
            meta_info=None,
        )
        self.db.add(doc)
        await self.db.commit()
        await self.db.refresh(doc)
        return self._format_document(doc)

    async def create_document_from_url(self, title: str, url: str, user_id: int) -> dict:
        """从URL导入文档"""
        if not url or not url.strip():
            raise ValueError("URL不能为空")

        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=20) as resp:
                if resp.status >= 400:
                    raise ValueError("URL内容获取失败")
                html = await resp.text()

        text = self._strip_html(html)
        if not text.strip():
            raise ValueError("未解析到有效文本")

        doc = Document(
            user_id=user_id,
            title=title or "网页导入",
            content=text.strip(),
            document_type="source",
            source_type="url",
            source_url=url,
            file_path=None,
            meta_info=None,
        )
        self.db.add(doc)
        await self.db.commit()
        await self.db.refresh(doc)
        return self._format_document(doc)

    async def list_documents(self, skip: int, limit: int, category: Optional[str], user_id: int) -> List[dict]:
        """获取文档列表"""
        query = select(Document).where(Document.user_id == user_id)
        if category:
            query = query.where(Document.document_type == category)
        query = query.order_by(Document.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        docs = result.scalars().all()
        return [self._format_document(doc) for doc in docs]

    async def get_document(self, doc_id: str, user_id: int) -> dict:
        """获取文档详情"""
        query = select(Document).where(and_(Document.id == doc_id, Document.user_id == user_id))
        result = await self.db.execute(query)
        doc = result.scalars().first()
        if not doc:
            raise ValueError("文档不存在")

        summary = await self._get_latest_summary(doc.id, user_id)
        payload = self._format_document(doc)
        if summary:
            payload["latest_summary"] = summary
        return payload

    async def update_document(self, doc_id: str, doc_data: Dict, user_id: int) -> dict:
        """更新文档信息 (标签、分类等)"""
        query = select(Document).where(and_(Document.id == doc_id, Document.user_id == user_id))
        result = await self.db.execute(query)
        doc = result.scalars().first()
        if not doc:
            raise ValueError("文档不存在")

        if doc_data.get("title"):
            doc.title = doc_data["title"]
        if doc_data.get("category"):
            doc.document_type = doc_data["category"]
        doc.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(doc)
        return self._format_document(doc)

    async def delete_document(self, doc_id: str, user_id: int) -> None:
        """删除文档"""
        query = select(Document).where(and_(Document.id == doc_id, Document.user_id == user_id))
        result = await self.db.execute(query)
        doc = result.scalars().first()
        if not doc:
            raise ValueError("文档不存在")

        await self.db.execute(delete(DocumentSummary).where(DocumentSummary.document_id == doc.id))
        await self.db.delete(doc)
        await self.db.commit()

    async def generate_summary(self, doc_id: str, summary_level: str, user_id: int) -> dict:
        """
        生成文档摘要

        1. 读取文档内容
        2. 根据级别控制摘要长度
        3. 使用 Qwen-Plus 生成摘要
        4. 计算质量分数
        5. 保存摘要记录
        """
        logger.info(f"生成摘要: {doc_id}, 级别: {summary_level}")

        query = select(Document).where(and_(Document.id == doc_id, Document.user_id == user_id))
        result = await self.db.execute(query)
        doc = result.scalars().first()
        if not doc:
            raise ValueError("文档不存在")

        prompt = self._build_summary_prompt(doc.title, doc.content, summary_level)
        summary_text = await self._call_qwen(prompt)
        quality_score = self._estimate_quality(doc.content, summary_text)

        summary = DocumentSummary(
            document_id=doc.id,
            user_id=user_id,
            summary_level=summary_level,
            summary_text=summary_text,
            quality_score=quality_score,
            model_name=settings.QWEN_MODEL_NAME,
        )
        self.db.add(summary)
        await self.db.commit()
        await self.db.refresh(summary)

        return self._format_summary(summary)

    async def get_concepts(self, doc_id: str, user_id: int) -> List[dict]:
        """获取文档关键概念"""
        query = select(Document).where(and_(Document.id == doc_id, Document.user_id == user_id))
        result = await self.db.execute(query)
        doc = result.scalars().first()
        if not doc:
            raise ValueError("文档不存在")

        return []

    async def get_citations(self, doc_id: str, user_id: int) -> List[dict]:
        """获取文档引用关系"""
        query = select(Document).where(and_(Document.id == doc_id, Document.user_id == user_id))
        result = await self.db.execute(query)
        doc = result.scalars().first()
        if not doc:
            raise ValueError("文档不存在")

        return []

    async def search_similar(self, query: str, limit: int = 10, user_id: int = 0) -> List[dict]:
        """相似文献搜索（占位实现）"""
        logger.info(f"搜索相似文献: {query}")
        return []

    def _parse_file(self, path: str, ext: str) -> str:
        if ext == "pdf":
            return self._parse_pdf(path)
        if ext == "txt":
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        if ext == "docx":
            doc = DocxDocument(path)
            return "\n".join([p.text for p in doc.paragraphs if p.text])
        return ""

    def _parse_pdf(self, path: str) -> str:
        texts = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                texts.append(page.extract_text() or "")
        return "\n".join(texts)

    def _strip_html(self, html: str) -> str:
        html = re.sub(r"<script.*?>.*?</script>", "", html, flags=re.S | re.I)
        html = re.sub(r"<style.*?>.*?</style>", "", html, flags=re.S | re.I)
        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _build_summary_prompt(self, title: str, content: str, level: str) -> str:
        level_map = {
            "one_liner": "用一句话概括全文要点。",
            "paragraph": "输出一段摘要，涵盖背景、方法、结论。",
            "full": "输出完整摘要，逻辑清晰、层次分明。",
        }
        instruction = level_map.get(level, level_map["paragraph"])
        return (
            "你是严谨的中文文献摘要助手。请遵循以下要求：\n"
            "1) 只输出摘要正文，不要输出标题或多余解释\n"
            "2) 用客观、正式的中文表述\n"
            "3) 保持信息准确，不要编造\n\n"
            f"文献标题：{title}\n\n"
            f"原文内容（可能较长）：\n{content[:60000]}\n\n"
            f"摘要要求：{instruction}"
        )

    async def _call_qwen(self, prompt: str) -> str:
        if not settings.QWEN_API_KEY:
            return "（未配置 QWEN_API_KEY，无法生成摘要。请在后端 .env 中配置后重试。）"

        api_url = settings.QWEN_BASE_URL.rstrip("/") + "/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.QWEN_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": settings.QWEN_MODEL_NAME,
            "messages": [
                {"role": "system", "content": "你是专业的学术文献摘要助手。"},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "top_p": 0.9,
            "max_tokens": 1200,
            "stream": False,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json=payload, headers=headers, timeout=60) as resp:
                if resp.status >= 400:
                    raise ValueError("摘要生成失败")
                data = await resp.json()
        content = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )
        return content.strip()

    def _estimate_quality(self, source: str, summary: str) -> float:
        if not source or not summary:
            return 0.0
        ratio = min(len(summary) / max(len(source), 1), 1.0)
        return round(max(0.2, 1 - abs(ratio - 0.2)), 3)

    async def _get_latest_summary(self, doc_id: int, user_id: int) -> Optional[dict]:
        query = (
            select(DocumentSummary)
            .where(and_(DocumentSummary.document_id == doc_id, DocumentSummary.user_id == user_id))
            .order_by(DocumentSummary.created_at.desc())
            .limit(1)
        )
        result = await self.db.execute(query)
        summary = result.scalars().first()
        if not summary:
            return None
        return self._format_summary(summary)

    def _format_document(self, doc: Document) -> dict:
        return {
            "id": doc.id,
            "title": doc.title,
            "document_type": doc.document_type,
            "source_type": doc.source_type,
            "source_url": doc.source_url,
            "file_path": doc.file_path,
            "created_at": doc.created_at,
            "updated_at": doc.updated_at,
        }

    def _format_summary(self, summary: DocumentSummary) -> dict:
        return {
            "id": summary.id,
            "document_id": summary.document_id,
            "summary_level": summary.summary_level,
            "summary_text": summary.summary_text,
            "quality_score": summary.quality_score,
            "model_name": summary.model_name,
            "created_at": summary.created_at,
        }
