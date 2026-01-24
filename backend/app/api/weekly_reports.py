"""
周报生成模块 API
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.base_services import ReportService
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/logs", status_code=status.HTTP_201_CREATED)
async def create_work_log(
    work_type: str,
    task_description: str,
    hours_spent: float,
    db: AsyncSession = Depends(get_db)
):
    """创建工作日志"""
    service = ReportService(db)
    return await service.create_log({
        "work_type": work_type,
        "task_description": task_description,
        "hours_spent": hours_spent
    })


@router.get("/logs")
async def list_work_logs(
    date_from: str = None,
    date_to: str = None,
    db: AsyncSession = Depends(get_db)
):
    """获取工作日志列表"""
    service = ReportService(db)
    return await service.list_logs(None, date_from, date_to)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_weekly_report(
    week_start_date: str,
    week_end_date: str,
    db: AsyncSession = Depends(get_db)
):
    """生成周报"""
    service = ReportService(db)
    return await service.create_report({
        "week_start_date": week_start_date,
        "week_end_date": week_end_date
    })


@router.get("/")
async def list_weekly_reports(
    skip: int = 0,
    limit: int = 10,
    status: str = None,
    db: AsyncSession = Depends(get_db)
):
    """获取周报列表"""
    service = ReportService(db)
    return await service.list_reports(skip, limit, status)


@router.get("/{report_id}")
async def get_weekly_report(
    report_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取周报详情"""
    service = ReportService(db)
    return await service.get_report(report_id)


@router.put("/{report_id}")
async def update_weekly_report(
    report_id: str,
    title: str = None,
    db: AsyncSession = Depends(get_db)
):
    """更新周报"""
    service = ReportService(db)
    return await service.update_report(report_id, {"title": title})


@router.post("/{report_id}/submit")
async def submit_weekly_report(
    report_id: str,
    db: AsyncSession = Depends(get_db)
):
    """提交周报审核"""
    service = ReportService(db)
    return await service.submit_report(report_id)


@router.post("/{report_id}/review")
async def review_weekly_report(
    report_id: str,
    status: str,
    feedback: str = None,
    db: AsyncSession = Depends(get_db)
):
    """审核周报"""
    service = ReportService(db)
    return await service.review_report(report_id, {
        "status": status,
        "feedback": feedback
    })


@router.post("/{report_id}/export")
async def export_weekly_report(
    report_id: str,
    format: str = "markdown",
    db: AsyncSession = Depends(get_db)
):
    """导出周报"""
    service = ReportService(db)
    return await service.export_report(report_id, format)
