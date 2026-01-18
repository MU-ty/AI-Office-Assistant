"""数据库初始化脚本"""

import asyncio
import logging
from app.db import init_db, SessionLocal
from app.models import User, Task, Document
from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


async def main():
    """初始化数据库"""
    try:
        logger.info("开始初始化数据库...")
        
        # 创建所有表
        await init_db()
        logger.info("数据库表创建成功")
        
        # 创建示例数据
        db = SessionLocal()
        try:
            # 检查是否已有用户
            existing_user = db.query(User).first()
            if not existing_user:
                logger.info("创建示例用户...")
                sample_user = User(
                    username="admin",
                    email="admin@example.com",
                    hashed_password="$2b$12$example",  # 这只是示例，实际应该使用bcrypt
                    full_name="管理员",
                    is_active=True,
                    is_superuser=True
                )
                db.add(sample_user)
                db.commit()
                logger.info(f"示例用户创建成功: {sample_user.username}")
            else:
                logger.info("数据库已有用户，跳过创建")
                
        finally:
            db.close()
        
        logger.info("数据库初始化完成！")
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
