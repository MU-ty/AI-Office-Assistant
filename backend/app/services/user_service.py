"""
用户认证与管理服务层
提供业务逻辑实现 - 这里逐个实现
"""

from typing import List, Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
import jwt

from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.utils.logger import get_logger
from app.utils.exceptions import (
    UserNotFoundError, UserAlreadyExistsError, InvalidCredentialsError
)

logger = get_logger(__name__)

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """用户服务 - 处理用户相关业务逻辑"""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _ensure_default_admin(self) -> None:
        """确保存在默认管理员账号（仅用于本地测试）"""
        default_username = "admin"
        default_email = "admin@example.com"
        default_password = "Admin@123456"

        existing = await self.get_user_by_username(default_username)
        if existing:
            return
        existing_email = await self.get_user_by_email(default_email)
        if existing_email:
            return

        hashed_password = await self.hash_password(default_password)
        admin = User(
            username=default_username,
            email=default_email,
            full_name="系统管理员",
            hashed_password=hashed_password,
            is_active=True
        )
        self.db.add(admin)
        await self.db.commit()
        await self.db.refresh(admin)
        logger.info("已创建默认管理员账号: admin / Admin@123456")
    
    async def register_user(self, user_data: UserCreate) -> UserResponse:
        """
        注册新用户
        
        1. 检查用户名和邮箱是否已存在
        2. 密码加密
        3. 创建用户记录
        4. 返回用户信息
        """
        logger.info(f"用户注册: {user_data.username}")

        existing = await self.get_user_by_username(user_data.username)
        if existing:
            raise UserAlreadyExistsError("用户名已存在")

        existing_email = await self.get_user_by_email(user_data.email)
        if existing_email:
            raise UserAlreadyExistsError("邮箱已存在")

        hashed_password = await self.hash_password(user_data.password)
        user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            is_active=True
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return UserResponse.model_validate(user)
    
    async def login_user(self, username: str, password: str) -> dict:
        """
        用户登录
        
        1. 查询用户
        2. 验证密码
        3. 生成JWT令牌
        4. 创建会话记录
        """
        logger.info(f"用户登录: {username}")

        await self._ensure_default_admin()

        query = select(User).where(or_(User.username == username, User.email == username))
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise InvalidCredentialsError()

        if not await self.verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()

        access_token = await self.generate_jwt_token(str(user.id))
        refresh_token = await self.generate_refresh_token(str(user.id))

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": UserResponse.model_validate(user)
        }
    
    async def refresh_access_token(self, refresh_token: str) -> dict:
        """
        刷新访问令牌
        
        1. 验证刷新令牌有效性
        2. 解析令牌获取user_id
        3. 生成新的访问令牌
        """
        try:
            payload = jwt.decode(
                refresh_token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            if payload.get("type") != "refresh":
                raise InvalidCredentialsError("无效的刷新令牌")
        except jwt.ExpiredSignatureError:
            raise InvalidCredentialsError("刷新令牌已过期")
        except jwt.InvalidTokenError:
            raise InvalidCredentialsError("无效的刷新令牌")

        user_id = payload.get("sub")
        if not user_id:
            raise InvalidCredentialsError("无效的刷新令牌")

        access_token = await self.generate_jwt_token(str(user_id))
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    async def get_user_by_id(self, user_id: str) -> UserResponse:
        """获取用户信息"""
        query = select(User).where(User.id == int(user_id))
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        if not user:
            raise UserNotFoundError()
        return UserResponse.model_validate(user)
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """通过用户名查询用户"""
        query = select(User).where(User.username == username)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """通过邮箱查询用户"""
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> UserResponse:
        """更新用户信息"""
        query = select(User).where(User.id == int(user_id))
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        if not user:
            raise UserNotFoundError()

        if user_data.email is not None:
            user.email = user_data.email
        if user_data.full_name is not None:
            user.full_name = user_data.full_name

        user.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(user)
        return UserResponse.model_validate(user)
    
    async def delete_user(self, user_id: str) -> None:
        """删除用户 (软删除)"""
        query = select(User).where(User.id == int(user_id))
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        if not user:
            raise UserNotFoundError()
        user.is_active = False
        user.updated_at = datetime.utcnow()
        await self.db.commit()
    
    async def list_users(self, skip: int = 0, limit: int = 10) -> List[UserResponse]:
        """获取用户列表"""
        query = select(User).offset(skip).limit(limit)
        result = await self.db.execute(query)
        users = result.scalars().all()
        return [UserResponse.model_validate(user) for user in users]
    
    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)
    
    async def hash_password(self, password: str) -> str:
        """密码加密"""
        return pwd_context.hash(password)
    
    async def generate_jwt_token(self, user_id: str, expires_in_minutes: int = 30) -> str:
        """生成JWT访问令牌"""
        expire = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
        payload = {
            "sub": user_id,
            "exp": expire,
            "type": "access"
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    async def generate_refresh_token(self, user_id: str, expires_in_days: int = 7) -> str:
        """生成刷新令牌"""
        expire = datetime.now(timezone.utc) + timedelta(days=expires_in_days)
        payload = {
            "sub": user_id,
            "exp": expire,
            "type": "refresh"
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
