
import asyncio
import os
import sys

# 将当前目录添加到路径以便导入 app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.weknora_service import weknora_service
from app.core.config import settings

async def initialize_weknora():
    """初始化 WeKnora 模型配置"""
    print("开始初始化 WeKnora 模型配置...")
    
    try:
        # 检查基本配置
        if not settings.WEKNORA_BASE_URL or not settings.WEKNORA_API_KEY:
            print("⚠️  WeKnora 配置未完整，跳过初始化")
            return None, None
        
        # 1. 获取现有模型列表
        try:
            existing_models = await weknora_service.list_models()
        except Exception as e:
            print(f"⚠️  获取模型列表失败: {str(e)}")
            existing_models = []
        
        embedding_model_id = None
        qa_model_id = None
        
        for model in existing_models:
            if model.get("type") == "Embedding":
                embedding_model_id = model.get("id")
            elif model.get("type") == "KnowledgeQA":
                qa_model_id = model.get("id")
        
        # 2. 如果没有 Embedding 模型，创建一个
        if not embedding_model_id and settings.QWEN_API_KEY:
            try:
                print("未发现 Embedding 模型，正在创建 (使用阿里云 DashScope)...")
                # 使用阿里云的 text-embedding-v3
                params = {
                    "base_url": settings.QWEN_BASE_URL,
                    "api_key": settings.QWEN_API_KEY,
                    "provider": "aliyun",
                    "embedding_parameters": {
                        "dimension": 1024
                    }
                }
                res = await weknora_service.create_model(
                    name="text-embedding-v3",
                    model_type="Embedding",
                    source="remote",
                    parameters=params
                )
                embedding_model_id = res.get("data", {}).get("id") or res.get("id")
                if embedding_model_id:
                    print(f"✅ Embedding 模型创建成功: {embedding_model_id}")
                else:
                    print(f"⚠️  Embedding 模型创建响应解析失败: {res}")
            except Exception as e:
                print(f"⚠️  创建 Embedding 模型失败: {str(e)}")
        elif embedding_model_id:
            print(f"✅ 已存在 Embedding 模型: {embedding_model_id}")

        # 3. 如果没有 QA 模型，创建一个
        if not qa_model_id and settings.QWEN_API_KEY:
            try:
                print("未发现 KnowledgeQA 模型，正在创建...")
                params = {
                    "base_url": settings.QWEN_BASE_URL,
                    "api_key": settings.QWEN_API_KEY,
                    "provider": "aliyun"
                }
                res = await weknora_service.create_model(
                    name=settings.QWEN_MODEL_NAME,
                    model_type="KnowledgeQA",
                    source="remote",
                    parameters=params
                )
                qa_model_id = res.get("data", {}).get("id") or res.get("id")
                if qa_model_id:
                    print(f"✅ KnowledgeQA 模型创建成功: {qa_model_id}")
                else:
                    print(f"⚠️  KnowledgeQA 模型创建响应解析失败: {res}")
            except Exception as e:
                print(f"⚠️  创建 KnowledgeQA 模型失败: {str(e)}")
        elif qa_model_id:
            print(f"✅ 已存在 KnowledgeQA 模型: {qa_model_id}")

        return embedding_model_id, qa_model_id

    except Exception as e:
        print(f"❌ 初始化 WeKnora 失败: {str(e)}")
        import traceback
        traceback.print_exc()
