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

from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.core.auth import get_current_user_id
from app.services.document_service import DocumentService
from app.schemas.document import (
    DocumentUpdate,
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
    embedding_model_id: Optional[str] = None


class KBCreateRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    embedding_model_id: Optional[str] = None
    summary_model_id: Optional[str] = None
    rerank_model_id: Optional[str] = None


@router.post("/knowledge-bases", status_code=status.HTTP_201_CREATED)
async def create_knowledge_base(
    request: KBCreateRequest
):
    """在 WeKnora 中创建新的知识库"""
    from app.services.weknora_service import weknora_service
    
    # 模型 ID 自动化处理
    embedding_model_id = request.embedding_model_id
    if not embedding_model_id:
        embedding_model_id = await weknora_service.get_embedding_model_id("text-embedding-v3")
    
    summary_model_id = request.summary_model_id
    if not summary_model_id:
        summary_model_id = await weknora_service.get_model_id_by_type("Chat")
    
    rerank_model_id = request.rerank_model_id
    if not rerank_model_id:
        rerank_model_id = await weknora_service.get_model_id_by_type("Rerank")

    return await weknora_service.create_knowledge_base({
        "name": request.name,
        "description": request.description,
        "embedding_model_id": embedding_model_id,
        "summary_model_id": summary_model_id,
        "rerank_model_id": rerank_model_id
    })


@router.post("/ask")
async def ask_with_rag(
    request: AskRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """基于知识库回答问题 (RAG)"""
    from app.services.rag_service import rag_service
    from app.services.document_service import DocumentService
    
    kb_ids = request.knowledge_base_ids
    if not kb_ids:
        service = DocumentService(db)
        default_kb_id = await service._get_or_create_default_kb(current_user_id)
        kb_ids = [default_kb_id] if default_kb_id else []

    return await rag_service.answer_with_knowledge(
        request.query, 
        kb_ids, 
        request.session_id
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    file: UploadFile = File(...),
    kb_id: Optional[int] = Form(None),
    dir_id: Optional[int] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """上传新文档 (异步处理：支持 PDF, TXT, DOCX, MD)"""
    try:
        service = DocumentService(db)
        # 1. 第一阶段：保存文件并创建记录
        result = await service.create_document(title, file, current_user_id, kb_id, dir_id)
        
        # 2. 第二阶段：触发后台处理任务
        background_tasks.add_task(service.process_document_background, result["id"])
        
        return {"code": 200, "message": "文件已上传，正在后台处理", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"上传文档失败: {e}")
        raise HTTPException(status_code=500, detail="上传失败")


@router.get("/{doc_id}/status")
async def get_document_status(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """查询文档处理状态"""
    try:
        service = DocumentService(db)
        doc = await service.get_document(doc_id, current_user_id)
        return {
            "code": 200, 
            "data": {
                "id": doc["id"],
                "status": doc.get("status"),
                "progress": doc.get("processing_progress"),
                "error": doc.get("error_message")
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"获取文档状态失败: {e}")
        raise HTTPException(status_code=500, detail="获取失败")


@router.get("/")
async def list_documents(
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None,
    knowledge_base_id: Optional[int] = None,
    directory_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取文档列表"""
    try:
        service = DocumentService(db)
        result = await service.list_documents(
            skip, 
            limit, 
            category, 
            current_user_id,
            knowledge_base_id,
            directory_id
        )
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
        # try:
        #     return await service.get_document_details(doc_id)
        # except Exception:
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
