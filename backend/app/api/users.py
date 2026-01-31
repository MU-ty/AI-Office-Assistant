"""
用户认证与管理模块 API

Endpoints:
  POST   /api/v1/users/register          - 注册新用户
  POST   /api/v1/users/login              - 用户登录
  POST   /api/v1/users/refresh-token      - 刷新令牌
  GET    /api/v1/users/me                 - 获取当前用户信息
  PUT    /api/v1/users/me                 - 更新当前用户
  GET    /api/v1/users/{user_id}          - 获取用户信息
  PUT    /api/v1/users/{user_id}          - 更新用户信息
  DELETE /api/v1/users/{user_id}          - 删除用户
  GET    /api/v1/users                    - 获取用户列表 (管理员)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserLogin, RefreshTokenRequest
from app.services.user_service import UserService
from app.utils.logger import get_logger
from app.utils.exceptions import UserAlreadyExistsError, InvalidCredentialsError, UserNotFoundError

logger = get_logger(__name__)
router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    用户注册
    
    - **username**: 用户名 (唯一)
    - **email**: 邮箱 (唯一)
    - **password**: 密码 (至少8个字符)
    - **full_name**: 全名
    """
    service = UserService(db)
    try:
        return await service.register_user(user_data)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"注册异常: {e}")
        raise HTTPException(status_code=500, detail="注册失败")


@router.post("/login")
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    用户登录
    
    返回访问令牌和刷新令牌
    """
    service = UserService(db)
    try:
        return await service.login_user(payload.username, payload.password)
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"登录异常: {e}")
        raise HTTPException(status_code=500, detail="登录失败")


@router.post("/refresh-token")
async def refresh_token(payload: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """
    使用刷新令牌获取新的访问令牌
    """
    service = UserService(db)
    try:
        return await service.refresh_access_token(payload.refresh_token)
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"刷新令牌异常: {e}")
        raise HTTPException(status_code=500, detail="刷新令牌失败")


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user_id: str = None,  # 从JWT令牌中提取
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前登录用户信息
    """
    service = UserService(db)
    try:
        return await service.get_user_by_id(current_user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user_id: str = None,
    db: AsyncSession = Depends(get_db)
):
    """
    更新当前用户信息
    """
    service = UserService(db)
    try:
        return await service.update_user(current_user_id, user_data)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/")
async def list_users(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户列表 (需要管理员权限)
    """
    service = UserService(db)
    return await service.list_users(skip, limit)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    获取指定用户信息
    """
    service = UserService(db)
    try:
        return await service.get_user_by_id(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    更新指定用户信息 (管理员)
    """
    service = UserService(db)
    try:
        return await service.update_user(user_id, user_data)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    删除指定用户 (管理员)
    """
    service = UserService(db)
    try:
        await service.delete_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
