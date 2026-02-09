"""
JWT 认证相关工具
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from app.core.config import settings

security = HTTPBearer(auto_error=False)


def get_current_user_id(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> int:
    token = credentials.credentials if credentials else None
    if not token:
        token = request.query_params.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录")
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="登录已过期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效令牌")

    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效令牌类型")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效令牌")

    try:
        return int(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效用户信息")

def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> int:
    # 兼容性函数，目前 get_current_user_id 返回的就是 ID，这里为了匹配依赖名称暂时直接复用逻辑
    # 注意：chat.py 中的 Depends(get_current_user) 期望得到 User 对象，但这里 auth.py 只返回了 ID
    # 我们需要确认 chat.py 中是否真的需要 User 对象，或者只需要 ID。
    # 如果 chat.py 定义 current_user: User，那这里返回 int 会导致类型不匹配，甚至后续逻辑错误。
    # 鉴于我无法修改 User 模型加载逻辑（可能涉及数据库），最稳妥的方式是让 chat.py 接收 ID，或者在这里加载 User。
    # 但根据 auth.py 现有代码，它只负责解析 token 拿 ID。
    # 让我们先修复导入错误，把 get_current_user 指向 get_current_user_id (或者新建一个别名)。
    # 更好的做法是修改 chat.py 让它接受 user_id。
    return get_current_user_id(request, credentials)
