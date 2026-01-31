"""
文献摘要处理模块 API

Endpoints:
  POST   /api/v1/documents                    - 上传文档
  GET    /api/v1/documents                    - 获取文档列表
  GET    /api/v1/documents/{doc_id}           - 获取文档详情
  PUT    /api/v1/documents/{doc_id}           - 更新文档
  DELETE /api/v1/documents/{doc_id}           - 删除文档
  POST   /api/v1/documents/{doc_id}/summarize - 生成摘要
  GET    /api/v1/documents/{doc_id}/concepts  - 获取关键概念
  GET    /api/v1/documents/{doc_id}/citations - 获取引用关系
  POST   /api/v1/documents/search             - 相似文献搜索
"""

from fastapi import APIRouter, Depends, status, UploadFile, File, Body, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.services.document_service import DocumentService
from app.services.rag_service import rag_service
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


class SearchRequest(BaseModel):
    query: str
    knowledge_base_ids: List[str]
    limit: Optional[int] = 10


class AskRequest(BaseModel):
    query: str
    knowledge_base_ids: List[str]
    session_id: Optional[str] = None


class KBCreateRequest(BaseModel):
    name: str
    description: Optional[str] = ""


class DocUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None


@router.post("/knowledge-bases", status_code=status.HTTP_201_CREATED)
async def create_knowledge_base(
    request: KBCreateRequest
):
    """在 WeKnora 中创建新的知识库"""
    from app.services.weknora_service import weknora_service
    return await weknora_service.create_knowledge_base(request.name, request.description)


@router.post("/ask")
async def ask_with_rag(
    request: AskRequest
):
    """基于知识库回答问题 (RAG)"""
    return await rag_service.answer_with_knowledge(
        request.query, 
        request.knowledge_base_ids, 
        request.session_id
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_document(
    title: str,
    knowledge_base_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """上传新文档"""
    service = DocumentService(db)
    return await service.create_document(title, file, knowledge_base_id)


@router.get("/")
async def list_documents(
    knowledge_base_id: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取指定知识库下的文档列表"""
    if not knowledge_base_id:
        return {"data": [], "total": 0, "success": True, "message": "请提供 knowledge_base_id 以获取文档列表"}
    
    # 兼容 skip/limit 模式
    actual_page = page
    actual_size = page_size
    if skip > 0 or limit != 20:
        actual_size = limit
        actual_page = (skip // limit) + 1

    from app.services.weknora_service import weknora_service
    return await weknora_service.list_documents(knowledge_base_id, actual_page, actual_size)


@router.get("/{doc_id}")
async def get_document_details(
    doc_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取文档详情"""
    from app.services.weknora_service import weknora_service
    return await weknora_service.get_document(doc_id)


@router.put("/{doc_id}")
async def update_document(
    doc_id: str,
    request: DocUpdateRequest,
    title: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """更新文档信息"""
    from app.services.weknora_service import weknora_service
    
    # 优先使用 Body 中的参数，如果没有则使用 Query 中的参数
    final_title = request.title or title
    # 优先使用 description，如果没有则尝试使用 category (Body 或 Query)
    final_desc = request.description or request.category or category
    
    return await weknora_service.update_document(doc_id, final_title, final_desc)


@router.delete("/{doc_id}")
async def delete_document(
    doc_id: str,
    db: AsyncSession = Depends(get_db)
):
    """删除文档"""
    from app.services.weknora_service import weknora_service
    return await weknora_service.delete_document(doc_id)


@router.post("/{doc_id}/summarize")
async def summarize_document(
    doc_id: str,
    db: AsyncSession = Depends(get_db)
):
    """生成文档摘要"""
    from app.services.weknora_service import weknora_service
    return await weknora_service.summarize_document(doc_id)


@router.get("/{doc_id}/concepts")
async def get_document_concepts(
    doc_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取文档关键概念"""
    from app.services.weknora_service import weknora_service
    return await weknora_service.get_document_concepts(doc_id)


@router.get("/{doc_id}/citations")
async def get_document_citations(
    doc_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取文档引用关系"""
    from app.services.weknora_service import weknora_service
    return await weknora_service.get_document_citations(doc_id)


@router.post("/search")
async def search_similar_documents(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db)
):
    """搜索相似文献"""
    service = DocumentService(db)
    return await service.search_similar(request.query, request.knowledge_base_ids, request.limit)
