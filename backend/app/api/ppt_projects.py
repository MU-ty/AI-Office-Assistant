"""
PPT生成模块 API
"""

from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user_id
from app.schemas.ppt import (
    PPTCreateRequest,
    PPTUpdateRequest,
    PPTGenerateRequest,
    PPTExportRequest,
)
from app.services.base_services import PPTService
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_ppt_project(
    request: PPTCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """创建PPT项目"""
    try:
        service = PPTService(db)
        result = await service.create_project(
            {
                "title": request.title,
                "description": request.description,
                "source_content": request.source_content,
                "theme": request.theme,
                "theme_palette": request.theme_palette,
            },
            user_id=current_user_id,
        )
        return {"code": 200, "message": "创建成功", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"创建项目失败: {e}")
        raise HTTPException(status_code=500, detail="创建失败")


@router.post("/import", status_code=status.HTTP_201_CREATED)
async def import_ppt_project(
    title: str,
    file: UploadFile = File(...),
    description: str = None,
    theme: str = None,
    theme_palette: str = None,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """导入Markdown/Word/PDF内容"""
    try:
        service = PPTService(db)
        result = await service.create_project_from_file(
            title=title,
            file=file,
            description=description,
            theme=theme,
            theme_palette=theme_palette,
            user_id=current_user_id
        )
        return {"code": 200, "message": "导入成功", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"导入失败: {e}")
        raise HTTPException(status_code=500, detail="导入失败")


@router.get("/")
async def list_ppt_projects(
    skip: int = 0,
    limit: int = 10,
    status: str = None,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取PPT项目列表"""
    try:
        service = PPTService(db)
        result = await service.list_projects(current_user_id, skip, limit, status)
        return {"code": 200, "message": "获取成功", "data": result}
    except Exception as e:
        logger.error(f"获取项目失败: {e}")
        raise HTTPException(status_code=500, detail="获取失败")


@router.get("/{project_id}")
async def get_ppt_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取项目详情"""
    try:
        service = PPTService(db)
        result = await service.get_project(project_id, current_user_id)
        return {"code": 200, "message": "获取成功", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"获取项目失败: {e}")
        raise HTTPException(status_code=500, detail="获取失败")


@router.put("/{project_id}")
async def update_ppt_project(
    project_id: int,
    request: PPTUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """更新项目"""
    try:
        service = PPTService(db)
        result = await service.update_project(project_id, request.model_dump(), current_user_id)
        return {"code": 200, "message": "更新成功", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"更新项目失败: {e}")
        raise HTTPException(status_code=500, detail="更新失败")


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ppt_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """删除项目"""
    try:
        service = PPTService(db)
        await service.delete_project(project_id, current_user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"删除项目失败: {e}")
        raise HTTPException(status_code=500, detail="删除失败")


@router.post("/{project_id}/generate")
async def generate_ppt_slides(
    project_id: int,
    request: PPTGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """生成幻灯片"""
    try:
        service = PPTService(db)
        result = await service.generate_slides(
            project_id,
            current_user_id,
            request.tone,
            request.theme,
            request.theme_palette,
        )
        return {"code": 200, "message": "生成成功", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"生成失败: {e}")
        raise HTTPException(status_code=500, detail="生成失败")


@router.get("/{project_id}/slides")
async def get_ppt_slides(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取幻灯片列表"""
    try:
        service = PPTService(db)
        result = await service.get_slides(project_id, current_user_id)
        return {"code": 200, "message": "获取成功", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"获取幻灯片失败: {e}")
        raise HTTPException(status_code=500, detail="获取失败")


@router.post("/{project_id}/export")
async def export_pptx_file(
    project_id: int,
    request: PPTExportRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """导出PPTX文件"""
    try:
        service = PPTService(db)
        result = await service.export_pptx(project_id, current_user_id, request.format)
        return {"code": 200, "message": "导出成功", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"导出失败: {e}")
        raise HTTPException(status_code=500, detail="导出失败")
