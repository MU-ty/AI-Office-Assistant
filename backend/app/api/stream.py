"""
流式API端点示例
演示如何在FastAPI中使用流式服务
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
import logging

from app.services.stream_service import StreamService, StreamProvider
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/stream", tags=["流式接口"])


@router.post("/local")
async def stream_local(
    messages: list,
    question: str = Query("", description="原始问题"),
    model_name: str = Query("qwen-plus", description="模型名称"),
):
    """
    本地模型流式响应端点
    
    Args:
        messages: 对话消息列表 [{"role": "user", "content": "..."}]
        question: 原始问题
        model_name: 模型名称
        
    Returns:
        StreamingResponse: OpenAI格式的SSE流式数据
    """
    try:
        # 假设在main.py中注入了stream_service
        stream_service = StreamService(logger=logger)
        
        return StreamingResponse(
            stream_service.stream(
                provider=StreamProvider.LOCAL,
                messages=messages,
                question=question,
                model_name=model_name
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive"
            }
        )
    except Exception as e:
        logger.error(f"本地流式请求异常: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/qwen")
async def stream_qwen(
    messages: list,
    question: str = Query("", description="原始问题"),
    api_url: str = Query("http://localhost:8000/v1/chat/completions", description="API地址"),
    model_name: str = Query("Qwen3-8B", description="模型名称"),
    temperature: float = Query(0.1, description="温度参数"),
    top_p: float = Query(0.95, description="top_p参数"),
    max_tokens: int = Query(1024, description="最大令牌数"),
):
    """
    Qwen模型API流式响应端点
    
    Args:
        messages: 对话消息列表
        question: 原始问题
        api_url: Qwen API地址
        model_name: 模型名称
        temperature: 温度参数
        top_p: top_p参数
        max_tokens: 最大令牌数
        
    Returns:
        StreamingResponse: OpenAI格式的SSE流式数据
    """
    try:
        stream_service = StreamService(logger=logger)
        
        return StreamingResponse(
            stream_service.stream(
                provider=StreamProvider.QWEN,
                messages=messages,
                question=question,
                api_url=api_url,
                model_name=model_name,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive"
            }
        )
    except Exception as e:
        logger.error(f"Qwen流式请求异常: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/deepseek")
async def stream_deepseek(
    messages: list,
    question: str = Query("", description="原始问题"),
    api_url: str = Query("http://localhost:8000/v1/chat/completions", description="API地址"),
    model_name: str = Query("DeepSeek-32B", description="模型名称"),
    temperature: float = Query(0.1, description="温度参数"),
    top_p: float = Query(0.95, description="top_p参数"),
    max_tokens: int = Query(1024, description="最大令牌数"),
):
    """
    DeepSeek模型API流式响应端点
    
    Args:
        messages: 对话消息列表
        question: 原始问题
        api_url: DeepSeek API地址
        model_name: 模型名称
        temperature: 温度参数
        top_p: top_p参数
        max_tokens: 最大令牌数
        
    Returns:
        StreamingResponse: OpenAI格式的SSE流式数据
    """
    try:
        stream_service = StreamService(logger=logger)
        
        return StreamingResponse(
            stream_service.stream(
                provider=StreamProvider.DEEPSEEK,
                messages=messages,
                question=question,
                api_url=api_url,
                model_name=model_name,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive"
            }
        )
    except Exception as e:
        logger.error(f"DeepSeek流式请求异常: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/openai")
async def stream_openai(
    messages: list,
    api_key: str = Query(..., description="OpenAI API密钥"),
    question: str = Query("", description="原始问题"),
    model_name: str = Query("gpt-3.5-turbo", description="模型名称"),
    temperature: float = Query(0.7, description="温度参数"),
    top_p: float = Query(1.0, description="top_p参数"),
    max_tokens: int = Query(1024, description="最大令牌数"),
):
    """
    OpenAI模型流式响应端点
    
    Args:
        messages: 对话消息列表
        api_key: OpenAI API密钥
        question: 原始问题
        model_name: 模型名称
        temperature: 温度参数
        top_p: top_p参数
        max_tokens: 最大令牌数
        
    Returns:
        StreamingResponse: OpenAI格式的SSE流式数据
    """
    try:
        stream_service = StreamService(logger=logger)
        
        return StreamingResponse(
            stream_service.stream(
                provider=StreamProvider.OPENAI,
                messages=messages,
                api_key=api_key,
                question=question,
                model_name=model_name,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive"
            }
        )
    except Exception as e:
        logger.error(f"OpenAI流式请求异常: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
