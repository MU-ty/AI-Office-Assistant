from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthenticationCredentials
from sqlalchemy.orm import Session
from app.auth import decode_token
from app.db.database import get_db
from app.db.models import User
from jose import JWTError

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthenticationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    获取当前用户（从 JWT token）
    
    Args:
        credentials: HTTP Bearer token
        db: 数据库会话
    
    Returns:
        当前用户对象
    
    Raises:
        HTTPException: Token 无效或用户不存在
    """
    token = credentials.credentials
    
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token 无效",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 无效或已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 从数据库获取用户
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.status.value != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账户已被禁用",
        )
    
    return user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    获取当前管理员用户
    
    Args:
        current_user: 当前用户
    
    Returns:
        当前用户对象
    
    Raises:
        HTTPException: 用户不是管理员
    """
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员才能访问此资源",
        )
    
    return current_user


def require_permission(permission: str):
    """
    权限验证装饰器工厂
    
    Args:
        permission: 所需权限名称
    
    Returns:
        依赖函数
    """
    async def check_permission(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        from app.db.models import UserPermission
        
        # 管理员拥有所有权限
        if current_user.role.value == "admin":
            return current_user
        
        # 检查用户是否拥有所需权限
        user_permission = db.query(UserPermission).filter(
            UserPermission.user_id == current_user.id,
            UserPermission.permission == permission,
        ).first()
        
        if not user_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"用户没有 '{permission}' 权限",
            )
        
        return current_user
    
    return check_permission
