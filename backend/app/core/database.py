"""
数据库连接和会话管理
"""

import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession, create_async_engine, async_sessionmaker
)
from sqlalchemy.pool import NullPool, StaticPool
from sqlalchemy.orm import declarative_base
from sqlalchemy import text

from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# 创建基类
Base = declarative_base()

# 确保 SQLite 数据库目录存在
if settings.DB_TYPE == "sqlite":
    db_dir = os.path.dirname(settings.SQLITE_DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        logger.info(f"创建数据库目录: {db_dir}")

# 创建异步引擎（支持 SQLite 和 PostgreSQL）
engine_kwargs = {
    "echo": settings.SQLALCHEMY_ECHO,
}

if settings.DB_TYPE == "sqlite":
    # SQLite 专用配置
    engine_kwargs.update({
        "poolclass": StaticPool,
        "connect_args": {"check_same_thread": False},
    })
    logger.info(f"使用 SQLite 数据库: {settings.SQLITE_DB_PATH}")
else:
    # PostgreSQL 专用配置
    engine_kwargs.update({
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_pre_ping": True,
        "poolclass": NullPool if settings.DEBUG else None,
    })
    logger.info(f"使用 PostgreSQL 数据库: {settings.DATABASE_URL}")

engine = create_async_engine(
    settings.DATABASE_URL,
    **engine_kwargs
)

# 创建异步会话工厂
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话依赖注入"""
    async with async_session() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"数据库会话错误: {e}")
            raise
        finally:
            await session.close()


async def init_db():
    """初始化数据库 - 创建所有表"""
    try:
        async with engine.begin() as conn:
            # 注意：这里需要先导入所有模型
            from app.models import user, meeting, document, polish, translation, ppt, report
            
            await conn.run_sync(Base.metadata.create_all)
            if settings.DB_TYPE == "sqlite":
                await _ensure_sqlite_schema(conn)
            logger.info("✅ 数据库表创建完成")
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        raise


async def _ensure_sqlite_schema(conn):
    """修复 SQLite 旧表缺失列的问题"""
    try:
        migrations = {
            "work_logs": [
                ("user_id", "INTEGER"),
            ],
            "weekly_reports": [
                ("user_id", "INTEGER"),
                ("title", "VARCHAR(255)"),
                ("week_start_date", "DATETIME"),
                ("week_end_date", "DATETIME"),
                ("week", "VARCHAR(50)"),
                ("summary", "TEXT"),
                ("content", "TEXT"),
                ("status", "VARCHAR(50)"),
                ("total_hours", "FLOAT"),
                ("review_feedback", "TEXT"),
                ("reviewer_id", "INTEGER"),
                ("reviewed_at", "DATETIME"),
                ("created_at", "DATETIME"),
                ("updated_at", "DATETIME"),
            ],
            "polish_tasks": [
                ("user_id", "INTEGER"),
                ("document_id", "INTEGER"),
                ("polished_text", "TEXT"),
                ("status", "VARCHAR(20)"),
                ("polish_level", "VARCHAR(20)"),
                ("terminology_issues", "TEXT"),
                ("tense_issues", "TEXT"),
                ("style_issues", "TEXT"),
                ("thesis_issues", "TEXT"),
                ("total_issues", "INTEGER"),
                ("fixed_issues", "INTEGER"),
                ("accuracy", "FLOAT"),
                ("auto_fix_enabled", "VARCHAR(5)"),
                ("created_at", "DATETIME"),
                ("updated_at", "DATETIME"),
                ("completed_at", "DATETIME"),
            ],
        }

        for table_name, columns_to_add in migrations.items():
            result = await conn.execute(text(f"PRAGMA table_info({table_name})"))
            existing_columns = {row[1] for row in result.fetchall()}
            for column_name, column_type in columns_to_add:
                if column_name not in existing_columns:
                    await conn.execute(text(
                        f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
                    ))
                    logger.info(f"SQLite 迁移: {table_name} 补充列 {column_name}")
    except Exception as e:
        logger.error(f"SQLite 迁移失败: {e}")
        raise


async def close_db():
    """关闭数据库连接"""
    await engine.dispose()
