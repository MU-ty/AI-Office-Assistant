"""
学术润色模块 API
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.base_services import PolishService
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_polish_task(
    input_text: str,
    polish_level: str = "standard",
    db: AsyncSession = Depends(get_db)
):
    """创建学术润色任务"""
    service = PolishService(db)
    return await service.create_task({"input_text": input_text, "polish_level": polish_level})


@router.get("/")
async def list_polish_tasks(
    skip: int = 0,
    limit: int = 10,
    status: str = None,
    db: AsyncSession = Depends(get_db)
):
    """获取润色任务列表"""
    service = PolishService(db)
    return await service.list_tasks(skip, limit, status)


@router.get("/{task_id}")
async def get_polish_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取任务详情"""
    service = PolishService(db)
    return await service.get_task(task_id)


@router.put("/{task_id}")
async def update_polish_task(
    task_id: str,
    input_text: str = None,
    db: AsyncSession = Depends(get_db)
):
    """更新任务"""
    service = PolishService(db)
    return await service.update_task(task_id, {"input_text": input_text})


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_polish_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """删除任务"""
    service = PolishService(db)
    await service.delete_task(task_id)


@router.get("/{task_id}/issues")
async def get_polish_issues(
    task_id: str,
    filter_type: str = None,
    db: AsyncSession = Depends(get_db)
):
    """获取润色问题列表"""
    service = PolishService(db)
    return await service.get_issues(task_id, filter_type)


@router.post("/{task_id}/accept/{issue_id}")
async def accept_polish_suggestion(
    task_id: str,
    issue_id: str,
    db: AsyncSession = Depends(get_db)
):
    """接受润色建议"""
    service = PolishService(db)
    return await service.accept_suggestion(task_id, issue_id)


@router.post("/{task_id}/reject/{issue_id}")
async def reject_polish_suggestion(
    task_id: str,
    issue_id: str,
    db: AsyncSession = Depends(get_db)
):
    """拒绝润色建议"""
    service = PolishService(db)
    return await service.reject_suggestion(task_id, issue_id)


@router.get("/{task_id}/export")
async def export_polish_result(
    task_id: str,
    format: str = "markdown",
    db: AsyncSession = Depends(get_db)
):
    """导出润色结果"""
    service = PolishService(db)
    return await service.export_result(task_id, format)
