
import asyncio
from sqlalchemy import select
from app.core.database import engine, init_db
from app.models.user import User
from app.services.user_service import UserService
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

async def fix_admin_password():
    # 确保表存在
    await init_db()
    
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        user_service = UserService(session)
        
        # 查找现有的 admin 用户
        query = select(User).where(User.username == "admin")
        result = await session.execute(query)
        admin = result.scalar_one_or_none()
        
        if admin:
            # 重新生成正确的 hash
            new_hash = await user_service.hash_password("Admin@123456")
            admin.hashed_password = new_hash
            await session.commit()
            print("✅ 默认管理员 (admin) 密码已修复")
        else:
            # 如果不存在则创建
            await user_service._ensure_default_admin()
            print("✅ 默认管理员账号已创建")

if __name__ == "__main__":
    asyncio.run(fix_admin_password())
