"""测试配置和夹具"""
import pytest
import sys
from pathlib import Path

# 将 backend 目录添加到 Python 路径
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))


@pytest.fixture(scope="session")
def test_settings():
    """提供测试设置"""
    from app.core.config import settings
    return settings


if __name__ == "__main__":
    pass
