"""JWT Token 测试"""
import pytest
from datetime import timedelta, datetime, timezone
from jose import JWTError
from app.auth import create_access_token, create_refresh_token, decode_token
from app.core.config import settings


class TestCreateAccessToken:
    """访问令牌生成测试"""
    
    def test_create_access_token_success(self):
        """测试成功创建访问令牌"""
        data = {"sub": "test-user-id", "username": "testuser"}
        token = create_access_token(data)
        
        # Token 应该是字符串
        assert isinstance(token, str)
        # Token 应该由三部分组成（Header.Payload.Signature）
        assert token.count(".") == 2
    
    def test_create_access_token_with_custom_expiry(self):
        """测试使用自定义过期时间创建令牌"""
        data = {"sub": "test-user-id", "username": "testuser"}
        expires_delta = timedelta(minutes=60)
        token = create_access_token(data, expires_delta)
        
        # 解码并验证
        payload = decode_token(token)
        assert payload["sub"] == "test-user-id"
        assert payload["username"] == "testuser"
    
    def test_create_access_token_exp_is_timestamp(self):
        """测试 exp 字段是 Unix 时间戳（整数）"""
        data = {"sub": "test-user-id"}
        token = create_access_token(data)
        payload = decode_token(token)
        
        # exp 应该是整数（Unix 时间戳），而不是 datetime 对象
        assert isinstance(payload["exp"], int)
        # exp 应该大于当前时间戳
        assert payload["exp"] > int(datetime.now(timezone.utc).timestamp())


class TestCreateRefreshToken:
    """刷新令牌生成测试"""
    
    def test_create_refresh_token_success(self):
        """测试成功创建刷新令牌"""
        data = {"sub": "test-user-id", "username": "testuser"}
        token = create_refresh_token(data)
        
        assert isinstance(token, str)
        assert token.count(".") == 2
    
    def test_refresh_token_has_type_field(self):
        """测试刷新令牌包含 type 字段"""
        data = {"sub": "test-user-id"}
        token = create_refresh_token(data)
        payload = decode_token(token)
        
        # 刷新令牌应该包含 type: "refresh"
        assert payload.get("type") == "refresh"
    
    def test_refresh_token_exp_is_timestamp(self):
        """测试 refresh token 的 exp 字段是 Unix 时间戳"""
        data = {"sub": "test-user-id"}
        token = create_refresh_token(data)
        payload = decode_token(token)
        
        # exp 应该是整数
        assert isinstance(payload["exp"], int)


class TestDecodeToken:
    """Token 解码测试"""
    
    def test_decode_valid_token(self):
        """测试解码有效的 token"""
        data = {"sub": "test-user-id", "username": "testuser"}
        token = create_access_token(data)
        payload = decode_token(token)
        
        assert payload["sub"] == "test-user-id"
        assert payload["username"] == "testuser"
    
    def test_decode_invalid_token_raises_error(self):
        """测试解码无效的 token 会抛出异常"""
        invalid_token = "invalid.token.here"
        
        with pytest.raises(JWTError):
            decode_token(invalid_token)
    
    def test_decode_expired_token_raises_error(self):
        """测试解码过期的 token 会抛出异常"""
        # 创建一个已过期的 token（过期时间为负数）
        data = {"sub": "test-user-id"}
        expires_delta = timedelta(seconds=-10)  # 10秒前已过期
        token = create_access_token(data, expires_delta)
        
        with pytest.raises(JWTError):
            decode_token(token)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
