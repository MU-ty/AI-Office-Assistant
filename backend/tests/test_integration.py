"""认证与授权功能集成测试"""

import pytest
import sys
from pathlib import Path
import os

# 添加项目路径
project_root = Path(__file__).parent.parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

from app.auth import create_access_token, create_refresh_token, decode_token
from app.auth.password import verify_password, get_password_hash
from app.db.models import User
from app.core.config import settings


class TestIntegrationAuth:
    """认证功能集成测试"""
    
    def test_complete_auth_flow(self):
        """测试完整的认证流程"""
        # 1. 测试密码哈希和验证
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True
        
        # 2. 测试JWT令牌创建和解码
        user_data = {"sub": "test-user-123", "username": "testuser"}
        
        # 创建访问令牌
        access_token = create_access_token(user_data)
        access_payload = decode_token(access_token)
        
        assert access_payload["sub"] == "test-user-123"
        assert access_payload["username"] == "testuser"
        assert isinstance(access_payload["exp"], int)
        
        # 创建刷新令牌
        refresh_token = create_refresh_token(user_data)
        refresh_payload = decode_token(refresh_token)
        
        assert refresh_payload["type"] == "refresh"
        assert isinstance(refresh_payload["exp"], int)
        
        print("✅ 完整认证流程测试通过")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])