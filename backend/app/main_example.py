"""
FastAPI 主应用配置示例
展示如何集成流式处理服务
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZIPMiddleware
from contextlib import asynccontextmanager
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# 导入路由和服务
# ============================================================================

# 导入流式API路由
from app.api import stream

# 导入其他现有的API路由 (学术润色、会议记录等)
from app.api import polish_tasks, meetings, documents, users

# 导入服务
from app.services.stream_service import StreamService
from app.core.database import engine
from app.core.config import settings

# ============================================================================
# 生命周期事件处理
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    """
    # 启动事件
    logger.info("🚀 应用启动中...")
    
    # 初始化数据库连接
    logger.info("📊 初始化数据库...")
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    
    logger.info("✅ 应用启动完成")
    
    yield  # 应用运行中...
    
    # 关闭事件
    logger.info("🛑 应用关闭中...")
    await engine.dispose()
    logger.info("✅ 应用已关闭")


# ============================================================================
# 创建FastAPI应用
# ============================================================================

app = FastAPI(
    title="AI Office Assistant API",
    description="学术润色、会议记录、文档生成等办公助手API",
    version="1.0.0",
    lifespan=lifespan
)

# ============================================================================
# 中间件配置
# ============================================================================

# CORS中间件 - 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZIP压缩中间件 - 压缩响应体
app.add_middleware(GZIPMiddleware, minimum_size=1000)

# ============================================================================
# 健康检查端点
# ============================================================================

@app.get("/health", tags=["系统"])
async def health_check():
    """
    健康检查端点
    """
    return {
        "status": "ok",
        "service": "AI Office Assistant",
        "version": "1.0.0"
    }


@app.get("/", tags=["系统"])
async def root():
    """
    根端点 - API文档
    """
    return {
        "message": "欢迎使用AI Office Assistant API",
        "docs": "http://localhost:8000/docs",
        "endpoints": {
            "流式处理": "/api/v1/stream",
            "学术润色": "/api/v1/polish",
            "会议记录": "/api/v1/meetings",
            "文档生成": "/api/v1/documents",
            "用户管理": "/api/v1/users"
        }
    }


# ============================================================================
# 注册API路由
# ============================================================================

# 流式处理路由 (新增)
logger.info("📡 注册流式处理API路由...")
app.include_router(stream.router)

# 学术润色路由
logger.info("✏️  注册学术润色API路由...")
app.include_router(polish_tasks.router)

# 会议记录路由
logger.info("🎤 注册会议记录API路由...")
app.include_router(meetings.router)

# 文档生成路由
logger.info("📄 注册文档生成API路由...")
app.include_router(documents.router)

# 用户管理路由
logger.info("👤 注册用户管理API路由...")
app.include_router(users.router)

# ============================================================================
# 全局异常处理器
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    全局异常处理器
    """
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return {
        "error": "Internal Server Error",
        "detail": str(exc),
        "status_code": 500
    }


# ============================================================================
# 后台任务示例
# ============================================================================

from fastapi import BackgroundTasks

@app.post("/api/v1/tasks/async", tags=["任务"])
async def create_async_task(background_tasks: BackgroundTasks, task_name: str):
    """
    创建异步后台任务的示例
    """
    async def process_task(name: str):
        logger.info(f"后台任务开始: {name}")
        # 模拟耗时操作
        import asyncio
        await asyncio.sleep(2)
        logger.info(f"后台任务完成: {name}")
    
    background_tasks.add_task(process_task, task_name)
    return {"status": "task_created", "task_name": task_name}


# ============================================================================
# 启动配置
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # 启动开发服务器
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
    
    # 生产环境启动方式:
    # gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
