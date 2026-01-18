"""健康检查路由"""

from fastapi import APIRouter, Response
from app.core.config import get_settings

router = APIRouter(prefix="/api/v1/health", tags=["health"])
settings = get_settings()


@router.get("")
async def health_check():
    """系统健康检查"""
    return {
        "status": "ok",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@router.get("/ready")
async def readiness_check():
    """就绪检查"""
    return {
        "ready": True,
        "message": "应用已就绪"
    }
