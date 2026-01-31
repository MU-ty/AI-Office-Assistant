
import asyncio
import os
import sys

# 将当前目录添加到路径以便导入 app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.weknora_service import weknora_service
from app.core.config import settings

async def force_update_weknora_models():
    print(f"开始同步 .env 中的 QWEN_API_KEY 到 WeKnora...")
    print(f"当前使用的 Key: {settings.QWEN_API_KEY[:10]}...")
    
    try:
        # 1. 获取现有模型列表
        existing_models = await weknora_service.list_models()
        
        for model in existing_models:
            model_id = model.get("id")
            model_type = model.get("type")
            model_name = model.get("name")
            
            print(f"正在更新模型: {model_name} ({model_type})...")
            
            # 构造更新参数
            params = {
                "base_url": settings.QWEN_BASE_URL,
                "api_key": settings.QWEN_API_KEY,
                "provider": "aliyun" if model_type == "Embedding" else "generic"
            }
            if model_type == "Embedding":
                params["embedding_parameters"] = {"dimension": 1024}
            
            # 调用 WeKnora 的模型更新接口 (PUT /models/:id)
            await weknora_service._request("PUT", f"/models/{model_id}", json={
                "name": model_name,
                "parameters": params
            })
            print(f"✅ 模型 {model_name} 密钥已同步更新。")
            
        print("\n✨ 所有模型密钥同步完成！请重新上传文档进行测试。")

    except Exception as e:
        print(f"❌ 同步失败: {str(e)}")

if __name__ == "__main__":
    asyncio.run(force_update_weknora_models())
