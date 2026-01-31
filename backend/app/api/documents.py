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

from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.core.auth import get_current_user_id
from app.services.document_service import DocumentService
from app.schemas.document import (
    DocumentCreateText,
    DocumentCreateUrl,
    DocumentUpdate,
    DocumentSummaryRequest,
    DocumentSearchRequest,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_document(
    title: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """上传新文档"""
    try:
        service = DocumentService(db)
        result = await service.create_document(title, file, current_user_id)
        return {"code": 200, "message": "上传成功", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"上传文档失败: {e}")
        raise HTTPException(status_code=500, detail="上传失败")


@router.post("/text", status_code=status.HTTP_201_CREATED)
async def upload_document_text(
    request: DocumentCreateText,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """文本上传"""
    try:
        service = DocumentService(db)
        result = await service.create_document_from_text(request.title, request.content, current_user_id)
        return {"code": 200, "message": "上传成功", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"文本上传失败: {e}")
        raise HTTPException(status_code=500, detail="上传失败")


@router.post("/url", status_code=status.HTTP_201_CREATED)
async def upload_document_url(
    request: DocumentCreateUrl,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """URL导入"""
    try:
        service = DocumentService(db)
        result = await service.create_document_from_url(request.title, request.url, current_user_id)
        return {"code": 200, "message": "导入成功", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"URL导入失败: {e}")
        raise HTTPException(status_code=500, detail="导入失败")


@router.get("/")
async def list_documents(
    skip: int = 0,
    limit: int = 10,
    category: str = None,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取文档列表"""
    try:
        service = DocumentService(db)
        result = await service.list_documents(skip, limit, category, current_user_id)
        return {"code": 200, "message": "获取成功", "data": result}
    except Exception as e:
        logger.error(f"获取文档列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取失败")


@router.get("/{doc_id}")
async def get_document(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取文档详情"""
    try:
        service = DocumentService(db)
        result = await service.get_document(doc_id, current_user_id)
        return {"code": 200, "message": "获取成功", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"获取文档失败: {e}")
        raise HTTPException(status_code=500, detail="获取失败")


@router.put("/{doc_id}")
async def update_document(
    doc_id: str,
    request: DocumentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """更新文档信息"""
    try:
        service = DocumentService(db)
        result = await service.update_document(doc_id, request.model_dump(), current_user_id)
        return {"code": 200, "message": "更新成功", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"更新文档失败: {e}")
        raise HTTPException(status_code=500, detail="更新失败")


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """删除文档"""
    try:
        service = DocumentService(db)
        await service.delete_document(doc_id, current_user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"删除文档失败: {e}")
        raise HTTPException(status_code=500, detail="删除失败")


@router.post("/{doc_id}/summarize")
async def summarize_document(
    doc_id: str,
    request: DocumentSummaryRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """生成文档摘要"""
    try:
        service = DocumentService(db)
        result = await service.generate_summary(doc_id, request.summary_level, current_user_id)
        return {"code": 200, "message": "生成成功", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"生成摘要失败: {e}")
        raise HTTPException(status_code=500, detail="生成失败")


@router.get("/{doc_id}/concepts")
async def get_document_concepts(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取文档关键概念"""
    try:
        service = DocumentService(db)
        result = await service.get_concepts(doc_id, current_user_id)
        return {"code": 200, "message": "获取成功", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"获取概念失败: {e}")
        raise HTTPException(status_code=500, detail="获取失败")


@router.get("/{doc_id}/citations")
async def get_document_citations(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取文档引用关系"""
    try:
        service = DocumentService(db)
        result = await service.get_citations(doc_id, current_user_id)
        return {"code": 200, "message": "获取成功", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"获取引用失败: {e}")
        raise HTTPException(status_code=500, detail="获取失败")


@router.post("/search")
async def search_similar_documents(
    request: DocumentSearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """搜索相似文献"""
    try:
        service = DocumentService(db)
        result = await service.search_similar(request.query, request.limit, current_user_id)
        return {"code": 200, "message": "获取成功", "data": result}
    except Exception as e:
        logger.error(f"搜索文献失败: {e}")
        raise HTTPException(status_code=500, detail="搜索失败")
