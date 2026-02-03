"""
WeKnora 知识库接入 API
"""

import json
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from typing import Optional

from app.core.auth import get_current_user_id
from app.schemas.weknora import (
    AgentChatRequest,
    KnowledgeBasePayload,
    KnowledgeChatRequest,
    KnowledgeSearchRequest,
    KnowledgeUrlCreate,
)
from app.services.weknora_service import weknora_service
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/knowledge-bases")
async def list_knowledge_bases(
    current_user_id: int = Depends(get_current_user_id)
):
    """获取知识库列表"""
    try:
        result = await weknora_service.list_knowledge_bases()
        return {"code": 200, "message": "获取成功", "data": result}
    except Exception as e:
        logger.error("获取知识库列表失败: %s", e)
        raise HTTPException(status_code=500, detail="获取失败")


@router.post("/knowledge-bases")
async def create_knowledge_base(
    payload: KnowledgeBasePayload,
    current_user_id: int = Depends(get_current_user_id)
):
    """创建知识库"""
    try:
        result = await weknora_service.create_knowledge_base(payload.model_dump(exclude_none=True))
        return {"code": 200, "message": "创建成功", "data": result}
    except Exception as e:
        logger.error("创建知识库失败: %s", e)
        raise HTTPException(status_code=500, detail="创建失败")


@router.get("/knowledge-bases/{kb_id}")
async def get_knowledge_base(
    kb_id: str,
    current_user_id: int = Depends(get_current_user_id)
):
    """获取知识库详情"""
    try:
        result = await weknora_service.get_knowledge_base(kb_id)
        return {"code": 200, "message": "获取成功", "data": result}
    except Exception as e:
        logger.error("获取知识库详情失败: %s", e)
        raise HTTPException(status_code=500, detail="获取失败")


@router.put("/knowledge-bases/{kb_id}")
async def update_knowledge_base(
    kb_id: str,
    payload: KnowledgeBasePayload,
    current_user_id: int = Depends(get_current_user_id)
):
    """更新知识库"""
    try:
        result = await weknora_service.update_knowledge_base(
            kb_id,
            payload.model_dump(exclude_none=True)
        )
        return {"code": 200, "message": "更新成功", "data": result}
    except Exception as e:
        logger.error("更新知识库失败: %s", e)
        raise HTTPException(status_code=500, detail="更新失败")


@router.delete("/knowledge-bases/{kb_id}")
async def delete_knowledge_base(
    kb_id: str,
    current_user_id: int = Depends(get_current_user_id)
):
    """删除知识库"""
    try:
        result = await weknora_service.delete_knowledge_base(kb_id)
        return {"code": 200, "message": "删除成功", "data": result}
    except Exception as e:
        logger.error("删除知识库失败: %s", e)
        raise HTTPException(status_code=500, detail="删除失败")


@router.get("/knowledge-bases/{kb_id}/knowledge")
async def list_knowledge(
    kb_id: str,
    page: int = 1,
    page_size: int = 20,
    tag_id: Optional[str] = None,
    current_user_id: int = Depends(get_current_user_id)
):
    """获取知识库下的知识列表"""
    try:
        params = {"page": page, "page_size": page_size}
        if tag_id:
            params["tag_id"] = tag_id
        result = await weknora_service.list_knowledge(kb_id, params)
        return {"code": 200, "message": "获取成功", "data": result}
    except Exception as e:
        logger.error("获取知识列表失败: %s", e)
        raise HTTPException(status_code=500, detail="获取失败")


@router.post("/knowledge-bases/{kb_id}/knowledge/file")
async def upload_knowledge_file(
    kb_id: str,
    file: UploadFile = File(...),
    metadata: Optional[str] = Form(default=None),
    enable_multimodel: Optional[bool] = Form(default=None),
    fileName: Optional[str] = Form(default=None),
    current_user_id: int = Depends(get_current_user_id)
):
    """上传文件到知识库"""
    try:
        file_bytes = await file.read()
        data = {}
        if metadata:
            try:
                data["metadata"] = json.loads(metadata)
            except json.JSONDecodeError:
                data["metadata"] = metadata
        if enable_multimodel is not None:
            data["enable_multimodel"] = str(enable_multimodel).lower()
        if fileName:
            data["fileName"] = fileName

        result = await weknora_service.upload_knowledge_file(
            kb_id=kb_id,
            file_name=file.filename,
            file_bytes=file_bytes,
            content_type=file.content_type,
            data=data,
        )
        return {"code": 200, "message": "上传成功", "data": result}
    except Exception as e:
        logger.error("上传知识文件失败: %s", e)
        raise HTTPException(status_code=500, detail="上传失败")


@router.post("/knowledge-bases/{kb_id}/knowledge/url")
async def create_knowledge_url(
    kb_id: str,
    payload: KnowledgeUrlCreate,
    current_user_id: int = Depends(get_current_user_id)
):
    """从 URL 创建知识"""
    try:
        result = await weknora_service.create_knowledge_url(kb_id, payload.model_dump(exclude_none=True))
        return {"code": 200, "message": "创建成功", "data": result}
    except Exception as e:
        logger.error("创建 URL 知识失败: %s", e)
        raise HTTPException(status_code=500, detail="创建失败")


@router.get("/knowledge/{knowledge_id}")
async def get_knowledge(
    knowledge_id: str,
    current_user_id: int = Depends(get_current_user_id)
):
    """获取知识详情"""
    try:
        result = await weknora_service.get_knowledge(knowledge_id)
        return {"code": 200, "message": "获取成功", "data": result}
    except Exception as e:
        logger.error("获取知识详情失败: %s", e)
        raise HTTPException(status_code=500, detail="获取失败")


@router.delete("/knowledge/{knowledge_id}")
async def delete_knowledge(
    knowledge_id: str,
    current_user_id: int = Depends(get_current_user_id)
):
    """删除知识"""
    try:
        result = await weknora_service.delete_knowledge(knowledge_id)
        return {"code": 200, "message": "删除成功", "data": result}
    except Exception as e:
        logger.error("删除知识失败: %s", e)
        raise HTTPException(status_code=500, detail="删除失败")


@router.post("/knowledge-search")
async def knowledge_search(
    payload: KnowledgeSearchRequest,
    current_user_id: int = Depends(get_current_user_id)
):
    """知识库搜索"""
    try:
        result = await weknora_service.knowledge_search(payload.model_dump(exclude_none=True))
        return {"code": 200, "message": "搜索成功", "data": result}
    except Exception as e:
        logger.error("知识搜索失败: %s", e)
        raise HTTPException(status_code=500, detail="搜索失败")


@router.post("/knowledge-chat/{session_id}")
async def knowledge_chat(
    session_id: str,
    payload: KnowledgeChatRequest,
    current_user_id: int = Depends(get_current_user_id)
):
    """基于知识库的问答（SSE 转发）"""
    try:
        async def event_stream():
            async for chunk in weknora_service.knowledge_chat_stream(
                session_id,
                payload.model_dump(exclude_none=True)
            ):
                yield chunk

        return StreamingResponse(event_stream(), media_type="text/event-stream")
    except Exception as e:
        logger.error("知识库问答失败: %s", e)
        raise HTTPException(status_code=500, detail="问答失败")


@router.post("/agent-chat/{session_id}")
async def agent_chat(
    session_id: str,
    payload: AgentChatRequest,
    current_user_id: int = Depends(get_current_user_id)
):
    """基于 Agent 的问答（SSE 转发）"""
    try:
        async def event_stream():
            async for chunk in weknora_service.agent_chat_stream(
                session_id,
                payload.model_dump(exclude_none=True)
            ):
                yield chunk

        return StreamingResponse(event_stream(), media_type="text/event-stream")
    except Exception as e:
        logger.error("Agent 问答失败: %s", e)
        raise HTTPException(status_code=500, detail="问答失败")
