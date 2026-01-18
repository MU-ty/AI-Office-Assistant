"""用户模型"""

from sqlalchemy import Column, String, Boolean, Text
from .base import BaseModel


class User(BaseModel):
    """用户数据模型"""
    
    __tablename__ = "users"
    
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    bio = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<User {self.username}>"
