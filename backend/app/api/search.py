
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.services.search_service import search_service

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None
    page: int = 1
    size: int = 10

@router.post("/search")
async def search_documents(request: SearchRequest):
    """
    全文检索 (Elasticsearch)
    支持 filters: {"document_type": "pdf", "knowledge_base_id": 1}
    """
    return await search_service.search(
        request.query, 
        request.filters, 
        request.page, 
        request.size
    )
