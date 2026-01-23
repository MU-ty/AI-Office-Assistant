from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User
from app.auth.dependencies import get_current_user, get_current_admin_user
from app.schemas import UserProfileResponse, UserUpdateRequest, PasswordChangeRequest
from app.auth import verify_password, get_password_hash, validate_password_strength

router = APIRouter(prefix="/api/v1/users", tags=["用户"])


@router.get("/me", response_model=UserProfileResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    """
    获取当前用户信息
    """
    return current_user


@router.put("/me", response_model=UserProfileResponse)
def update_current_user_profile(
    update_data: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    更新当前用户信息
    """
    
    # 更新允许的字段
    update_dict = update_data.dict(exclude_unset=True)
    
    for key, value in update_dict.items():
        if value is not None:
            setattr(current_user, key, value)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.post("/change-password")
def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    修改用户密码
    """
    
    # 验证旧密码
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="旧密码错误",
        )
    
    # 验证新密码和确认密码是否一致
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码和确认密码不一致",
        )
    
    # 验证新密码强度
    is_valid, error_msg = validate_password_strength(password_data.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )
    
    # 检查新密码是否与旧密码相同
    if password_data.new_password == password_data.old_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码不能与旧密码相同",
        )
    
    # 更新密码
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "密码修改成功"}


@router.get("/{user_id}", response_model=UserProfileResponse)
def get_user_profile(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    获取用户信息（只能查看自己或管理员权限）
    """
    
    # 检查权限（只能查看自己的信息，除非是管理员）
    if str(current_user.id) != user_id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该用户信息",
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    
    return user


@router.get("")
def list_users(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_admin_user),  # 需要管理员权限
    db: Session = Depends(get_db),
):
    """
    列出所有用户（仅管理员）
    """
    
    users = db.query(User).offset(skip).limit(limit).all()
    total = db.query(User).count()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": users,
    }
