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
    if settings.DEBUG:
        engine_kwargs.update({
            "poolclass": NullPool,
        })
    else:
        engine_kwargs.update({
            "pool_size": settings.DB_POOL_SIZE,
            "max_overflow": settings.DB_MAX_OVERFLOW,
            "pool_pre_ping": True,
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
            # 无论 SQLite 还是 PostgreSQL，都确保关键列存在
            await _ensure_db_schema(conn)
            logger.info("✅ 数据库表创建完成")
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        raise


async def _ensure_db_schema(conn):
    """确保数据库表结构符合预期 (支持 SQLite 和 PostgreSQL)"""
    try:
        is_sqlite = settings.DB_TYPE == "sqlite"
        migrations = {
            "meetings": [
                ("user_id", "INTEGER"),
                ("description", "TEXT"),
                ("date", "VARCHAR(50)"),
                ("status", "VARCHAR(20)"),
                ("transcription", "TEXT"),
                ("created_at", "DATETIME" if is_sqlite else "TIMESTAMP"),
                ("updated_at", "DATETIME" if is_sqlite else "TIMESTAMP"),
            ],
            "meeting_minutes": [
                ("user_id", "INTEGER"),
                ("file_path", "VARCHAR(500)"),
                ("created_at", "DATETIME" if is_sqlite else "TIMESTAMP"),
            ],
            "documents": [
                ("user_id", "INTEGER" if is_sqlite else "INTEGER"),
                ("source_type", "VARCHAR(50)"),
                ("source_url", "VARCHAR(500)"),
                ("file_path", "VARCHAR(500)"),
                ("meta_info", "TEXT"),
                ("weknora_knowledge_id", "VARCHAR(100)"),
                ("weknora_kb_id", "VARCHAR(100)"),
                ("status", "VARCHAR(20)"),
                ("error_message", "TEXT"),
                ("processing_progress", "INTEGER"),
            ],
            "ppt_projects": [
                ("user_id", "INTEGER"),
                ("outline_json", "TEXT"),
                ("slides_json", "TEXT"),
                ("file_path", "VARCHAR(500)"),
                ("theme", "VARCHAR(50)"),
                ("theme_palette", "TEXT"),
            ],
            "translation_tasks": [
                ("user_id", "INTEGER"),
                ("domain", "VARCHAR(50)"),
                ("quality_score", "FLOAT"),
                ("rating", "INTEGER"),
                ("feedback", "TEXT"),
            ],
            "weekly_reports": [
                ("user_id", "INTEGER"),
                ("title", "VARCHAR(255)"),
                ("week", "VARCHAR(50)"),
                ("summary", "TEXT"),
                ("content", "TEXT"),
                ("status", "VARCHAR(50)"),
            ],
            "polish_tasks": [
                ("user_id", "INTEGER"),
                ("document_id", "INTEGER"),
                ("polished_text", "TEXT"),
                ("status", "VARCHAR(20)"),
            ],
        }

        for table_name, columns_to_add in migrations.items():
            if is_sqlite:
                result = await conn.execute(text(f"PRAGMA table_info({table_name})"))
                existing_columns = {row[1] for row in result.fetchall()}
            else:
                # PostgreSQL 检查列是否存在
                result = await conn.execute(text(
                    f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'"
                ))
                existing_columns = {row[0] for row in result.fetchall()}

            for column_name, column_type in columns_to_add:
                if column_name not in existing_columns:
                    try:
                        await conn.execute(text(
                            f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
                        ))
                        logger.info(f"数据库迁移: {table_name} 补充列 {column_name}")
                    except Exception as col_e:
                        logger.warning(f"添加列 {column_name} 到 {table_name} 失败 (可能已存在): {col_e}")

    except Exception as e:
        logger.error(f"数据库迁移失败: {e}")
        # 不中断启动，除非是严重错误
        if settings.DB_TYPE == "sqlite":
            raise


async def close_db():
    """关闭数据库连接"""
    await engine.dispose()
