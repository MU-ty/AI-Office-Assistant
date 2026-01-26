"""
流式处理服务使用指南和客户端示例
"""

import asyncio
import aiohttp
import json
from typing import AsyncGenerator

# ============================================================================
# 1. 直接使用StreamService（后端服务间通信）
# ============================================================================

async def example_direct_usage():
    """
    直接在后端服务中使用StreamService的示例
    """
    from app.services.stream_service import StreamService, StreamProvider
    import logging
    
    logger = logging.getLogger(__name__)
    
    # 初始化流式服务（假设已配置本地模型）
    stream_service = StreamService(logger=logger, model=None)
    
    # 构造消息
    messages = [
        {"role": "system", "content": "你是一个学术论文编辑助手。"},
        {"role": "user", "content": "请帮我润色以下句子：这个研究很重要。"}
    ]
    
    # 流式获取响应
    print("=== 直接使用示例 ===")
    async for chunk in stream_service.stream(
        provider=StreamProvider.QWEN,
        messages=messages,
        question="请帮我润色以下句子：这个研究很重要。",
        api_url="http://localhost:8000/v1/chat/completions",
        model_name="Qwen3-8B"
    ):
        print(chunk, end="")


# ============================================================================
# 2. HTTP客户端使用（前端调用API）
# ============================================================================

async def example_http_client():
    """
    通过HTTP API调用流式接口的客户端示例
    """
    
    async def stream_from_api(
        api_url: str,
        messages: list,
        question: str = "",
        provider: str = "qwen",
        **params
    ) -> AsyncGenerator[str, None]:
        """
        调用流式API并获取SSE格式的流式数据
        
        Args:
            api_url: API基础URL
            messages: 对话消息
            question: 原始问题
            provider: 提供商 (local/qwen/deepseek/openai)
            **params: 其他参数
            
        Yields:
            SSE格式的数据行
        """
        url = f"{api_url}/api/v1/stream/{provider}"
        headers = {"Content-Type": "application/json"}
        
        payload = {
            "messages": messages,
            "question": question,
            **params
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                async for line in resp.content:
                    if line:
                        yield line.decode("utf-8")
    
    # 使用示例
    print("\n=== HTTP客户端示例 ===")
    
    messages = [
        {"role": "system", "content": "你是一个学术论文编辑助手。"},
        {"role": "user", "content": "请帮我润色以下句子：这个研究很重要。"}
    ]
    
    async for chunk in stream_from_api(
        api_url="http://localhost:8000",
        messages=messages,
        question="请帮我润色以下句子：这个研究很重要。",
        provider="qwen",
        model_name="Qwen3-8B",
        temperature=0.1,
        max_tokens=1024
    ):
        print(chunk, end="")


# ============================================================================
# 3. 解析SSE流式响应
# ============================================================================

async def parse_sse_stream(stream_line: str) -> dict:
    """
    解析SSE格式的流式数据行
    
    Args:
        stream_line: SSE格式的数据行 "data: {...}\n\n"
        
    Returns:
        解析后的JSON数据或None
    """
    if stream_line.startswith("data: "):
        try:
            json_str = stream_line[6:].strip()
            if json_str:
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    return None


async def example_parse_sse():
    """
    解析SSE流式响应的示例
    """
    print("\n=== SSE解析示例 ===")
    
    # 模拟从API接收的SSE流
    sse_lines = [
        'data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1234567890,"model":"qwen-plus","choices":[{"delta":{"role":"assistant","content":"这"},"index":0,"finish_reason":null}]}\n\n',
        'data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1234567890,"model":"qwen-plus","choices":[{"delta":{"role":"assistant","content":"个","question":""},"index":0,"finish_reason":null}]}\n\n',
        'data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1234567890,"model":"qwen-plus","choices":[{"delta":{},"index":0,"finish_reason":"stop"}]}\n\n'
    ]
    
    full_content = ""
    for line in sse_lines:
        data = await parse_sse_stream(line)
        if data and "choices" in data:
            content = data["choices"][0].get("delta", {}).get("content", "")
            full_content += content
            print(f"接收内容: {content}")
    
    print(f"完整响应: {full_content}")


# ============================================================================
# 4. 前端JavaScript示例
# ============================================================================

JAVASCRIPT_EXAMPLE = """
// 前端JavaScript使用SSE流式接口示例

// 基础的流式请求函数
async function streamCompletion(provider, messages, question, options = {}) {
    const url = `http://localhost:8000/api/v1/stream/${provider}`;
    
    const payload = {
        messages: messages,
        question: question,
        ...options
    };
    
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            throw new Error(`API错误: ${response.status}`);
        }
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let result = '';
        
        while (true) {
            const { done, value } = await reader.read();
            
            if (done) break;
            
            const chunk = decoder.decode(value);
            const lines = chunk.split('\\n\\n');
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.slice(6));
                        const content = data.choices?.[0]?.delta?.content || '';
                        
                        if (content) {
                            result += content;
                            // 实时更新UI
                            console.log('接收内容:', content);
                            // document.getElementById('output').innerText += content;
                        }
                        
                        // 检查是否完成
                        if (data.choices?.[0]?.finish_reason === 'stop') {
                            console.log('流式响应完成');
                        }
                        
                        // 检查是否出错
                        if (data.error) {
                            console.error('流式错误:', data.error);
                        }
                    } catch (e) {
                        console.error('JSON解析失败:', e);
                    }
                }
            }
        }
        
        return result;
    } catch (error) {
        console.error('流式请求异常:', error);
        throw error;
    }
}

// 使用示例
(async function() {
    const messages = [
        { role: "system", content: "你是一个学术论文编辑助手。" },
        { role: "user", content: "请帮我润色以下句子：这个研究很重要。" }
    ];
    
    const result = await streamCompletion('qwen', messages, 
        "请帮我润色以下句子：这个研究很重要。",
        {
            model_name: "Qwen3-8B",
            temperature: 0.1,
            max_tokens: 1024
        }
    );
    
    console.log('最终结果:', result);
})();
"""


# ============================================================================
# 5. React Hook示例
# ============================================================================

REACT_HOOK_EXAMPLE = """
import { useState, useCallback } from 'react';

export function useStreamCompletion() {
    const [content, setContent] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    
    const stream = useCallback(async (provider, messages, question, options = {}) => {
        setLoading(true);
        setContent('');
        setError(null);
        
        try {
            const url = `http://localhost:8000/api/v1/stream/${provider}`;
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ messages, question, ...options })
            });
            
            if (!response.ok) throw new Error(`API错误: ${response.status}`);
            
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
                        try {
                            const data = JSON.parse(line.slice(6));
                            const text = data.choices?.[0]?.delta?.content || '';
                            
                            if (text) {
                                fullContent += text;
                                setContent(fullContent);
                            }
                        } catch {}
                    }
                }
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, []);
    
    return { content, loading, error, stream };
}

// 使用示例
export function StreamExample() {
    const { content, loading, error, stream } = useStreamCompletion();
    
    const handleStream = async () => {
        await stream('qwen', 
            [{ role: "user", content: "帮我润色这句话" }],
            "帮我润色这句话",
            { model_name: "Qwen3-8B" }
        );
    };
    
    return (
        <div>
            <button onClick={handleStream} disabled={loading}>
                {loading ? '流式中...' : '开始流式'}
            </button>
            {error && <div style={{ color: 'red' }}>{error}</div>}
            <div style={{ whiteSpace: 'pre-wrap' }}>{content}</div>
        </div>
    );
}
"""


def print_guides():
    """打印所有使用指南"""
    print("\n" + "="*80)
    print("流式处理服务 - 完整使用指南")
    print("="*80)
    
    print("\n【JavaScript客户端示例】")
    print(JAVASCRIPT_EXAMPLE)
    
    print("\n【React Hook示例】")
    print(REACT_HOOK_EXAMPLE)
    
    print("\n" + "="*80)
    print("API端点说明")
    print("="*80)
    print("""
POST /api/v1/stream/local
  说明: 本地模型流式响应
  参数: messages (必需), question, model_name
  
POST /api/v1/stream/qwen
  说明: Qwen模型API流式响应
  参数: messages (必需), question, api_url, model_name, temperature, top_p, max_tokens
  
POST /api/v1/stream/deepseek
  说明: DeepSeek模型API流式响应
  参数: messages (必需), question, api_url, model_name, temperature, top_p, max_tokens
  
POST /api/v1/stream/openai
  说明: OpenAI模型流式响应
  参数: messages (必需), api_key (必需), question, model_name, temperature, top_p, max_tokens
  
返回: text/event-stream (SSE格式)
""")


async def main():
    """运行所有示例"""
    print_guides()
    
    # 注意：以下示例需要实际的模型和API配置才能运行
    # await example_parse_sse()
    # await example_direct_usage()
    # await example_http_client()


if __name__ == "__main__":
    asyncio.run(main())
