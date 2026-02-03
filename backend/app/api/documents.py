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
from typing import List, Optional
from pydantic import BaseModel

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
    return await weknora_service.create_knowledge_base({
        "name": request.name,
        "description": request.description
    })


@router.post("/ask")
async def ask_with_rag(
    request: AskRequest,
    current_user_id: int = Depends(get_current_user_id)
):
    """基于知识库回答问题 (RAG)"""
    from app.services.rag_service import rag_service
    
    # 如果没有提供知识库ID，尝试获取用户的默认知识库
    kb_ids = request.knowledge_base_ids
    if not kb_ids:
        from app.services.document_service import DocumentService
        # 这里只是一个占位逻辑，实际可以从 db 中获取
        kb_ids = [f"User_{current_user_id}_Default"]

    return await rag_service.answer_with_knowledge(
        request.query, 
        kb_ids, 
        request.session_id
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_document(
    title: str = Form(...),
    file: UploadFile = File(...),
    kb_id: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """上传新文档 (支持 PDF, TXT, DOCX, MD)"""
    try:
        service = DocumentService(db)
        result = await service.create_document(title, file, current_user_id, kb_id)
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
        result = await service.create_document_from_text(request.title, request.content, current_user_id, request.kb_id)
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
        result = await service.create_document_from_url(request.title, request.url, current_user_id, request.kb_id)
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
    category: Optional[str] = None,
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
async def get_document_details(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取文档详情"""
    try:
        service = DocumentService(db)
        # 优先从 WeKnora 获取，如果失败则回退到本地数据库
        try:
            return await service.get_document_details(doc_id)
        except Exception:
            result = await service.get_document(doc_id, current_user_id)
            return {"code": 200, "message": "获取成功 (本地)", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"获取文档失败: {e}")
        raise HTTPException(status_code=500, detail="获取失败")


@router.put("/{doc_id}")
async def update_document(
    doc_id: int,
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


@router.delete("/{doc_id}")
async def delete_document(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """删除文档"""
    try:
        service = DocumentService(db)
        await service.delete_document(doc_id, current_user_id)
        return {"code": 200, "message": "删除成功"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"删除文档失败: {e}")
        raise HTTPException(status_code=500, detail="删除失败")


@router.post("/{doc_id}/summarize")
async def summarize_document(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """生成文档摘要"""
    try:
        service = DocumentService(db)
        return await service.summarize_document(doc_id, current_user_id)
    except Exception as e:
        logger.error(f"生成摘要失败: {e}")
        raise HTTPException(status_code=500, detail="生成失败")


@router.get("/{doc_id}/concepts")
async def get_document_concepts(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取文档关键概念"""
    try:
        service = DocumentService(db)
        return await service.get_document_concepts(doc_id)
    except Exception as e:
        logger.error(f"获取概念失败: {e}")
        raise HTTPException(status_code=500, detail="获取失败")


@router.get("/{doc_id}/citations")
async def get_document_citations(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取文档引用关系"""
    try:
        service = DocumentService(db)
        return await service.get_document_citations(doc_id)
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
        result = await service.search_similar(request.query, request.knowledge_base_ids, request.limit)
        return {"code": 200, "message": "获取成功", "data": result}
    except Exception as e:
        logger.error(f"搜索文献失败: {e}")
        raise HTTPException(status_code=500, detail="搜索失败")
