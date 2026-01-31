"""
学术润色模块 API
根据流程图中的学术规范化子模块实现
包含：术语替换、时态调整、风格检查、论文规范检查
"""

from typing import Optional
from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.base_services import PolishService
from app.schemas.polish import (
    PolishTaskCreate,
    PolishTaskUpdate,
    PolishTaskResponse,
    PolishTaskListResponse,
    PolishIssueResponse,
    AcceptSuggestionRequest,
    RejectSuggestionRequest,
    ExportResultRequest,
    PolishStatistics,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/polish", tags=["学术润色"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_polish_task(
    request: PolishTaskCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建学术润色任务
    
    流程：
    1. 接收文本和配置
    2. 执行学术规范化分析（术语、时态、风格、论文规范）
    3. 返回检测到的问题列表
    
    Args:
        request: 润色任务请求
        db: 数据库会话
        
    Returns:
        任务详情及问题列表
    """
    try:
        logger.info("创建学术润色任务")
        service = PolishService(db)
        task_data = {
            "original_text": request.original_text,
            "polish_level": request.polish_level,
            "auto_fix_enabled": request.auto_fix_enabled,
            "document_id": request.document_id,
        }
        result = await service.create_task(task_data)
        return {
            "code": 200,
            "message": "任务创建成功",
            "data": result
        }
    except ValueError as e:
        logger.warning(f"参数验证错误: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"创建任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("", response_model=dict)
async def list_polish_tasks(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(10, ge=1, le=100, description="返回数量"),
    status: Optional[str] = Query(None, description="筛选状态: pending/processing/completed/failed"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取润色任务列表
    
    Args:
        skip: 跳过数量
        limit: 返回数量
        status: 任务状态筛选
        db: 数据库会话
        
    Returns:
        任务列表
    """
    try:
        logger.info(f"获取润色任务列表，skip={skip}, limit={limit}, status={status}")
        service = PolishService(db)
        result = await service.list_tasks(skip, limit, status)
        return {
            "code": 200,
            "message": "获取成功",
            "data": result
        }
    except Exception as e:
        logger.error(f"获取任务列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/{task_id}", response_model=dict)
async def get_polish_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取任务详情
    
    Args:
        task_id: 任务ID
        db: 数据库会话
        
    Returns:
        任务详情及所有问题
    """
    try:
        logger.info(f"获取润色任务详情，task_id={task_id}")
        service = PolishService(db)
        task = await service.get_task(task_id)
        
        # 获取问题列表
        issues_result = await service.get_issues(task_id)
        task["issues"] = issues_result["issues"]
        
        return {
            "code": 200,
            "message": "获取成功",
            "data": task
        }
    except ValueError as e:
        logger.warning(f"任务不存在: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"获取任务详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.put("/{task_id}", response_model=dict)
async def update_polish_task(
    task_id: int,
    request: PolishTaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    更新任务
    
    支持更新原始文本、润色级别等
    
    Args:
        task_id: 任务ID
        request: 更新请求
        db: 数据库会话
        
    Returns:
        更新后的任务详情
    """
    try:
        logger.info(f"更新润色任务，task_id={task_id}")
        service = PolishService(db)
        task_data = request.dict(exclude_unset=True)
        result = await service.update_task(task_id, task_data)
        return {
            "code": 200,
            "message": "更新成功",
            "data": result
        }
    except ValueError as e:
        logger.warning(f"任务不存在: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"更新任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_polish_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    删除任务
    
    Args:
        task_id: 任务ID
        db: 数据库会话
    """
    try:
        logger.info(f"删除润色任务，task_id={task_id}")
        service = PolishService(db)
        await service.delete_task(task_id)
    except ValueError as e:
        logger.warning(f"任务不存在: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"删除任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/{task_id}/issues", response_model=dict)
async def get_polish_issues(
    task_id: int,
    filter_type: Optional[str] = Query(None, description="筛选问题类型"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取任务的所有问题
    
    可按问题类型筛选：
    - terminology: 术语问题
    - tense: 时态问题
    - style: 风格问题
    - thesis: 论文规范问题
    
    Args:
        task_id: 任务ID
        filter_type: 问题类型筛选
        db: 数据库会话
        
    Returns:
        问题列表
    """
    try:
        logger.info(f"获取润色问题列表，task_id={task_id}, filter_type={filter_type}")
        service = PolishService(db)
        result = await service.get_issues(task_id, filter_type)
        return {
            "code": 200,
            "message": "获取成功",
            "data": result
        }
    except ValueError as e:
        logger.warning(f"任务不存在: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"获取问题列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.post("/{task_id}/issues/{issue_id}/accept", response_model=dict)
async def accept_polish_suggestion(
    task_id: int,
    issue_id: int,
    request: Optional[AcceptSuggestionRequest] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    接受润色建议
    
    接受后，该问题将被标记为已接受
    
    Args:
        task_id: 任务ID
        issue_id: 问题ID
        request: 请求体（可选反馈）
        db: 数据库会话
        
    Returns:
        更新后的问题详情
    """
    try:
        logger.info(f"接受建议，task_id={task_id}, issue_id={issue_id}")
        service = PolishService(db)
        feedback = request.feedback if request else None
        result = await service.accept_suggestion(task_id, issue_id, feedback)
        return {
            "code": 200,
            "message": "建议已接受",
            "data": result
        }
    except ValueError as e:
        logger.warning(f"问题不存在: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"接受建议失败: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.post("/{task_id}/issues/{issue_id}/reject", response_model=dict)
async def reject_polish_suggestion(
    task_id: int,
    issue_id: int,
    request: Optional[RejectSuggestionRequest] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    拒绝润色建议
    
    拒绝后，该问题将被标记为已拒绝
    
    Args:
        task_id: 任务ID
        issue_id: 问题ID
        request: 拒绝原因
        db: 数据库会话
        
    Returns:
        更新后的问题详情
    """
    try:
        logger.info(f"拒绝建议，task_id={task_id}, issue_id={issue_id}")
        service = PolishService(db)
        reason = request.reason if request else None
        result = await service.reject_suggestion(task_id, issue_id, reason)
        return {
            "code": 200,
            "message": "建议已拒绝",
            "data": result
        }
    except ValueError as e:
        logger.warning(f"问题不存在: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"拒绝建议失败: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.post("/{task_id}/export", response_model=dict)
async def export_polish_result(
    task_id: int,
    request: ExportResultRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    导出润色结果
    
    支持多种导出格式：
    - json: JSON格式
    - txt: 纯文本格式
    
    Args:
        task_id: 任务ID
        request: 导出请求
        db: 数据库会话
        
    Returns:
        导出的结果
    """
    try:
        logger.info(f"导出润色结果，task_id={task_id}, format={request.format}")
        service = PolishService(db)
        result = await service.export_result(task_id, request.format)
        return {
            "code": 200,
            "message": "导出成功",
            "data": result
        }
    except ValueError as e:
        logger.warning(f"导出失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"导出结果失败: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("", response_model=dict, name="get_statistics")
async def get_polish_statistics(
    db: AsyncSession = Depends(get_db)
):
    """
    获取润色统计信息
    
    Returns:
        统计信息（总任务数、完成数、问题分类统计等）
    """
    try:
        logger.info("获取润色统计信息")
        service = PolishService(db)
        
        # 获取统计数据
        all_tasks = await service.list_tasks(0, 10000)  # 获取所有任务
        tasks = all_tasks.get("items", [])
        
        total_issues = sum(t.get("total_issues", 0) for t in tasks)
        total_fixed = sum(t.get("fixed_issues", 0) for t in tasks)
        completed = sum(1 for t in tasks if t.get("status") == "completed")
        
        stats = {
            "total_tasks": len(tasks),
            "completed_tasks": completed,
            "pending_tasks": len(tasks) - completed,
            "average_accuracy": round(sum(t.get("accuracy", 0) for t in tasks) / len(tasks), 2) if tasks else 0.0,
            "total_issues_found": total_issues,
            "total_issues_fixed": total_fixed,
        }
        
        return {
            "code": 200,
            "message": "获取成功",
            "data": stats
        }
    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")



@router.get("/{task_id}/export")
async def export_polish_result(
    task_id: str,
    format: str = "markdown",
    db: AsyncSession = Depends(get_db)
):
    """导出润色结果"""
    service = PolishService(db)
    return await service.export_result(task_id, format)
