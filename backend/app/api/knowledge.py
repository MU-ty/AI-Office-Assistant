
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user_id
from app.services.knowledge_service import KnowledgeService

router = APIRouter()

# Schemas
class KBCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_public: bool = False

class KBResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_public: bool
    owner_id: int

class DirectoryCreate(BaseModel):
    name: str
    kb_id: int
    parent_id: Optional[int] = None

class DirectoryMove(BaseModel):
    new_parent_id: Optional[int]
    new_order: int = 0

class TagCreate(BaseModel):
    name: str
    color: str = "#blue"

# Endpoints

@router.post("/knowledge-bases", response_model=KBResponse)
async def create_knowledge_base(
    data: KBCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    service = KnowledgeService(db)
    return await service.create_knowledge_base(data.name, user_id, data.description, data.is_public)

@router.get("/knowledge-bases", response_model=List[KBResponse])
async def list_knowledge_bases(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    service = KnowledgeService(db)
    return await service.list_knowledge_bases(user_id)

@router.get("/knowledge-bases/{kb_id}/tree")
async def get_directory_tree(
    kb_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    service = KnowledgeService(db)
    return await service.get_directory_tree(kb_id)

@router.post("/directories")
async def create_directory(
    data: DirectoryCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    service = KnowledgeService(db)
    return await service.create_directory(data.name, data.kb_id, data.parent_id)

@router.put("/directories/{dir_id}/move")
async def move_directory(
    dir_id: int,
    data: DirectoryMove,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    service = KnowledgeService(db)
    try:
        return await service.move_directory(dir_id, data.new_parent_id, data.new_order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/knowledge-bases/{kb_id}")
async def delete_knowledge_base(
    kb_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    service = KnowledgeService(db)
    try:
        await service.delete_knowledge_base(kb_id, user_id)
        return {"message": "知识库删除成功"}
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.delete("/directories/{dir_id}")
async def delete_directory(
    dir_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    service = KnowledgeService(db)
    try:
        await service.delete_directory(dir_id)
        return {"message": "目录删除成功"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/tags")
async def create_tag(
    data: TagCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    service = KnowledgeService(db)
    return await service.create_tag(data.name, data.color)

@router.get("/tags")
async def list_tags(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    service = KnowledgeService(db)
    return await service.list_tags()

@router.post("/documents/{doc_id}/tags")
async def add_tags_to_document(
    doc_id: int,
    tags: List[str],
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    service = KnowledgeService(db)
    try:
        await service.add_tags_to_document(doc_id, tags)
        return {"message": "标签添加成功"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
