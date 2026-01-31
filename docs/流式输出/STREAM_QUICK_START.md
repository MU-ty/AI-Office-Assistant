# 流式处理服务 - 快速开始指南

## 5分钟快速上手

### 1. 基本配置

在 `backend/app/main.py` 中添加流式API路由：

```python
from fastapi import FastAPI
from app.api import stream

app = FastAPI()

# 注册流式API路由
app.include_router(stream.router)
```

### 2. 启动服务

```bash
cd backend
python -m uvicorn app.main:app --reload
```

### 3. 调用API

#### 使用curl测试

```bash
curl -X POST http://localhost:8000/api/v1/stream/qwen \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "system", "content": "你是一个学术论文编辑助手。"},
      {"role": "user", "content": "请帮我润色：这个研究很重要。"}
    ],
    "question": "请帮我润色：这个研究很重要。",
    "api_url": "http://localhost:8000/v1/chat/completions",
    "model_name": "Qwen3-8B"
  }'
```

#### 使用Python异步客户端

```python
import asyncio
import aiohttp

async def test_stream():
    url = "http://localhost:8000/api/v1/stream/qwen"
    payload = {
        "messages": [
            {"role": "system", "content": "你是一个学术论文编辑助手。"},
            {"role": "user", "content": "请帮我润色：这个研究很重要。"}
        ],
        "question": "请帮我润色：这个研究很重要。",
        "api_url": "http://localhost:8000/v1/chat/completions",
        "model_name": "Qwen3-8B"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            async for line in resp.content:
                print(line.decode("utf-8"), end="")

asyncio.run(test_stream())
```

#### 使用JavaScript (浏览器)

```javascript
async function streamPolish() {
    const response = await fetch('http://localhost:8000/api/v1/stream/qwen', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            messages: [
                { role: "system", content: "你是一个学术论文编辑助手。" },
                { role: "user", content: "请帮我润色：这个研究很重要。" }
            ],
            question: "请帮我润色：这个研究很重要。",
            api_url: "http://localhost:8000/v1/chat/completions",
            model_name: "Qwen3-8B"
        })
    });
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const text = decoder.decode(value);
        const lines = text.split('\n\n');
        
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const data = JSON.parse(line.slice(6));
                const content = data.choices?.[0]?.delta?.content || '';
                if (content) {
                    process.stdout.write(content);
                }
            }
        }
    }
}

streamPolish();
```

## 支持的提供商

| 提供商 | 端点 | 需要参数 | 用途 |
|--------|------|--------|------|
| Local | `/api/v1/stream/local` | model_name | 本地模型 |
| Qwen | `/api/v1/stream/qwen` | api_url, model_name | 通义千问 |
| DeepSeek | `/api/v1/stream/deepseek` | api_url, model_name | DeepSeek |
| OpenAI | `/api/v1/stream/openai` | api_key, model_name | OpenAI |

## 请求参数

### 通用参数

| 参数 | 类型 | 必需 | 说明 |
|-----|------|------|------|
| messages | array | ✓ | 对话消息列表 |
| question | string | | 原始问题 |

### Qwen/DeepSeek特定参数

| 参数 | 类型 | 默认值 | 说明 |
|-----|------|--------|------|
| api_url | string | http://localhost:8000/v1/chat/completions | API地址 |
| model_name | string | Qwen3-8B | 模型名称 |
| temperature | float | 0.1 | 温度参数 (0-2) |
| top_p | float | 0.95 | top_p参数 (0-1) |
| max_tokens | int | 1024 | 最大令牌数 |

### OpenAI特定参数

| 参数 | 类型 | 默认值 | 说明 |
|-----|------|--------|------|
| api_key | string | | OpenAI API密钥 |
| model_name | string | gpt-3.5-turbo | 模型名称 |
| temperature | float | 0.7 | 温度参数 |
| top_p | float | 1.0 | top_p参数 |
| max_tokens | int | 1024 | 最大令牌数 |

## 响应格式

所有流式响应都采用SSE (Server-Sent Events) 格式：

```
data: {"id":"chatcmpl-xxx","object":"chat.completion.chunk","created":1234567890,"model":"qwen-plus","choices":[{"delta":{"role":"assistant","content":"响应内容"},"index":0,"finish_reason":null}]}

data: {"id":"chatcmpl-xxx","object":"chat.completion.chunk","created":1234567890,"model":"qwen-plus","choices":[{"delta":{},"index":0,"finish_reason":"stop"}]}
```

## 集成示例

### 在FastAPI中使用

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from app.services.stream_service import StreamService, StreamProvider

app = FastAPI()
stream_service = StreamService(logger=logger)

@app.post("/polish/stream")
async def polish_stream(text: str):
    messages = [
        {"role": "system", "content": "你是一个学术论文编辑助手。"},
        {"role": "user", "content": f"请帮我润色：{text}"}
    ]
    
    return StreamingResponse(
        stream_service.stream(
            provider=StreamProvider.QWEN,
            messages=messages,
            question=f"请帮我润色：{text}",
            api_url="http://localhost:8000/v1/chat/completions",
            model_name="Qwen3-8B"
        ),
        media_type="text/event-stream"
    )
```

### 在React中使用

```tsx
import { useState } from 'react';

export function PolishComponent() {
    const [content, setContent] = useState('');
    const [loading, setLoading] = useState(false);
    
    const handlePolish = async (text: string) => {
        setLoading(true);
        setContent('');
        
        const response = await fetch('/api/v1/stream/qwen', {
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
        let fullText = '';
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value);
            const lines = chunk.split('\n\n');
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = JSON.parse(line.slice(6));
                    const text = data.choices?.[0]?.delta?.content || '';
                    if (text) {
                        fullText += text;
                        setContent(fullText);
                    }
                }
            }
        }
        
        setLoading(false);
    };
    
    return (
        <div>
            <textarea 
                placeholder="输入要润色的文本" 
                id="input"
            />
            <button 
                onClick={() => handlePolish(document.getElementById('input').value)}
                disabled={loading}
            >
                {loading ? '流式处理中...' : '开始润色'}
            </button>
            <div style={{ whiteSpace: 'pre-wrap' }}>
                {content}
            </div>
        </div>
    );
}
```

## 故障排除

### 问题：连接拒绝

**解决方案**: 确保后端服务已启动
```bash
python -m uvicorn app.main:app --reload
```

### 问题：API超时

**解决方案**: 增加超时时间或检查API地址
```python
# 在stream_service.py中修改
timeout=aiohttp.ClientTimeout(total=600)  # 增加至600秒
```

### 问题：中文乱码

**解决方案**: 所有JSON已配置 `ensure_ascii=False`，但客户端需要设置正确的编码
```python
decoder = new TextDecoder('utf-8')  # JavaScript
```

### 问题：CORS错误

**解决方案**: 在main.py中添加CORS中间件
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 文件位置

- 核心服务: `backend/app/services/stream_service.py`
- API端点: `backend/app/api/stream.py`
- 使用示例: `backend/stream_examples.py`
- 完整文档: `STREAM_INTEGRATION_GUIDE.md`

## 下一步

1. ✅ 启动服务
2. ✅ 测试API端点
3. ✅ 集成到你的应用中
4. ✅ 参考完整文档了解高级特性

## 支持

如有问题，参考完整集成指南: `STREAM_INTEGRATION_GUIDE.md`
