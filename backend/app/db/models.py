from sqlalchemy import Column, String, Boolean, DateTime, Enum, Text, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid
import enum
from app.db.database import Base


class UserStatus(str, enum.Enum):
    """用户状态枚举"""
    active = "active"
    inactive = "inactive"
    suspended = "suspended"
    deleted = "deleted"


class UserRole(str, enum.Enum):
    """用户角色枚举"""
    admin = "admin"
    user = "user"
    guest = "guest"


class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    avatar_url = Column(String(255))
    
    status = Column(Enum(UserStatus), default=UserStatus.active, index=True)
    role = Column(Enum(UserRole), default=UserRole.user)
    
    organization = Column(String(100))
    position = Column(String(100))
    phone = Column(String(20))
    bio = Column(Text)
    
    is_email_verified = Column(Boolean, default=False)
    is_phone_verified = Column(Boolean, default=False)
    email_verified_at = Column(DateTime(timezone=True))
    phone_verified_at = Column(DateTime(timezone=True))
    
    language = Column(String(10), default="zh-CN")
    timezone = Column(String(50), default="UTC")
    theme = Column(String(20), default="auto")
    notification_enabled = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True))
    deleted_at = Column(DateTime(timezone=True))
    
    meta_data = Column(JSONB, default={})


class UserSession(Base):
    """用户会话模型"""
    __tablename__ = "user_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    access_token = Column(String(500), nullable=False)
    refresh_token = Column(String(500))
    token_type = Column(String(20), default="Bearer")
    
    device_type = Column(String(50))
    device_name = Column(String(100))
    ip_address = Column(String(45))
    user_agent = Column(Text)
    
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True))


class UserPermission(Base):
    """用户权限模型"""
    __tablename__ = "user_permissions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    permission = Column(String(100), nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        # 复合唯一索引，同一用户的同一权限只能存在一次
        ('__table_args__',),
    )


class UserRole_Table(Base):
    """用户角色关联表"""
    __tablename__ = "user_role_assignments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    role = Column(Enum(UserRole), nullable=False)
    
    assigned_at = Column(DateTime(timezone=True), default=func.now())
    assigned_by = Column(UUID(as_uuid=True))  # 分配者的用户 ID
    
    reason = Column(Text)
    
    created_at = Column(DateTime(timezone=True), default=func.now())
    revoked_at = Column(DateTime(timezone=True))
