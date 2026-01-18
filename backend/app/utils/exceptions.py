"""自定义异常"""

from fastapi import HTTPException
from typing import Any, Dict, Optional


class APIException(HTTPException):
    """API异常基类"""
    
    def __init__(
        self,
        status_code: int = 400,
        detail: str = "请求出错",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class ValidationError(APIException):
    """验证错误"""
    
    def __init__(self, detail: str = "数据验证失败"):
        super().__init__(status_code=422, detail=detail)


class NotFoundError(APIException):
    """资源不存在"""
    
    def __init__(self, detail: str = "资源不存在"):
        super().__init__(status_code=404, detail=detail)


class UnauthorizedError(APIException):
    """未授权"""
    
    def __init__(self, detail: str = "未授权访问"):
        super().__init__(status_code=401, detail=detail)


class ForbiddenError(APIException):
    """禁止访问"""
    
    def __init__(self, detail: str = "禁止访问"):
        super().__init__(status_code=403, detail=detail)
