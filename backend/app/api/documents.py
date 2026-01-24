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

from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.services.document_service import DocumentService
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_document(
    title: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """上传新文档"""
    service = DocumentService(db)
    return await service.create_document(title, file)


@router.get("/")
async def list_documents(
    skip: int = 0,
    limit: int = 10,
    category: str = None,
    db: AsyncSession = Depends(get_db)
):
    """获取文档列表"""
    service = DocumentService(db)
    return await service.list_documents(skip, limit, category)


@router.get("/{doc_id}")
async def get_document(
    doc_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取文档详情"""
    service = DocumentService(db)
    return await service.get_document(doc_id)


@router.put("/{doc_id}")
async def update_document(
    doc_id: str,
    title: str = None,
    category: str = None,
    db: AsyncSession = Depends(get_db)
):
    """更新文档信息"""
    service = DocumentService(db)
    return await service.update_document(doc_id, {"title": title, "category": category})


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: str,
    db: AsyncSession = Depends(get_db)
):
    """删除文档"""
    service = DocumentService(db)
    await service.delete_document(doc_id)


@router.post("/{doc_id}/summarize")
async def summarize_document(
    doc_id: str,
    summary_level: str = "paragraph",
    db: AsyncSession = Depends(get_db)
):
    """生成文档摘要"""
    service = DocumentService(db)
    return await service.generate_summary(doc_id, summary_level)


@router.get("/{doc_id}/concepts")
async def get_document_concepts(
    doc_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取文档关键概念"""
    service = DocumentService(db)
    return await service.get_concepts(doc_id)


@router.get("/{doc_id}/citations")
async def get_document_citations(
    doc_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取文档引用关系"""
    service = DocumentService(db)
    return await service.get_citations(doc_id)


@router.post("/search")
async def search_similar_documents(
    query: str,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """搜索相似文献"""
    service = DocumentService(db)
    return await service.search_similar(query, limit)
