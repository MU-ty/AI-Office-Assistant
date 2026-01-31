"""
流式响应处理模块
支持本地模型和远程API的流式输出
兼容OpenAI流式响应格式
"""

import asyncio
import json
import time
import uuid
import aiohttp
import logging
from typing import AsyncGenerator, List, Tuple, Optional, Dict, Any
from enum import Enum


class StreamProvider(Enum):
    """流式提供商类型"""
    LOCAL = "local"           # 本地模型
    QWEN = "qwen"             # 通义千问
    DEEPSEEK = "deepseek"     # DeepSeek
    OPENAI = "openai"         # OpenAI


class StreamFormatter:
    """流式响应格式化器"""
    
    @staticmethod
    def format_chunk(
        chat_id: str,
        content: str,
        model: str = "qwen-plus",
        question: str = "",
        finish_reason: Optional[str] = None
    ) -> str:
        """
        将内容格式化为OpenAI兼容的SSE流式格式
        
        Args:
            chat_id: 对话ID
            content: 响应内容
            model: 模型名称
            question: 原始问题（用于扩展）
            finish_reason: 完成原因（stop/length等）
            
        Returns:
            格式化后的SSE数据行
        """
        data = {
            "id": chat_id,
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": model,
            "choices": [
                {
                    "delta": {
                        "role": "assistant",
                        "content": content,
                        **({"question": question} if question else {})
                    },
                    "index": 0,
                    "finish_reason": finish_reason
                }
            ]
        }
        # 使用ensure_ascii=False确保中文编码正确
        json_str = json.dumps(data, ensure_ascii=False, default=str)
        return f"data: {json_str}\n\n"
    
    @staticmethod
    def format_end(
        chat_id: str,
        model: str = "qwen-plus"
    ) -> str:
        """
        格式化流式响应结束标记
        
        Args:
            chat_id: 对话ID
            model: 模型名称
            
        Returns:
            格式化后的结束标记
        """
        end_data = {
            "id": chat_id,
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": model,
            "choices": [
                {
                    "delta": {},
                    "index": 0,
                    "finish_reason": "stop"
                }
            ]
        }
        json_str = json.dumps(end_data, ensure_ascii=False, default=str)
        return f"data: {json_str}\n\n"
    
    @staticmethod
    def format_error(
        chat_id: str,
        error_msg: str,
        code: int = 500,
        model: str = "qwen-plus"
    ) -> str:
        """
        格式化错误响应
        
        Args:
            chat_id: 对话ID
            error_msg: 错误消息
            code: 错误码
            model: 模型名称
            
        Returns:
            格式化后的错误数据
        """
        # 安全的编码处理
        safe_error = error_msg.encode('utf-8', errors='ignore').decode('utf-8')
        
        error_data = {
            "id": chat_id,
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": model,
            "error": {
                "message": safe_error,
                "type": "stream_error",
                "code": code
            }
        }
        json_str = json.dumps(error_data, ensure_ascii=False, default=str)
        return f"data: {json_str}\n\n"


class LocalModelStream:
    """本地模型流式处理器"""
    
    def __init__(self, model, logger: logging.Logger):
        """
        初始化本地模型流处理器
        
        Args:
            model: 本地模型实例
            logger: 日志对象
        """
        self.model = model
        self.logger = logger
    
    async def stream(
        self,
        messages: List[Dict[str, str]],
        question: str = "",
        model_name: str = "qwen-plus",
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        异步流式调用本地模型
        
        Args:
            messages: 对话消息列表
            question: 原始问题
            model_name: 模型名称
            **kwargs: 其他参数
            
        Yields:
            OpenAI格式的流式数据
        """
        chat_id = f"chatcmpl-{uuid.uuid4().hex}"
        full_content = ""
        
        try:
            # 调用本地模型的异步流接口
            async for chunk in self.model.astream(messages):
                await asyncio.sleep(0)  # 释放事件循环，允许并发处理
                
                content = chunk.content or ""
                full_content += content
                
                # 格式化并返回流式数据
                yield StreamFormatter.format_chunk(
                    chat_id=chat_id,
                    content=content,
                    model=model_name,
                    question=question
                )
            
            # 记录响应日志（避免编码问题）
            self.logger.debug(f"模型响应长度: {len(full_content)} 字符")
            
            # 返回结束标记
            yield StreamFormatter.format_end(chat_id=chat_id, model=model_name)
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"本地模型流式调用异常: {error_msg}")
            yield StreamFormatter.format_error(
                chat_id=chat_id,
                error_msg=error_msg,
                model=model_name
            )


class RemoteAPIStream:
    """远程API流式处理器"""
    
    def __init__(self, logger: logging.Logger):
        """
        初始化远程API流处理器
        
        Args:
            logger: 日志对象
        """
        self.logger = logger
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def stream_qwen(
        self,
        messages: List[Dict[str, str]],
        api_url: str = "http://localhost:8000/v1/chat/completions",
        api_key: Optional[str] = None,
        question: str = "",
        model_name: str = "Qwen3-8B",
        temperature: float = 0.1,
        top_p: float = 0.95,
        max_tokens: int = 1024,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        异步流式调用Qwen模型API
        
        Args:
            messages: 对话消息列表
            api_url: API地址
            question: 原始问题
            model_name: 模型名称
            temperature: 温度参数
            top_p: top_p参数
            max_tokens: 最大令牌数
            **kwargs: 其他参数
            
        Yields:
            OpenAI格式的流式数据
        """
        chat_id = f"chatcmpl-{uuid.uuid4().hex}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        }

        # DashScope compatible-mode / OpenAI-compatible endpoints require Bearer auth.
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        else:
            # Without a key, Qwen-compatible streaming will fail; return a structured error.
            error_msg = "QWEN_API_KEY 未配置，无法进行流式调用"
            self.logger.error(error_msg)
            yield StreamFormatter.format_error(
                chat_id=chat_id,
                error_msg=error_msg,
                code=401,
                model=model_name,
            )
            return
        
        payload = {
            "model": model_name,
            "messages": messages,
            "stream": True,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            **kwargs
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    api_url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=300)
                ) as resp:
                    
                    if resp.status != 200:
                        error_msg = f"API请求失败，状态码: {resp.status}"
                        self.logger.error(error_msg)
                        yield StreamFormatter.format_error(
                            chat_id=chat_id,
                            error_msg=error_msg,
                            code=resp.status,
                            model=model_name
                        )
                        return
                    
                    # 逐行读取流式响应
                    async for line in resp.content:
                        if line:
                            line_str = line.decode("utf-8", errors='ignore')
                            
                            # 处理SSE格式数据
                            if line_str.startswith("data: "):
                                try:
                                    json_data = json.loads(line_str[6:])
                                    
                                    # 提取内容并格式化
                                    if "choices" in json_data and len(json_data["choices"]) > 0:
                                        delta = json_data["choices"][0].get("delta", {})
                                        content = delta.get("content", "")
                                        
                                        yield StreamFormatter.format_chunk(
                                            chat_id=chat_id,
                                            content=content,
                                            model=model_name,
                                            question=question
                                        )
                                except json.JSONDecodeError:
                                    continue
                    
                    # 返回结束标记
                    yield StreamFormatter.format_end(chat_id=chat_id, model=model_name)
        
        except asyncio.TimeoutError:
            error_msg = "API请求超时"
            self.logger.error(error_msg)
            yield StreamFormatter.format_error(
                chat_id=chat_id,
                error_msg=error_msg,
                code=504,
                model=model_name
            )
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Qwen API流式调用异常: {error_msg}")
            yield StreamFormatter.format_error(
                chat_id=chat_id,
                error_msg=error_msg,
                model=model_name
            )
    
    async def stream_deepseek(
        self,
        messages: List[Dict[str, str]],
        api_url: str = "http://localhost:8000/v1/chat/completions",
        question: str = "",
        model_name: str = "DeepSeek-32B",
        temperature: float = 0.1,
        top_p: float = 0.95,
        max_tokens: int = 1024,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        异步流式调用DeepSeek模型API（与Qwen兼容）
        
        Args:
            messages: 对话消息列表
            api_url: API地址
            question: 原始问题
            model_name: 模型名称
            temperature: 温度参数
            top_p: top_p参数
            max_tokens: 最大令牌数
            **kwargs: 其他参数
            
        Yields:
            OpenAI格式的流式数据
        """
        # DeepSeek API与Qwen兼容，使用相同的实现
        async for chunk in self.stream_qwen(
            messages=messages,
            api_url=api_url,
            question=question,
            model_name=model_name,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            **kwargs
        ):
            yield chunk
    
    async def stream_openai(
        self,
        messages: List[Dict[str, str]],
        api_key: str,
        question: str = "",
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        top_p: float = 1.0,
        max_tokens: int = 1024,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        异步流式调用OpenAI API
        
        Args:
            messages: 对话消息列表
            api_key: OpenAI API密钥
            question: 原始问题
            model_name: 模型名称
            temperature: 温度参数
            top_p: top_p参数
            max_tokens: 最大令牌数
            **kwargs: 其他参数
            
        Yields:
            OpenAI格式的流式数据
        """
        chat_id = f"chatcmpl-{uuid.uuid4().hex}"
        api_url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": model_name,
            "messages": messages,
            "stream": True,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            **kwargs
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    api_url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=300)
                ) as resp:
                    
                    if resp.status != 200:
                        error_text = await resp.text()
                        error_msg = f"OpenAI API请求失败: {error_text[:200]}"
                        self.logger.error(error_msg)
                        yield StreamFormatter.format_error(
                            chat_id=chat_id,
                            error_msg=error_msg,
                            code=resp.status,
                            model=model_name
                        )
                        return
                    
                    async for line in resp.content:
                        if line:
                            line_str = line.decode("utf-8", errors='ignore').strip()
                            
                            if line_str.startswith("data: "):
                                data_str = line_str[6:]
                                
                                if data_str == "[DONE]":
                                    yield StreamFormatter.format_end(
                                        chat_id=chat_id,
                                        model=model_name
                                    )
                                    break
                                
                                try:
                                    json_data = json.loads(data_str)
                                    
                                    if "choices" in json_data and len(json_data["choices"]) > 0:
                                        delta = json_data["choices"][0].get("delta", {})
                                        content = delta.get("content", "")
                                        
                                        yield StreamFormatter.format_chunk(
                                            chat_id=chat_id,
                                            content=content,
                                            model=model_name,
                                            question=question
                                        )
                                except json.JSONDecodeError:
                                    continue
        
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"OpenAI流式调用异常: {error_msg}")
            yield StreamFormatter.format_error(
                chat_id=chat_id,
                error_msg=error_msg,
                model=model_name
            )


class StreamService:
    """统一的流式服务接口"""
    
    def __init__(self, logger: logging.Logger, model=None):
        """
        初始化流式服务
        
        Args:
            logger: 日志对象
            model: 本地模型实例（可选）
        """
        self.logger = logger
        self.model = model
        self.local_stream = LocalModelStream(model, logger) if model else None
        self.remote_stream = RemoteAPIStream(logger)
    
    async def stream(
        self,
        provider: StreamProvider,
        messages: List[Dict[str, str]],
        question: str = "",
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        统一的流式接口
        
        Args:
            provider: 流式提供商
            messages: 对话消息列表
            question: 原始问题
            **kwargs: 其他参数（如model_name, api_url等）
            
        Yields:
            OpenAI格式的流式数据
            
        Raises:
            ValueError: 不支持的提供商或缺少必要参数
        """
        if provider == StreamProvider.LOCAL:
            if not self.local_stream:
                raise ValueError("本地模型未初始化")
            async for chunk in self.local_stream.stream(
                messages=messages,
                question=question,
                **kwargs
            ):
                yield chunk
        
        elif provider == StreamProvider.QWEN:
            async for chunk in self.remote_stream.stream_qwen(
                messages=messages,
                question=question,
                **kwargs
            ):
                yield chunk
        
        elif provider == StreamProvider.DEEPSEEK:
            async for chunk in self.remote_stream.stream_deepseek(
                messages=messages,
                question=question,
                **kwargs
            ):
                yield chunk
        
        elif provider == StreamProvider.OPENAI:
            async for chunk in self.remote_stream.stream_openai(
                messages=messages,
                question=question,
                **kwargs
            ):
                yield chunk
        
        else:
            raise ValueError(f"不支持的流式提供商: {provider}")
