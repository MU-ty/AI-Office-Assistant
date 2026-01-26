"""
流式处理服务 - 集成指南和文档
"""

# ============================================================================
# 文档: 流式处理服务集成指南
# ============================================================================

INTEGRATION_GUIDE = """
# 流式处理服务集成指南

## 概述

本项目提供了一个统一的流式处理服务，支持多种AI模型的流式响应，包括：
- 本地模型 (Local)
- Qwen模型 (Qwen3-8B, Qwen-Plus等)
- DeepSeek模型 (DeepSeek-32B等)
- OpenAI模型 (GPT系列)

所有流式响应都采用OpenAI兼容的SSE (Server-Sent Events)格式。

## 核心模块

### 1. StreamService (app/services/stream_service.py)

**主要类:**

#### StreamFormatter
负责格式化流式响应数据。
```python
# 格式化单个数据块
chunk_str = StreamFormatter.format_chunk(
    chat_id="chatcmpl-xxxxx",
    content="响应内容",
    model="qwen-plus",
    question="用户问题"
)

# 格式化结束标记
end_str = StreamFormatter.format_end(
    chat_id="chatcmpl-xxxxx",
    model="qwen-plus"
)

# 格式化错误
error_str = StreamFormatter.format_error(
    chat_id="chatcmpl-xxxxx",
    error_msg="错误信息",
    code=500
)
```

#### LocalModelStream
本地模型流式处理器。
```python
local_stream = LocalModelStream(model=your_model, logger=logger)
async for chunk in local_stream.stream(messages=[...], question="..."):
    # 处理SSE格式的流式数据
    pass
```

#### RemoteAPIStream
远程API流式处理器，支持Qwen、DeepSeek、OpenAI。
```python
remote_stream = RemoteAPIStream(logger=logger)

# 调用Qwen API
async for chunk in remote_stream.stream_qwen(
    messages=[...],
    api_url="http://localhost:8000/v1/chat/completions",
    model_name="Qwen3-8B"
):
    pass

# 调用DeepSeek API
async for chunk in remote_stream.stream_deepseek(
    messages=[...],
    api_url="http://localhost:8000/v1/chat/completions"
):
    pass

# 调用OpenAI API
async for chunk in remote_stream.stream_openai(
    messages=[...],
    api_key="sk-xxx"
):
    pass
```

#### StreamService
统一的流式服务接口。
```python
from app.services.stream_service import StreamService, StreamProvider

stream_service = StreamService(logger=logger, model=None)

# 使用不同的提供商
async for chunk in stream_service.stream(
    provider=StreamProvider.QWEN,
    messages=[
        {"role": "system", "content": "你是一个助手"},
        {"role": "user", "content": "你好"}
    ],
    question="你好",
    api_url="http://localhost:8000/v1/chat/completions",
    model_name="Qwen3-8B"
):
    # 处理chunk
    pass
```

### 2. API端点 (app/api/stream.py)

提供RESTful API接口，支持以下端点：

```
POST /api/v1/stream/local
POST /api/v1/stream/qwen
POST /api/v1/stream/deepseek
POST /api/v1/stream/openai
```

所有端点都返回 `text/event-stream` 格式的SSE流式数据。

## 集成步骤

### 步骤1: 在main.py中注册API路由

```python
# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import stream  # 导入流式API

app = FastAPI()

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册流式API路由
app.include_router(stream.router)

# 其他路由...
@app.get("/health")
async def health():
    return {"status": "ok"}
```

### 步骤2: 依赖项配置

确保 `pyproject.toml` 中包含以下依赖：

```toml
[project]
dependencies = [
    "fastapi>=0.100.0",
    "uvicorn>=0.23.0",
    "aiohttp>=3.8.0",
    "pydantic>=2.0.0",
    # ... 其他依赖
]
```

### 步骤3: 后端服务使用

在你的业务逻辑中使用流式服务：

```python
# 例如在学术润色服务中添加流式支持

from app.services.stream_service import StreamService, StreamProvider
import logging

logger = logging.getLogger(__name__)

async def polish_with_stream(text: str, question: str = ""):
    \"\"\"
    使用流式处理进行学术润色
    \"\"\"
    stream_service = StreamService(logger=logger)
    
    messages = [
        {"role": "system", "content": "你是一个学术论文编辑助手。"},
        {"role": "user", "content": f"请帮我润色以下文本:\\n{text}"}
    ]
    
    full_response = ""
    async for chunk in stream_service.stream(
        provider=StreamProvider.QWEN,
        messages=messages,
        question=question,
        api_url="http://localhost:8000/v1/chat/completions",
        model_name="Qwen3-8B"
    ):
        # 处理每个chunk
        print(chunk, end="")
        # 可以在这里进行额外的处理，如保存到数据库等
        full_response += chunk
    
    return full_response
```

### 步骤4: 前端集成

#### 纯JavaScript

```javascript
async function streamPolish(text) {
    const response = await fetch('http://localhost:8000/api/v1/stream/qwen', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            messages: [
                { role: "system", content: "你是一个学术论文编辑助手。" },
                { role: "user", content: `请帮我润色：${text}` }
            ],
            question: `请帮我润色：${text}`,
            model_name: "Qwen3-8B"
        })
    });
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\\n\\n');
        
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const data = JSON.parse(line.slice(6));
                const content = data.choices?.[0]?.delta?.content || '';
                
                if (content) {
                    console.log(content);
                    // 实时更新UI
                    document.getElementById('output').innerText += content;
                }
            }
        }
    }
}
```

#### React Hook

```typescript
import { useState } from 'react';

export function useStreamPolish() {
    const [content, setContent] = useState('');
    const [loading, setLoading] = useState(false);
    
    const polish = async (text: string) => {
        setLoading(true);
        setContent('');
        
        try {
            const response = await fetch('http://localhost:8000/api/v1/stream/qwen', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    messages: [
                        { role: "system", content: "你是一个学术论文编辑助手。" },
                        { role: "user", content: `请帮我润色：${text}` }
                    ],
                    question: `请帮我润色：${text}`,
                    model_name: "Qwen3-8B"
                })
            });
            
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let fullContent = '';
            
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                const chunk = decoder.decode(value);
                const lines = chunk.split('\\n\\n');
                
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = JSON.parse(line.slice(6));
                        const text = data.choices?.[0]?.delta?.content || '';
                        
                        if (text) {
                            fullContent += text;
                            setContent(fullContent);
                        }
                    }
                }
            }
        } finally {
            setLoading(false);
        }
    };
    
    return { content, loading, polish };
}
```

## SSE响应格式

所有流式响应都采用以下格式：

```json
data: {
  "id": "chatcmpl-xxxxx",
  "object": "chat.completion.chunk",
  "created": 1234567890,
  "model": "qwen-plus",
  "choices": [
    {
      "delta": {
        "role": "assistant",
        "content": "响应内容",
        "question": "原始问题（可选）"
      },
      "index": 0,
      "finish_reason": null
    }
  ]
}

// 流式响应结束标记
data: {
  "id": "chatcmpl-xxxxx",
  "object": "chat.completion.chunk",
  "created": 1234567890,
  "model": "qwen-plus",
  "choices": [
    {
      "delta": {},
      "index": 0,
      "finish_reason": "stop"
    }
  ]
}

// 错误响应
data: {
  "id": "chatcmpl-xxxxx",
  "object": "chat.completion.chunk",
  "created": 1234567890,
  "model": "qwen-plus",
  "error": {
    "message": "错误信息",
    "type": "stream_error",
    "code": 500
  }
}
```

## 配置说明

### 本地模型配置

```python
from config import model
from app.services.stream_service import StreamService

stream_service = StreamService(logger=logger, model=model)
```

### Qwen/DeepSeek配置

```python
async for chunk in stream_service.stream(
    provider=StreamProvider.QWEN,
    messages=[...],
    api_url="http://localhost:8000/v1/chat/completions",  # 修改为实际API地址
    model_name="Qwen3-8B",
    temperature=0.1,
    top_p=0.95,
    max_tokens=1024
):
    pass
```

### OpenAI配置

```python
async for chunk in stream_service.stream(
    provider=StreamProvider.OPENAI,
    messages=[...],
    api_key="sk-xxxxx",  # 替换为实际的OpenAI密钥
    model_name="gpt-3.5-turbo",
    temperature=0.7,
    top_p=1.0,
    max_tokens=1024
):
    pass
```

## 错误处理

所有异常都会被捕获并以SSE格式返回：

```json
data: {
  "id": "chatcmpl-xxxxx",
  "object": "chat.completion.chunk",
  "created": 1234567890,
  "model": "qwen-plus",
  "error": {
    "message": "API请求超时",
    "type": "stream_error",
    "code": 504
  }
}
```

前端可以通过检查 `data.error` 字段来处理错误。

## 性能优化建议

1. **超时配置**: 远程API默认超时时间为300秒，可根据需要调整
2. **流缓冲**: 使用 `X-Accel-Buffering: no` 禁用Nginx缓冲
3. **并发控制**: 使用信号量限制并发请求数
4. **错误重试**: 前端应实现重试机制

## 测试

运行示例代码：

```bash
cd backend
python stream_examples.py
```

## 文件清单

- `app/services/stream_service.py` - 核心流式服务模块 (750+ 行)
- `app/api/stream.py` - API端点定义 (200+ 行)
- `stream_examples.py` - 使用示例和文档

## 常见问题

Q: 如何修改流式响应的模型名称？
A: 在API调用时传递 `model_name` 参数即可。

Q: 支持哪些提供商？
A: 支持LOCAL、QWEN、DEEPSEEK、OPENAI四种提供商。

Q: 流式响应支持中文吗？
A: 完全支持，所有JSON数据都使用 `ensure_ascii=False` 确保正确编码。

Q: 如何处理流式超时？
A: 捕获 `asyncio.TimeoutError` 异常，会自动返回504错误。

Q: 可以组合多个提供商吗？
A: 支持，可在一个应用中同时使用多个提供商的API。
"""


def save_integration_guide():
    """保存集成指南"""
    with open("STREAM_INTEGRATION_GUIDE.md", "w", encoding="utf-8") as f:
        f.write(INTEGRATION_GUIDE)
    print("✅ 集成指南已保存到 STREAM_INTEGRATION_GUIDE.md")


if __name__ == "__main__":
    save_integration_guide()
