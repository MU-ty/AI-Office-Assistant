"""
文献摘要服务层
提供文档处理和摘要生成逻辑
"""

from typing import List, Optional, Dict, Any
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
from app.services.weknora_service import weknora_service
from app.services.llm_service import llm_service

logger = get_logger(__name__)


class DocumentService:
    """文献文档服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.weknora = weknora_service

    async def _get_or_create_default_kb(self, user_id: int) -> str:
        """获取或为用户创建默认知识库"""
        # 这里简单处理，先尝试找现有的知识库，没有则创建一个名为 "Default" 的
        # 在实际生产中，可能需要一个单独的表来记录用户的知识库映射
        try:
            kbs = await self.weknora._request("GET", "/knowledge-bases")
            for kb in kbs.get("data", []):
                if kb.get("name") == f"User_{user_id}_Default":
                    return kb.get("id")
            
            # 没找到，创建一个
            # 必须指定 Embedding 模型，否则无法进行 RAG 问答
            # 同时绑定 LLM 模型用于后续的摘要和问答优化
            embedding_model_id = await self.weknora.get_embedding_model_id("text-embedding-v3")
            chat_model_id = await self.weknora.get_model_id_by_type("Chat")
            
            new_kb = await self.weknora.create_knowledge_base(
                name=f"User_{user_id}_Default", 
                description=f"Default knowledge base for user {user_id}",
                embedding_model_id=embedding_model_id,
                summary_model_id=chat_model_id
            )
            return new_kb.get("data", {}).get("id")
        except Exception as e:
            logger.error(f"获取或创建 WeKnora 知识库失败: {e}")
            return None

    async def create_document(self, title: str, file: UploadFile, user_id: int, kb_id: Optional[str] = None) -> dict:
        """
        创建文档 (第一阶段：保存文件并创建记录)
        """
        logger.info(f"开始创建文档任务: {title}")

        filename = file.filename or "document"
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext not in {"pdf", "txt", "docx", "md"}:
            raise ValueError("仅支持 PDF/TXT/DOCX/MD 文件")

        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        safe_name = f"doc_{uuid.uuid4().hex}.{ext}"
        save_path = os.path.join(settings.UPLOAD_DIR, safe_name)

        content = await file.read()
        if not content:
            raise ValueError("文件内容为空")

        with open(save_path, "wb") as f:
            f.write(content)

        # 初始化文档记录
        meta_info = {
            "filename": filename,
            "size": len(content),
            "ext": ext,
        }

        # 预先获取或创建默认知识库 ID
        weknora_kb_id = kb_id or await self._get_or_create_default_kb(user_id)

        doc = Document(
            user_id=user_id,
            title=title or os.path.splitext(filename)[0],
            content="",  # 暂时为空，异步处理时填充
            document_type="source",
            source_type="file",
            source_url=None,
            file_path=save_path,
            meta_info=json.dumps(meta_info, ensure_ascii=False),
            weknora_kb_id=weknora_kb_id,
            status="pending",
            processing_progress=0
        )
        self.db.add(doc)
        await self.db.commit()
        await self.db.refresh(doc)

        return self._format_document(doc)

    async def process_document_background(self, doc_id: int):
        """
        后台处理文档 (解析 + 同步到 WeKnora)
        """
        logger.info(f"开始后台处理文档: {doc_id}")
        
        # 获取最新的 session 进行操作
        async with self.db as session:
            try:
                # 重新查询文档
                query = select(Document).where(Document.id == doc_id)
                result = await session.execute(query)
                doc = result.scalars().first()
                
                if not doc:
                    logger.error(f"文档 {doc_id} 不存在，停止处理")
                    return

                # 更新状态：处理中
                doc.status = "processing"
                doc.processing_progress = 10
                await session.commit()

                # 1. 解析文件内容
                parsed_text = ""
                try:
                    ext = json.loads(doc.meta_info).get("ext", "")
                    parsed_text = self._parse_file(doc.file_path, ext)
                    if not parsed_text.strip():
                        raise ValueError("未解析到有效文本")
                    
                    doc.content = parsed_text
                    doc.processing_progress = 40
                    await session.commit()
                except Exception as e:
                    logger.error(f"解析文档失败: {e}")
                    doc.status = "failed"
                    doc.error_message = f"解析失败: {str(e)}"
                    await session.commit()
                    return

                # 2. 同步到 WeKnora
                if doc.weknora_kb_id:
                    try:
                        weknora_result = await self.weknora.upload_document_file(doc.weknora_kb_id, doc.file_path)
                        weknora_doc_id = weknora_result.get("data", {}).get("id")
                        
                        doc.weknora_knowledge_id = weknora_doc_id
                        doc.processing_progress = 80
                        logger.info(f"文档同步到 WeKnora 成功: {weknora_doc_id}")
                    except Exception as e:
                        logger.error(f"同步文档到 WeKnora 失败: {str(e)}")
                        if hasattr(e, "response") and hasattr(e.response, "text"):
                            logger.error(f"WeKnora 错误详情: {e.response.text}")
                        
                        # 同步失败暂不标记为整个任务失败，但记录错误
                        doc.error_message = f"WeKnora同步失败: {str(e)}"
                
                # 完成
                doc.status = "completed"
                doc.processing_progress = 100
                await session.commit()
                logger.info(f"文档 {doc_id} 处理完成")

            except Exception as e:
                logger.error(f"后台处理文档异常: {e}")
                # 尝试更新错误状态
                try:
                    doc.status = "failed"
                    doc.error_message = f"系统错误: {str(e)}"
                    await session.commit()
                except:
                    pass

    async def list_documents(self, skip: int, limit: int, category: Optional[str], user_id: int) -> List[dict]:
        """获取文档列表"""
        query = select(Document).where(Document.user_id == user_id)
        if category:
            query = query.where(Document.document_type == category)
        query = query.order_by(Document.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        docs = result.scalars().all()
        return [self._format_document(doc) for doc in docs]

    async def get_document(self, doc_id: int, user_id: int) -> dict:
        """获取文档详情 (本地数据库)"""
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

    async def update_document(self, doc_id: int, doc_data: Dict, user_id: int) -> dict:
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

        # 同步更新 WeKnora 中的标题
        if doc.weknora_knowledge_id:
            try:
                await self.weknora.update_document(doc.weknora_knowledge_id, title=doc.title)
            except Exception as e:
                logger.error(f"同步更新 WeKnora 标题失败: {e}")

        return self._format_document(doc)

    async def delete_document(self, doc_id: int, user_id: int) -> None:
        """删除文档"""
        query = select(Document).where(and_(Document.id == doc_id, Document.user_id == user_id))
        result = await self.db.execute(query)
        doc = result.scalars().first()
        if not doc:
            raise ValueError("文档不存在")

        # 同步从 WeKnora 删除
        if doc.weknora_knowledge_id:
            try:
                await self.weknora.delete_document(doc.weknora_knowledge_id)
            except Exception as e:
                logger.error(f"同步删除 WeKnora 文档失败: {e}")

        await self.db.execute(delete(DocumentSummary).where(DocumentSummary.document_id == doc.id))
        await self.db.delete(doc)
        await self.db.commit()

    # =====================
    # WeKnora 整合逻辑
    # =====================

    async def search_similar(self, query: str, knowledge_base_ids: List[str] = None, limit: int = 10) -> List[dict]:
        """使用 WeKnora 进行语义搜索"""
        logger.info(f"使用 WeKnora 搜索相似文献: {query}")
        # 如果没有提供知识库ID，这里可以默认搜索所有相关的或者默认的
        results = await self.weknora.knowledge_search(query, knowledge_base_ids, top_k=limit)
        return results

    async def get_document_details(self, doc_id: int) -> dict:
        """获取文档详情 (自动映射 ID)"""
        # 先查本地找到 WeKnora ID
        query = select(Document).where(Document.id == doc_id)
        result = await self.db.execute(query)
        doc = result.scalars().first()
        
        if doc and doc.weknora_knowledge_id:
            return await self.weknora.get_document(doc.weknora_knowledge_id)
        
        raise ValueError("文档未同步到 WeKnora 或不存在")

    async def summarize_document(self, doc_id: int, user_id: int) -> dict:
        """使用 WeKnora 内容生成文档摘要并持久化"""
        logger.info(f"开始为文档生成摘要: {doc_id}")
        
        query = select(Document).where(Document.id == doc_id)
        result = await self.db.execute(query)
        doc = result.scalars().first()
        
        if not doc:
            return {"success": False, "message": "文档不存在"}

        content = ""
        if doc.weknora_knowledge_id:
            content = await self.weknora.get_document_full_content(doc.weknora_knowledge_id)
        
        if not content:
            content = doc.content
        
        if not content:
            return {"success": False, "message": "未找到文档内容"}
        
        summary_text = await llm_service.generate_document_summary(content)
        
        # --- 持久化摘要到数据库 ---
        summary = DocumentSummary(
            document_id=doc.id,
            user_id=user_id,
            summary_level="paragraph",
            summary_text=summary_text,
            model_name=llm_service.model
        )
        self.db.add(summary)
        await self.db.commit()
        await self.db.refresh(summary)

        return {"success": True, "data": self._format_summary(summary)}

    async def get_document_concepts(self, doc_id: int) -> dict:
        """从 WeKnora 内容获取文档关键概念"""
        logger.info(f"开始提取文档关键概念: {doc_id}")
        
        query = select(Document).where(Document.id == doc_id)
        result = await self.db.execute(query)
        doc = result.scalars().first()
        
        if not doc: return {"success": False, "message": "文档不存在"}

        content = ""
        if doc.weknora_knowledge_id:
            content = await self.weknora.get_document_full_content(doc.weknora_knowledge_id)
        
        if not content: content = doc.content
        
        if not content: return {"success": False, "message": "未找到文档内容"}
        
        concepts = await llm_service.extract_document_concepts(content)
        return {"success": True, "data": concepts}

    async def get_document_citations(self, doc_id: int) -> dict:
        """从 WeKnora 内容获取文档引用关系"""
        logger.info(f"开始提取文档引用关系: {doc_id}")
        
        query = select(Document).where(Document.id == doc_id)
        result = await self.db.execute(query)
        doc = result.scalars().first()
        
        if not doc: return {"success": False, "message": "文档不存在"}

        content = ""
        if doc.weknora_knowledge_id:
            content = await self.weknora.get_document_full_content(doc.weknora_knowledge_id)
        
        if not content: content = doc.content
        
        if not content: return {"success": False, "message": "未找到文档内容"}
        
        citations = await llm_service.extract_document_citations(content)
        return {"success": True, "data": citations}

    # =====================
    # 辅助方法
    # =====================

    def _parse_file(self, path: str, ext: str) -> str:
        if ext == "pdf":
            return self._parse_pdf(path)
        if ext in {"txt", "md"}:
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
            "weknora_knowledge_id": doc.weknora_knowledge_id,
            "weknora_kb_id": doc.weknora_kb_id,
            "status": doc.status,
            "processing_progress": doc.processing_progress,
            "error_message": doc.error_message,
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
