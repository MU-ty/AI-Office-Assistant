from passlib.context import CryptContext
from app.core.config import settings

# 密码加密配置
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码是否匹配"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """对密码进行哈希加密"""
    return pwd_context.hash(password)


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    验证密码强度
    
    返回: (is_valid, error_message)
    """
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        return False, f"密码长度至少需要 {settings.PASSWORD_MIN_LENGTH} 个字符"
    
    if settings.PASSWORD_REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
        return False, "密码必须包含至少一个大写字母"
    
    if settings.PASSWORD_REQUIRE_NUMBERS and not any(c.isdigit() for c in password):
        return False, "密码必须包含至少一个数字"
    
    if settings.PASSWORD_REQUIRE_SPECIAL_CHARS and not any(c in "!@#$%^&*" for c in password):
        return False, "密码必须包含至少一个特殊字符 (!@#$%^&*)"
    
    return True, ""
