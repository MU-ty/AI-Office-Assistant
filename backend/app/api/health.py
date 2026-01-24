"""
健康检查和系统状态端点
"""

from fastapi import APIRouter
from datetime import datetime

from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.APP_VERSION,
        "service": settings.APP_NAME
    }


@router.get("/health/detailed")
async def detailed_health_check():
    """详细健康检查"""
    from app.core.database import engine
    
    db_status = "unknown"
    redis_status = "unknown"
    
    # 检查数据库
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # 检查Redis (可选)
    try:
        import redis
        r = redis.Redis.from_url(settings.REDIS_URL)
        r.ping()
        redis_status = "healthy"
    except Exception as e:
        redis_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": db_status,
            "redis": redis_status,
        },
        "version": settings.APP_VERSION
    }


@router.get("/info")
async def system_info():
    """系统信息"""
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG,
        "environment": {
            "host": settings.HOST,
            "port": settings.PORT,
        }
    }
