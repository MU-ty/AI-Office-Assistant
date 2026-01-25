"""
自定义异常类
"""


class BaseException(Exception):
    """基础异常类"""
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(self.message)


class UserNotFoundError(BaseException):
    """用户不存在错误"""
    def __init__(self, message: str = "用户不存在"):
        super().__init__(message, 404)


class UserAlreadyExistsError(BaseException):
    """用户已存在错误"""
    def __init__(self, message: str = "用户已存在"):
        super().__init__(message, 409)


class InvalidCredentialsError(BaseException):
    """无效凭据错误"""
    def __init__(self, message: str = "用户名或密码不正确"):
        super().__init__(message, 401)


class MeetingNotFoundError(BaseException):
    """会议不存在错误"""
    def __init__(self, message: str = "会议不存在"):
        super().__init__(message, 404)


class InvalidFileError(BaseException):
    """无效文件错误"""
    def __init__(self, message: str = "无效的文件"):
        super().__init__(message, 400)


class ProcessingError(BaseException):
    """处理错误"""
    def __init__(self, message: str = "处理出错"):
        super().__init__(message, 500)
