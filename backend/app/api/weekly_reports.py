"""
周报生成模块 API
"""

from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user_id
from app.services.report_service import WeeklyReportService
from app.schemas.report import (
    WorkLogCreate, WorkLogUpdate, WorkLogResponse,
    WeeklyReportCreate, WeeklyReportUpdate, WeeklyReportReview,
    WeeklyReportResponse, WeeklyReportDetailResponse, WeeklyReportListResponse
)
from app.utils.logger import get_logger
from app.utils.exceptions import ValidationError

logger = get_logger(__name__)
router = APIRouter()


# ============================================================
# 工作日志相关接口
# ============================================================

@router.post("/logs", status_code=status.HTTP_201_CREATED, response_model=WorkLogResponse)
async def create_work_log(
    log_data: WorkLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    创建工作日志
    
    - **work_type**: 工作类型 (必需)
    - **task_description**: 任务描述 (必需)
    - **hours_spent**: 花费的小时数 (必需, 0-24)
    - **log_date**: 日志日期 (可选，默认为当前时间)
    """
    try:
        service = WeeklyReportService(db)
        return await service.create_log(log_data, user_id=current_user_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"创建工作日志异常: {e}")
        raise HTTPException(status_code=500, detail="创建工作日志失败")


@router.get("/logs", response_model=dict)
async def list_work_logs(
    date_from: str = Query(None, description="起始日期 (YYYY-MM-DD)"),
    date_to: str = Query(None, description="结束日期 (YYYY-MM-DD)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    获取工作日志列表
    
    - **date_from**: 起始日期过滤 (可选)
    - **date_to**: 结束日期过滤 (可选)
    - **skip**: 分页偏移 (默认0)
    - **limit**: 每页数量 (默认100, 最大1000)
    """
    try:
        from datetime import datetime
        
        date_from_obj = None
        date_to_obj = None
        
        if date_from:
            try:
                date_from_obj = datetime.fromisoformat(date_from)
            except ValueError:
                raise HTTPException(status_code=400, detail="date_from 格式错误，请使用 YYYY-MM-DD")
        
        if date_to:
            try:
                date_to_obj = datetime.fromisoformat(date_to)
            except ValueError:
                raise HTTPException(status_code=400, detail="date_to 格式错误，请使用 YYYY-MM-DD")
        
        service = WeeklyReportService(db)
        return await service.list_logs(
            user_id=current_user_id,
            date_from=date_from_obj,
            date_to=date_to_obj,
            skip=skip,
            limit=limit
        )
    
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取日志列表异常: {e}")
        raise HTTPException(status_code=500, detail="获取日志列表失败")


@router.get("/logs/{log_id}", response_model=WorkLogResponse)
async def get_work_log(
    log_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取工作日志详情"""
    try:
        service = WeeklyReportService(db)
        return await service.get_log(log_id, user_id=current_user_id)
    except ValidationError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"获取日志详情异常: {e}")
        raise HTTPException(status_code=500, detail="获取日志详情失败")


@router.put("/logs/{log_id}", response_model=WorkLogResponse)
async def update_work_log(
    log_id: int,
    log_data: WorkLogUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """更新工作日志"""
    try:
        service = WeeklyReportService(db)
        return await service.update_log(log_id, log_data, user_id=current_user_id)
    except ValidationError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"更新日志异常: {e}")
        raise HTTPException(status_code=500, detail="更新日志失败")


@router.delete("/logs/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_work_log(
    log_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """删除工作日志"""
    try:
        service = WeeklyReportService(db)
        await service.delete_log(log_id, user_id=current_user_id)
    except ValidationError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"删除日志异常: {e}")
        raise HTTPException(status_code=500, detail="删除日志失败")


# ============================================================
# 周报相关接口
# ============================================================

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=WeeklyReportDetailResponse)
async def create_weekly_report(
    report_data: WeeklyReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    生成周报
    
    会自动从该周的工作日志生成周报摘要和统计工作小时数
    
    - **title**: 周报标题 (可选)
    - **week_start_date**: 周开始日期 (必需, ISO格式)
    - **week_end_date**: 周结束日期 (必需, ISO格式)
    """
    try:
        service = WeeklyReportService(db)
        return await service.create_report(report_data, user_id=current_user_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"生成周报异常: {e}")
        raise HTTPException(status_code=500, detail="生成周报失败")


@router.get("/", response_model=WeeklyReportListResponse)
async def list_weekly_reports(
    status: str = Query(None, description="周报状态过滤 (draft/submitted/approved/rejected)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    获取周报列表
    
    - **status**: 周报状态过滤 (可选)
    - **skip**: 分页偏移 (默认0)
    - **limit**: 每页数量 (默认10, 最大100)
    """
    try:
        service = WeeklyReportService(db)
        result = await service.list_reports(user_id=current_user_id, status=status, skip=skip, limit=limit)
        return result
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"获取周报列表异常: {e}")
        raise HTTPException(status_code=500, detail="获取周报列表失败")


@router.get("/{report_id}", response_model=WeeklyReportDetailResponse)
async def get_weekly_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取周报详情"""
    try:
        service = WeeklyReportService(db)
        return await service.get_report(report_id, user_id=current_user_id)
    except ValidationError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"获取周报详情异常: {e}")
        raise HTTPException(status_code=500, detail="获取周报详情失败")


@router.put("/{report_id}", response_model=WeeklyReportDetailResponse)
async def update_weekly_report(
    report_id: int,
    report_data: WeeklyReportUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    更新周报
    
    只能编辑草稿状态的周报
    """
    try:
        service = WeeklyReportService(db)
        return await service.update_report(report_id, report_data, user_id=current_user_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"更新周报异常: {e}")
        raise HTTPException(status_code=500, detail="更新周报失败")


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_weekly_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    删除周报
    
    只能删除草稿状态的周报
    """
    try:
        service = WeeklyReportService(db)
        await service.delete_report(report_id, user_id=current_user_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"删除周报异常: {e}")
        raise HTTPException(status_code=500, detail="删除周报失败")


@router.post("/{report_id}/submit", response_model=WeeklyReportDetailResponse)
async def submit_weekly_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    提交周报审核
    
    将周报状态从草稿改为已提交
    """
    try:
        service = WeeklyReportService(db)
        return await service.submit_report(report_id, user_id=current_user_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"提交周报异常: {e}")
        raise HTTPException(status_code=500, detail="提交周报失败")


@router.post("/{report_id}/review", response_model=WeeklyReportDetailResponse)
async def review_weekly_report(
    report_id: int,
    review_data: WeeklyReportReview,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    审核周报
    
    - **status**: 审核状态 (approved/rejected) 必需
    - **review_feedback**: 审核反馈 (可选)
    """
    try:
        service = WeeklyReportService(db)
        return await service.review_report(
            report_id,
            review_data,
            reviewer_id=current_user_id,
            user_id=current_user_id
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"审核周报异常: {e}")
        raise HTTPException(status_code=500, detail="审核周报失败")


@router.post("/{report_id}/export", response_model=dict)
async def export_weekly_report(
    report_id: int,
    format: str = Query("markdown", description="导出格式 (markdown/html/pdf/docx)"),
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    导出周报
    
    - **format**: 导出格式，支持 markdown/html/pdf/docx (默认 markdown)
    """
    try:
        if format not in ["markdown", "html", "pdf", "docx"]:
            raise HTTPException(status_code=400, detail="不支持的导出格式，只支持 markdown/html/pdf/docx")
        
        service = WeeklyReportService(db)
        return await service.export_report(report_id, format, user_id=current_user_id)
    except ValidationError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"导出周报异常: {e}")
        raise HTTPException(status_code=500, detail="导出周报失败")
