"""
多语言翻译模块 API
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.base_services import TranslationService
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_translation_task(
    source_language: str,
    target_language: str,
    input_text: str,
    db: AsyncSession = Depends(get_db)
):
    """创建翻译任务"""
    service = TranslationService(db)
    return await service.create_task({
        "source_language": source_language,
        "target_language": target_language,
        "input_text": input_text
    })


@router.get("/")
async def list_translation_tasks(
    skip: int = 0,
    limit: int = 10,
    status: str = None,
    db: AsyncSession = Depends(get_db)
):
    """获取翻译任务列表"""
    service = TranslationService(db)
    return await service.list_tasks(skip, limit, status)


@router.get("/{task_id}")
async def get_translation_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取任务详情"""
    service = TranslationService(db)
    return await service.get_task(task_id)


@router.put("/{task_id}")
async def update_translation_task(
    task_id: str,
    input_text: str = None,
    db: AsyncSession = Depends(get_db)
):
    """更新任务"""
    service = TranslationService(db)
    return await service.update_task(task_id, {"input_text": input_text})


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_translation_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """删除任务"""
    service = TranslationService(db)
    await service.delete_task(task_id)


@router.get("/terminology/")
async def get_terminology(
    domain: str = None,
    db: AsyncSession = Depends(get_db)
):
    """获取术语库"""
    service = TranslationService(db)
    return await service.get_terminology(domain)


@router.post("/terminology/add")
async def add_terminology(
    original_term: str,
    translation: str,
    domain: str,
    db: AsyncSession = Depends(get_db)
):
    """添加自定义术语"""
    service = TranslationService(db)
    return await service.add_terminology({
        "original_term": original_term,
        "translation": translation,
        "domain": domain
    })


@router.post("/{task_id}/rate")
async def rate_translation(
    task_id: str,
    rating: int,
    feedback: str = None,
    db: AsyncSession = Depends(get_db)
):
    """评分翻译结果"""
    service = TranslationService(db)
    return await service.rate_translation(task_id, rating, feedback)
