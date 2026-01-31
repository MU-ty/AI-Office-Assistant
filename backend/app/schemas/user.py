"""
用户相关的数据验证模型
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class UserCreate(BaseModel):
    """创建用户请求模型"""
    username: str
    email: str
    password: str
    full_name: Optional[str] = None


class UserUpdate(BaseModel):
    """更新用户请求模型"""
    email: Optional[str] = None
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """用户登录请求模型"""
    username: str
    password: str


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求模型"""
    refresh_token: str
