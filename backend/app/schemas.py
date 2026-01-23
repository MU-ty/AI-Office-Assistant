from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum
from uuid import UUID


class UserStatus(str, Enum):
    """用户状态"""
    active = "active"
    inactive = "inactive"
    suspended = "suspended"


class UserRole(str, Enum):
    """用户角色"""
    admin = "admin"
    user = "user"
    guest = "guest"


# ==================== 认证相关 Schema ====================

class UserRegisterRequest(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "password": "SecurePass123",
                "full_name": "John Doe"
            }
        }


class UserLoginRequest(BaseModel):
    """用户登录请求"""
    username: str
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "password": "SecurePass123"
            }
        }


class TokenResponse(BaseModel):
    """Token 响应"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int  # 秒数
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "Bearer",
                "expires_in": 1800
            }
        }


class RefreshTokenRequest(BaseModel):
    """刷新 Token 请求"""
    refresh_token: str


# ==================== 用户相关 Schema ====================

class UserProfileResponse(BaseModel):
    """用户资料响应"""
    id: UUID
    username: str
    email: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    
    organization: Optional[str]
    position: Optional[str]
    phone: Optional[str]
    
    status: UserStatus
    role: UserRole
    
    is_email_verified: bool
    is_phone_verified: bool
    
    language: str
    timezone: str
    theme: str
    
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class UserUpdateRequest(BaseModel):
    """用户信息更新请求"""
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    organization: Optional[str] = None
    position: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    
    language: Optional[str] = None
    timezone: Optional[str] = None
    theme: Optional[str] = None
    notification_enabled: Optional[bool] = None


class PasswordChangeRequest(BaseModel):
    """密码修改请求"""
    old_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str


# ==================== 权限和角色 Schema ====================

class RoleAssignmentRequest(BaseModel):
    """角色分配请求"""
    user_id: UUID
    role: UserRole
    reason: Optional[str] = None


class PermissionResponse(BaseModel):
    """权限响应"""
    id: UUID
    user_id: UUID
    permission: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== 错误响应 Schema ====================

class ErrorResponse(BaseModel):
    """错误响应"""
    code: int
    message: str
    detail: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": 401,
                "message": "Unauthorized",
                "detail": "Invalid credentials"
            }
        }
