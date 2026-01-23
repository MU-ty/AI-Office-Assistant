from fastapi import APIRouter
from app.api.routes import auth_router, users_router

router = APIRouter()

# 包含所有子路由
router.include_router(auth_router)
router.include_router(users_router)

__all__ = ["router"]
