"""
文献摘要服务层
提供文档处理和摘要生成逻辑
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile
import os

from app.utils.logger import get_logger
from app.services.weknora_service import weknora_service
from app.services.llm_service import llm_service
from app.core.config import settings

logger = get_logger(__name__)


class DocumentService:
    """文献文档服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.weknora = weknora_service
    
    async def create_document(self, title: str, file: UploadFile, knowledge_base_id: str) -> dict:
        """
        创建文档，并同步到 WeKnora 知识库
        """
        logger.info(f"开始创建文档: {title}")
        
        # 1. 保存临时文件
        temp_path = os.path.join(settings.UPLOAD_DIR, file.filename)
        with open(temp_path, "wb") as f:
            f.write(await file.read())
            
        try:
            # 2. 调用 WeKnora 进行解析和索引
            result = await self.weknora.upload_document(temp_path, knowledge_base_id)
            logger.info(f"WeKnora 文档上传成功: {result}")
            
            # 获取 WeKnora 返回的 data 对象中的 id
            weknora_data = result.get("data", {})
            weknora_id = weknora_data.get("id")
            
            # 3. TODO: 在本地数据库记录文档元数据
            return {
                "title": title,
                "weknora_id": weknora_id,
                "status": "processing"
            }
        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    async def search_similar(self, query: str, knowledge_base_ids: List[str], limit: int = 10) -> List[dict]:
        """
        使用 WeKnora 进行语义搜索
        """
        logger.info(f"使用 WeKnora 搜索相似文献: {query}")
        results = await self.weknora.search_knowledge(query, knowledge_base_ids, top_k=limit)
        return results

    async def get_document_details(self, doc_id: str) -> dict:
        """获取文档详情"""
        return await self.weknora.get_document(doc_id)

    async def summarize_document(self, doc_id: str) -> dict:
        """生成文档摘要"""
        logger.info(f"开始为文档生成摘要: {doc_id}")
        content = await self.weknora.get_document_full_content(doc_id)
        if not content:
            return {"success": False, "message": "未找到文档内容或文档尚未解析完成"}
        
        summary = await llm_service.generate_document_summary(content)
        return {"success": True, "data": {"summary": summary}}

    async def get_document_concepts(self, doc_id: str) -> dict:
        """获取文档关键概念"""
        logger.info(f"开始提取文档关键概念: {doc_id}")
        content = await self.weknora.get_document_full_content(doc_id)
        if not content:
            return {"success": False, "message": "未找到文档内容"}
        
        concepts = await llm_service.extract_document_concepts(content)
        return {"success": True, "data": concepts}

    async def get_document_citations(self, doc_id: str) -> dict:
        """获取文档引用关系"""
        logger.info(f"开始提取文档引用关系: {doc_id}")
        content = await self.weknora.get_document_full_content(doc_id)
        if not content:
            return {"success": False, "message": "未找到文档内容"}
        
        citations = await llm_service.extract_document_citations(content)
        return {"success": True, "data": citations}
