"""API端点功能测试"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings


client = TestClient(app)


def test_register_endpoint():
    """测试用户注册端点"""
    response = client.post("/api/v1/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User"
    })
    # 由于用户可能已存在，我们主要测试端点是否可达
    assert response.status_code in [200, 400]  # 成功或用户已存在


def test_health_check():
    """测试健康检查端点"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_root_endpoint():
    """测试根端点"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert settings.PROJECT_NAME in data["message"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])