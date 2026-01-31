"""
多语言翻译模块 API
"""

from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user_id
from app.schemas.translation import (
    TranslationCreateRequest,
    TranslationUpdateRequest,
    TranslationRateRequest,
    TranslationExportRequest,
    TerminologyCreateRequest,
)
from app.services.base_services import TranslationService
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_translation_task(
    request: TranslationCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """创建翻译任务"""
    try:
        service = TranslationService(db)
        result = await service.create_task(
            {
                "source_language": request.source_language,
                "target_language": request.target_language,
                "input_text": request.input_text,
                "domain": request.domain,
            },
            user_id=current_user_id,
        )
        return {"code": 200, "message": "创建成功", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"创建翻译任务失败: {e}")
        raise HTTPException(status_code=500, detail="创建失败")


@router.get("/")
async def list_translation_tasks(
    skip: int = 0,
    limit: int = 10,
    status: str = None,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取翻译任务列表"""
    try:
        service = TranslationService(db)
        result = await service.list_tasks(current_user_id, skip, limit, status)
        return {"code": 200, "message": "获取成功", "data": result}
    except Exception as e:
        logger.error(f"获取翻译任务失败: {e}")
        raise HTTPException(status_code=500, detail="获取失败")


@router.get("/terminology")
@router.get("/terminology/")
async def get_terminology(
    domain: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取术语库"""
    try:
        service = TranslationService(db)
        result = await service.get_terminology(current_user_id, domain)
        return {"code": 200, "message": "获取成功", "data": result}
    except Exception as e:
        logger.error(f"获取术语失败: {e}")
        raise HTTPException(status_code=500, detail="获取失败")


@router.get("/{task_id}")
async def get_translation_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取任务详情"""
    try:
        service = TranslationService(db)
        result = await service.get_task(task_id, current_user_id)
        return {"code": 200, "message": "获取成功", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"获取翻译任务失败: {e}")
        raise HTTPException(status_code=500, detail="获取失败")


@router.put("/{task_id}")
async def update_translation_task(
    task_id: str,
    request: TranslationUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """更新任务"""
    try:
        service = TranslationService(db)
        result = await service.update_task(task_id, request.model_dump(), current_user_id)
        return {"code": 200, "message": "更新成功", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"更新翻译任务失败: {e}")
        raise HTTPException(status_code=500, detail="更新失败")


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_translation_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """删除任务"""
    try:
        service = TranslationService(db)
        await service.delete_task(task_id, current_user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"删除翻译任务失败: {e}")
        raise HTTPException(status_code=500, detail="删除失败")


@router.post("/terminology/add")
async def add_terminology(
    request: TerminologyCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """添加自定义术语"""
    try:
        service = TranslationService(db)
        result = await service.add_terminology(request.model_dump(), current_user_id)
        return {"code": 200, "message": "添加成功", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"添加术语失败: {e}")
        raise HTTPException(status_code=500, detail="添加失败")


@router.post("/{task_id}/rate")
async def rate_translation(
    task_id: str,
    request: TranslationRateRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """评分翻译结果"""
    try:
        service = TranslationService(db)
        result = await service.rate_translation(task_id, request.rating, request.feedback, current_user_id)
        return {"code": 200, "message": "提交成功", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"评分失败: {e}")
        raise HTTPException(status_code=500, detail="提交失败")


@router.post("/{task_id}/export")
async def export_translation(
    task_id: str,
    request: TranslationExportRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """导出翻译结果"""
    try:
        service = TranslationService(db)
        result = await service.export_result(task_id, request.format, current_user_id)
        return {"code": 200, "message": "导出成功", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"导出失败: {e}")
        raise HTTPException(status_code=500, detail="导出失败")
