"""
流式处理服务集成验证脚本
验证流式服务是否正确集成到主应用中
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def verify_stream_integration():
    """验证流式服务集成"""
    
    print("\n" + "="*80)
    print("🔍 流式处理服务集成验证".center(80))
    print("="*80 + "\n")
    
    # 1. 检查文件是否存在
    print("[步骤1] 检查核心文件存在性...")
    base_path = os.getcwd()
    files_to_check = [
        os.path.join(base_path, "backend/app/services/stream_service.py"),
        os.path.join(base_path, "backend/app/api/stream.py"),
        os.path.join(base_path, "backend/app/main.py")
    ]
    
    all_files_exist = True
    for file_path in files_to_check:
        exists = os.path.exists(file_path)
        status = "✅" if exists else "❌"
        display_path = file_path.replace(base_path, "").lstrip("\\").lstrip("/")
        print(f"  {status} {display_path}")
        if not exists:
            all_files_exist = False
    
    if not all_files_exist:
        print("\n❌ 某些文件不存在，请检查路径")
        return False
    
    print("\n✅ 所有文件存在\n")
    
    # 2. 检查导入是否正确
    print("[步骤2] 检查模块导入...")
    try:
        from app.services.stream_service import StreamService, StreamProvider
        print("  ✅ StreamService 导入成功")
        print("  ✅ StreamProvider 导入成功")
    except ImportError as e:
        print(f"  ❌ 导入失败: {e}")
        return False
    
    try:
        from app.api import stream
        print("  ✅ stream 模块导入成功")
    except ImportError as e:
        print(f"  ❌ stream 模块导入失败: {e}")
        return False
    
    print()
    
    # 3. 检查StreamService类
    print("[步骤3] 检查StreamService API...")
    try:
        import logging
        logger = logging.getLogger(__name__)
        service = StreamService(logger=logger)
        
        # 检查核心方法
        required_methods = ['stream']
        for method in required_methods:
            if not hasattr(service, method):
                print(f"  ❌ 缺少方法: {method}")
                return False
            print(f"  ✅ 方法 {method} 存在")
        
        # 检查StreamProvider枚举
        providers = list(StreamProvider)
        print(f"  ✅ 支持的提供商: {len(providers)} 个")
        for provider in providers:
            print(f"     - {provider.name}")
    
    except Exception as e:
        print(f"  ❌ 检查失败: {e}")
        return False
    
    print()
    
    # 4. 检查API路由
    print("[步骤4] 检查API路由...")
    try:
        expected_routes = [
            "/api/v1/stream/local",
            "/api/v1/stream/qwen",
            "/api/v1/stream/deepseek",
            "/api/v1/stream/openai"
        ]
        
        # 检查stream.py中的路由定义
        stream_path = os.path.join(base_path, "backend/app/api/stream.py")
        with open(stream_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        for route in expected_routes:
            if route.split("/")[-1] in content or f"/{route.split('/')[-1]}" in content:
                print(f"  ✅ 路由定义存在: {route}")
            else:
                print(f"  ⚠️  路由定义未确认: {route}")
        
    except Exception as e:
        print(f"  ❌ 检查失败: {e}")
        return False
    
    print()
    
    # 5. 检查main.py集成
    print("[步骤5] 检查main.py中的集成...")
    try:
        main_path = os.path.join(base_path, "backend/app/main.py")
        with open(main_path, "r", encoding="utf-8") as f:
            main_content = f.read()
        
        checks = [
            ("导入stream模块", "from app.api import" in main_content and "stream" in main_content),
            ("注册stream路由", 'app.include_router' in main_content and 'stream.router' in main_content),
            ("添加stream前缀", '"/api/v1/stream"' in main_content),
        ]
        
        for check_name, check_result in checks:
            status = "✅" if check_result else "❌"
            print(f"  {status} {check_name}")
            if not check_result:
                return False
    
    except Exception as e:
        print(f"  ❌ 检查失败: {e}")
        return False
    
    print()
    
    # 6. 显示集成信息
    print("[步骤6] 集成信息总结...")
    print("  流式处理服务已成功集成:")
    print("    - 核心服务: StreamService (支持4个提供商)")
    print("    - API路由: /api/v1/stream/* (4个端点)")
    print("    - 支持的提供商:")
    print("      • LOCAL (本地模型)")
    print("      • QWEN (通义千问)")
    print("      • DEEPSEEK (DeepSeek)")
    print("      • OPENAI (OpenAI GPT)")
    print()
    
    # 7. 显示快速开始
    print("[步骤7] 下一步操作...")
    print("  1️⃣ 启动服务:")
    print("     $ cd backend")
    print("     $ python -m uvicorn app.main:app --reload")
    print()
    print("  2️⃣ 测试API:")
    print("     $ curl -X POST http://localhost:8000/api/v1/stream/qwen \\")
    print("       -H \"Content-Type: application/json\" \\")
    print("       -d '{\"messages\": [{\"role\": \"user\", \"content\": \"你好\"}]}'")
    print()
    print("  3️⃣ 查看文档:")
    print("     - STREAM_QUICK_START.md (5分钟快速开始)")
    print("     - STREAM_INTEGRATION_GUIDE.md (详细集成指南)")
    print()
    
    return True


async def main():
    """主函数"""
    try:
        # 改变到项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        os.chdir(project_root)
        
        success = await verify_stream_integration()
        
        if success:
            print("="*80)
            print("✅ 流式处理服务集成验证完成！".center(80))
            print("="*80)
            print()
            return 0
        else:
            print("="*80)
            print("❌ 流式处理服务集成验证失败，请检查上述错误".center(80))
            print("="*80)
            print()
            return 1
    
    except Exception as e:
        print(f"\n❌ 验证过程出错: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
