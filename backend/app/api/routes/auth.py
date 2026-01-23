from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from app.db.database import get_db
from app.db.models import User
from app.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    RefreshTokenRequest,
)
from app.auth import (
    verify_password,
    get_password_hash,
    validate_password_strength,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.config import settings

router = APIRouter(prefix="/api/v1/auth", tags=["认证"])


@router.post("/register", response_model=dict)
def register(
    user_data: UserRegisterRequest,
    db: Session = Depends(get_db),
):
    """
    用户注册接口
    
    - **username**: 用户名，3-50 个字符
    - **email**: 邮箱地址（必须有效）
    - **password**: 密码，至少 8 个字符
    - **full_name**: 完整名称（可选）
    """
    
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(
        User.username == user_data.username
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在",
        )
    
    # 检查邮箱是否已存在
    existing_email = db.query(User).filter(
        User.email == user_data.email
    ).first()
    
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册",
        )
    
    # 验证密码强度
    is_valid, error_msg = validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )
    
    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {
        "message": "注册成功，请登录",
        "user_id": str(db_user.id),
        "username": db_user.username,
        "email": db_user.email,
    }


@router.post("/login", response_model=TokenResponse)
def login(
    login_data: UserLoginRequest,
    db: Session = Depends(get_db),
):
    """
    用户登录接口
    
    返回访问令牌和刷新令牌
    """
    
    # 查询用户（支持用户名或邮箱登录）
    db_user = db.query(User).filter(
        (User.username == login_data.username) | (User.email == login_data.username)
    ).first()
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    
    # 验证密码
    if not verify_password(login_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    
    # 检查用户状态
    if db_user.status.value != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账户已被禁用",
        )
    
    # 更新最后登录时间
    db_user.last_login_at = datetime.now()
    db.commit()
    
    # 创建 tokens
    access_token = create_access_token(
        data={"sub": str(db_user.id), "username": db_user.username},
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    refresh_token = create_refresh_token(
        data={"sub": str(db_user.id), "username": db_user.username}
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # 转换为秒
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """
    刷新访问令牌接口
    
    使用刷新令牌获取新的访问令牌
    """
    
    try:
        payload = decode_token(request.refresh_token)
        
        # 检查 token 类型
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的刷新令牌",
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌无效",
            )
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="刷新令牌无效或已过期",
        )
    
    # 查询用户
    db_user = db.query(User).filter(User.id == user_id).first()
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
        )
    
    # 创建新的访问令牌
    new_access_token = create_access_token(
        data={"sub": str(db_user.id), "username": db_user.username},
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=request.refresh_token,  # 保持原有的刷新令牌
        token_type="Bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout")
def logout():
    """
    用户登出接口
    
    注意：在前端实现中，应该删除本地存储的 token
    """
    return {"message": "登出成功"}
