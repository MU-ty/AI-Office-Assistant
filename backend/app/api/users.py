"""用户路由"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import User

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("")
async def list_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """获取用户列表"""
    users = db.query(User).offset(skip).limit(limit).all()
    return {
        "total": db.query(User).count(),
        "items": [u.to_dict() for u in users]
    }


@router.get("/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """获取单个用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user.to_dict()
