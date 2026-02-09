
from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import StreamingResponse
from typing import List, Dict, Optional, Any
from pydantic import BaseModel

from app.core.auth import get_current_user
from app.models.user import User
from app.services.rag_service import rag_service
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    history: List[Dict[str, str]] = []
    knowledge_base_ids: List[int] = []
    top_k: int = 5

@router.post("/knowledge")
async def chat_knowledge(
    request: ChatRequest,
    current_user_id: int = Depends(get_current_user)
):
    """
    知识库问答 (流式)
    """
    return StreamingResponse(
        rag_service.chat_stream(
            query=request.query,
            history=request.history,
            knowledge_base_ids=request.knowledge_base_ids,
            top_k=request.top_k
        ),
        media_type="text/event-stream"
    )
