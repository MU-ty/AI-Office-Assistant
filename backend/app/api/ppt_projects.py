"""
PPT生成模块 API
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.base_services import PPTService
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_ppt_project(
    project_name: str,
    source_content: str,
    db: AsyncSession = Depends(get_db)
):
    """创建PPT项目"""
    service = PPTService(db)
    return await service.create_project({
        "project_name": project_name,
        "source_content": source_content
    })


@router.get("/")
async def list_ppt_projects(
    skip: int = 0,
    limit: int = 10,
    status: str = None,
    db: AsyncSession = Depends(get_db)
):
    """获取PPT项目列表"""
    service = PPTService(db)
    return await service.list_projects(skip, limit, status)


@router.get("/{project_id}")
async def get_ppt_project(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取项目详情"""
    service = PPTService(db)
    return await service.get_project(project_id)


@router.put("/{project_id}")
async def update_ppt_project(
    project_id: str,
    project_name: str = None,
    db: AsyncSession = Depends(get_db)
):
    """更新项目"""
    service = PPTService(db)
    return await service.update_project(project_id, {"project_name": project_name})


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ppt_project(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """删除项目"""
    service = PPTService(db)
    await service.delete_project(project_id)


@router.post("/{project_id}/generate")
async def generate_ppt_slides(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """生成幻灯片"""
    service = PPTService(db)
    return await service.generate_slides(project_id)


@router.get("/{project_id}/slides")
async def get_ppt_slides(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取幻灯片列表"""
    service = PPTService(db)
    return await service.get_slides(project_id)


@router.post("/{project_id}/export")
async def export_pptx_file(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """导出PPTX文件"""
    service = PPTService(db)
    return await service.export_pptx(project_id)
