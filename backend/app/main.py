"""
办公助手Agent - FastAPI 主应用入口
版本: v1.0
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.core.database import init_db, get_db
from app.utils.logger import get_logger
from app.api import (
    health,
    users,
    meetings,
    documents,
    polish_tasks,
    translation_tasks,
    ppt_projects,
    weekly_reports,
    stream,  # 新增: 流式处理服务
    asr,  # 新增: 语音识别服务
    weknora,
    knowledge, # 新增
    search,     # 新增
    chat       # 新增
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理 - 启动和关闭钩子"""
    # 启动事件
    logger.info("🚀 应用启动中...")
    try:
        await init_db()
        logger.info("✅ 数据库初始化完成")
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        raise
    
    # 自动初始化 WeKnora 模型配置（非关键，初始化失败不阻止应用启动）
    try:
        from init_weknora import initialize_weknora
        await initialize_weknora()
        logger.info("✅ WeKnora 模型配置初始化完成")
    except Exception as e:
        logger.warning(f"⚠️  WeKnora 模型配置初始化失败: {e}")
        # 不 raise，让应用继续启动
    
    # 自动初始化 ES 索引
    try:
        from app.services.search_service import search_service
        import asyncio
        # 等待 ES 启动 (简单的重试机制)
        for i in range(5):
            try:
                await search_service.init_index()
                logger.info("✅ ES 索引初始化完成")
                break
            except Exception as e:
                if i == 4:
                    raise e
                logger.warning(f"⚠️ ES 连接失败，正在重试 ({i+1}/5): {e}")
                await asyncio.sleep(5)
    except Exception as e:
        logger.error(f"❌ ES 索引初始化失败: {e}")

    yield
    
    # 关闭事件
    logger.info("🛑 应用关闭中...")


# 创建FastAPI应用
app = FastAPI(
    title="办公助手Agent API",
    description="AI驱动的办公生产力助手系统",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)


# ============================================================
# 中间件配置
# ============================================================

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 受信主机中间件
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)


# ============================================================
# 异常处理
# ============================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """数据验证异常处理"""
    return JSONResponse(
        status_code=422,
        content={
            "code": "VALIDATION_ERROR",
            "message": "请求数据验证失败",
            "errors": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理"""
    logger.error(f"未捕获异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "code": "INTERNAL_ERROR",
            "message": "服务器内部错误"
        }
    )


# ============================================================
# 请求日志中间件
# ============================================================

@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """记录HTTP请求和响应"""
    import time
    
    start_time = time.time()
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        logger.info(
            f"{request.method} {request.url.path}",
            extra={
                "status_code": response.status_code,
                "process_time": process_time,
                "client": request.client.host if request.client else "unknown"
            }
        )
        
        response.headers["X-Process-Time"] = str(process_time)
        return response
    except Exception as e:
        logger.error(f"请求处理异常: {e}")
        raise


# ============================================================
# 路由注册
# ============================================================

# 静态文件服务 - 用于下载生成的文档
if not os.path.exists(settings.UPLOAD_DIR):
    os.makedirs(settings.UPLOAD_DIR)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# 健康检查
app.include_router(health.router, tags=["Health"])

# 流式处理服务 (新增)
app.include_router(
    stream.router,
    prefix="/api/v1/stream",
    tags=["Stream"]
)

# 语音识别服务 (新增)
app.include_router(
    asr.router,
    prefix="/api/v1/asr",
    tags=["ASR"]
)

# 用户认证模块
app.include_router(
    users.router,
    prefix="/api/v1/users",
    tags=["Users"]
)

# 会议纪要模块
app.include_router(
    meetings.router,
    prefix="/api/v1/meetings",
    tags=["Meetings"]
)

# 文献摘要模块
app.include_router(
    documents.router,
    prefix="/api/v1/documents",
    tags=["Documents"]
)

# 学术润色模块
app.include_router(
    polish_tasks.router,
    prefix="/api/v1/polish",
    tags=["Polish"]
)

# 多语言翻译模块
app.include_router(
    translation_tasks.router,
    prefix="/api/v1/translations",
    tags=["Translation"]
)

# PPT生成模块
app.include_router(
    ppt_projects.router,
    prefix="/api/v1/ppt",
    tags=["PPT"]
)

# 周报生成模块
app.include_router(
    weekly_reports.router,
    prefix="/api/v1/reports",
    tags=["Reports"]
)

# WeKnora 知识库接入
app.include_router(
    weknora.router,
    prefix="/api/v1/weknora",
    tags=["WeKnora"]
)

# 知识库管理
app.include_router(
    knowledge.router,
    prefix="/api/v1/knowledge",
    tags=["Knowledge"]
)

# 搜索服务
app.include_router(
    search.router,
    prefix="/api/v1/search",
    tags=["Search"]
)

# 智能问答服务
app.include_router(
    chat.router,
    prefix="/api/v1/chat",
    tags=["Chat"]
)


# ============================================================
# 根路由
# ============================================================

@app.get("/", tags=["Root"])
async def root():
    """API根路由"""
    return {
        "name": "办公助手Agent API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/api/docs",
        "openapi": "/api/openapi.json",
        "endpoints": {
            "流式处理": "/api/v1/stream",
            "学术润色": "/api/v1/polish",
            "会议记录": "/api/v1/meetings",
            "文档生成": "/api/v1/documents",
            "用户管理": "/api/v1/users",
            "翻译": "/api/v1/translations",
            "PPT生成": "/api/v1/ppt",
            "周报生成": "/api/v1/reports"
        }
    }


# ============================================================
# 应用启动命令
# ============================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
