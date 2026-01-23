"""认证流程测试"""
import pytest
from app.auth import verify_password, get_password_hash, validate_password_strength


class TestPasswordValidation:
    """密码验证测试"""
    
    def test_verify_password_success(self):
        """测试密码验证成功"""
        plain_password = "TestPassword123"
        hashed_password = get_password_hash(plain_password)
        
        # 相同密码应该验证成功
        assert verify_password(plain_password, hashed_password) is True
    
    def test_verify_password_failure(self):
        """测试密码验证失败"""
        plain_password = "TestPassword123"
        wrong_password = "WrongPassword456"
        hashed_password = get_password_hash(plain_password)
        
        # 不同密码应该验证失败
        assert verify_password(wrong_password, hashed_password) is False
    
    def test_password_hash_is_different_each_time(self):
        """测试每次哈希生成的结果不同（bcrypt 的 salt）"""
        password = "TestPassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # 两次哈希结果应该不同（由于 salt）
        assert hash1 != hash2
        # 但都应该能验证相同的密码
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestPasswordStrength:
    """密码强度验证测试"""
    
    def test_password_too_short(self):
        """测试密码过短"""
        short_password = "Pass1"  # 少于 8 字符
        is_valid, error_msg = validate_password_strength(short_password)
        
        assert is_valid is False
        assert "至少需要" in error_msg or "长度" in error_msg
    
    def test_password_missing_uppercase(self):
        """测试密码缺少大写字母"""
        password = "password123!@#"  # 没有大写字母
        is_valid, error_msg = validate_password_strength(password)
        
        assert is_valid is False
        # 如果配置要求大写字母
        if "PASSWORD_REQUIRE_UPPERCASE" in str(error_msg).upper():
            assert "大写字母" in error_msg or "uppercase" in error_msg.lower()
    
    def test_password_missing_numbers(self):
        """测试密码缺少数字"""
        password = "PasswordTest!@#"  # 没有数字
        is_valid, error_msg = validate_password_strength(password)
        
        assert is_valid is False
        assert "数字" in error_msg or "number" in error_msg.lower()
    
    def test_password_valid_strong(self):
        """测试强密码"""
        strong_password = "StrongPassword123"
        is_valid, error_msg = validate_password_strength(strong_password)
        
        assert is_valid is True
        assert error_msg == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
