"""LLM服务接入层"""

import json
from typing import List, Optional, Dict, Any, Union
import dashscope
from dashscope import Generation
from openai import OpenAI
from ..core.config import get_settings

settings = get_settings()

class LLMService:
    """LLM服务类，支持通义千问(Qwen)和OpenAI"""
    
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        if self.provider == "qwen":
            dashscope.api_key = settings.QWEN_API_KEY
        elif self.provider == "openai":
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            
    async def chat(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> Union[str, Any]:
        """通用对话接口"""
        if self.provider == "qwen":
            return await self._chat_qwen(messages, model, temperature, max_tokens, stream)
        elif self.provider == "openai":
            return await self._chat_openai(messages, model, temperature, max_tokens, stream)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    async def _chat_qwen(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> str:
        """通义千问API调用"""
        model_name = model or settings.QWEN_MODEL
        
        # 转换格式，Qwen使用 messages 列表
        response = Generation.call(
            model=model_name,
            messages=messages,
            result_format='message',
            temperature=temperature,
            max_tokens=max_tokens,
            incremental_output=stream
        )
        
        if response.status_code == 200:
            return response.output.choices[0].message.content
        else:
            error_msg = f"Qwen API Error: {response.code} - {response.message}"
            print(error_msg)
            raise Exception(error_msg)

    async def _chat_openai(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> str:
        """OpenAI API调用"""
        model_name = model or "gpt-3.5-turbo"
        
        response = self.client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream
        )
        
        if stream:
            return response
        return response.choices[0].message.content

    def generate_prompt(self, template: str, **kwargs) -> str:
        """从模板生成提示词"""
        return template.format(**kwargs)

# 单例模式
llm_service = LLMService()
