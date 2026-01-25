#!/usr/bin/env python
"""
开发服务器启动脚本
自动处理路径和依赖加载
"""

import os
import sys
import subprocess
from pathlib import Path

# 获取当前脚本所在目录
current_dir = Path(__file__).parent.absolute()

# 设置工作目录
os.chdir(current_dir)

# 确保当前目录在 Python 路径中
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

print(f"✓ 工作目录: {current_dir}")
print(f"✓ Python 路径已配置")
print()

# 启动 Uvicorn 服务器
cmd = [
    sys.executable, "-m", "uvicorn",
    "app.main:app",
    "--reload",
    "--port", "8001",
    "--host", "0.0.0.0"
]

print(f"启动命令: {' '.join(cmd)}")
print(f"访问地址: http://127.0.0.1:8001")
print(f"API 文档: http://127.0.0.1:8001/docs")
print()
print("=" * 60)

try:
    subprocess.run(cmd)
except KeyboardInterrupt:
    print("\n服务已停止")
    sys.exit(0)
except Exception as e:
    print(f"错误: {e}")
    sys.exit(1)
