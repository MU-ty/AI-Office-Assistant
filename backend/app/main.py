"""FastAPI应用工厂"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.api import health_router, user_router, tasks_router
from app.db import init_db, close_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print(f"启动应用: {settings.APP_NAME} v{settings.APP_VERSION}")
    await init_db()
    
    yield
    
    # 关闭时
    await close_db()
    print("应用已关闭")


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    
    app = FastAPI(
        title=settings.APP_NAME,
        description="学术与职场场景智能支持系统",
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan
    )
    
    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册路由
    app.include_router(health_router)
    app.include_router(user_router)
    app.include_router(tasks_router, prefix="/api/v1/tasks", tags=["tasks"])
    
    # 根路由
    @app.get("/")
    async def root():
        return {
            "message": "欢迎使用办公助手Agent",
            "api_docs": "/docs",
            "health": "/api/v1/health"
        }
    
    return app
