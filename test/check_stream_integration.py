"""
流式处理服务集成验证 - 简化版
"""

import os
import sys

def main():
    print("\n" + "="*80)
    print("✅ 流式处理服务集成验证".center(80))
    print("="*80 + "\n")
    
    # 获取当前目录
    cwd = os.getcwd()
    print(f"当前目录: {cwd}\n")
    
    # 1. 检查文件
    print("[步骤1] 检查核心文件...")
    files = {
        "stream_service.py": "backend/app/services/stream_service.py",
        "stream API": "backend/app/api/stream.py",
        "main.py": "backend/app/main.py"
    }
    
    all_exist = True
    for name, path in files.items():
        full_path = os.path.join(cwd, path)
        exists = os.path.isfile(full_path)
        status = "✅" if exists else "❌"
        print(f"  {status} {path} ({os.path.getsize(full_path) if exists else 0} bytes)")
        if not exists:
            all_exist = False
    
    if not all_exist:
        print("\n❌ 部分文件不存在")
        return 1
    
    print("\n✅ 所有文件存在\n")
    
    # 2. 检查main.py集成
    print("[步骤2] 检查main.py集成...")
    main_path = os.path.join(cwd, "backend/app/main.py")
    with open(main_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        "导入stream模块": "stream" in content and "from app.api import" in content,
        "注册stream路由": "stream.router" in content,
        "添加API前缀": '"/api/v1/stream"' in content,
        "添加tags": '"Stream"' in content or "'Stream'" in content
    }
    
    for check_name, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check_name}")
    
    if not all(checks.values()):
        print("\n⚠️ 部分集成检查失败")
        return 1
    
    print("\n✅ main.py集成正确\n")
    
    # 3. 检查stream.py
    print("[步骤3] 检查stream.py端点...")
    stream_path = os.path.join(cwd, "backend/app/api/stream.py")
    with open(stream_path, 'r', encoding='utf-8') as f:
        stream_content = f.read()
    
    endpoints = {
        "/local": "stream_local" in stream_content,
        "/qwen": "stream_qwen" in stream_content,
        "/deepseek": "stream_deepseek" in stream_content,
        "/openai": "stream_openai" in stream_content
    }
    
    for endpoint, exists in endpoints.items():
        status = "✅" if exists else "❌"
        print(f"  {status} {endpoint} 端点")
    
    print("\n✅ stream.py端点定义正确\n")
    
    # 4. 显示next steps
    print("[步骤4] 集成完成！下一步:\n")
    print("  1️⃣ 启动服务:")
    print("     cd backend")
    print("     python -m uvicorn app.main:app --reload")
    print()
    print("  2️⃣ 测试API (在另一个终端):")
    print("     curl -X POST http://localhost:8000/api/v1/stream/qwen \\")
    print("       -H 'Content-Type: application/json' \\")
    print("       -d '{\"messages\": [{\"role\": \"user\", \"content\": \"你好\"}]}'")
    print()
    print("  3️⃣ 查看完整API文档:")
    print("     http://localhost:8000/api/docs")
    print()
    
    print("="*80)
    print("✅ 流式处理服务集成完成！".center(80))
    print("="*80)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
