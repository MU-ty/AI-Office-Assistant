
from typing import List, Dict, Any, AsyncGenerator
import json
import asyncio

from app.services.llm_service import llm_service
from app.services.search_service import search_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

class RAGService:
    """
    RAG (检索增强生成) 服务
    """

    def __init__(self):
        self.llm = llm_service
        self.search = search_service

    async def chat_stream(
        self, 
        query: str, 
        history: List[Dict[str, str]] = None,
        knowledge_base_ids: List[int] = None,
        top_k: int = 5
    ) -> AsyncGenerator[str, None]:
        """
        RAG 问答流
        
        Yields:
            JSON 字符串，格式如 SSE data: {"type": "token", "content": "..."}
        """
        try:
            # 1. 检索阶段
            logger.info(f"RAG Search: {query}, KBs: {knowledge_base_ids}")
            
            # 生成查询向量
            query_vector = await self.llm.get_embeddings(query)
            if not query_vector:
                # 降级为纯文本搜索 (暂未实现纯文本 RAG 检索接口，这里简单处理)
                logger.warning("向量生成失败，可能导致检索效果下降")
                query_vector = [0.0] * 1024 # 修正：占位向量维度改为 1024
                
            # 执行混合检索
            chunks = await self.search.search_hybrid(
                query_text=query,
                query_vector=query_vector,
                knowledge_base_ids=knowledge_base_ids,
                top_k=top_k
            )
            
            # 发送检索到的文档引用信息
            sources = []
            context_list = []
            
            for i, chunk in enumerate(chunks):
                # 记录来源
                meta = chunk.get("metadata", {})
                sources.append({
                    "id": chunk.get("doc_id"),
                    "title": meta.get("title", f"Document {chunk.get('doc_id')}"),
                    "score": chunk.get("score"),
                    "content_preview": chunk.get("content", "")[:100] + "..."
                })
                # 构建上下文
                context_list.append(f"文档 [{i+1}] (标题: {meta.get('title')}):\n{chunk.get('content')}\n")
            
            # 发送 sources 事件
            yield json.dumps({"type": "sources", "data": sources}, ensure_ascii=False)
            
            if not context_list:
                yield json.dumps({"type": "token", "content": "抱歉，在知识库中没有找到相关信息。"}, ensure_ascii=False)
                return

            context_text = "\n---\n".join(context_list)
            
            # 2. 生成阶段
            system_prompt = f"""你是一个智能办公助手。请基于以下提供的【参考文档】回答用户的问题。
            
要求：
1. 答案必须基于【参考文档】的内容。如果参考文档中没有相关信息，请直接回答"根据提供的文档，我无法找到相关信息"，不要编造。
2. 回答要准确、连贯、逻辑清晰。
3. 可以在回答中引用文档编号，如 [1], [2]。

【参考文档】：
{context_text}
"""
            
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # 添加历史对话 (最近 2-3 轮)
            if history:
                # 简单过滤，只保留 user 和 assistant 消息
                valid_history = [h for h in history if h.get("role") in ["user", "assistant"]]
                messages.extend(valid_history[-4:]) # 保留最近 4 条
            
            # 添加当前问题
            messages.append({"role": "user", "content": query})
            
            logger.info("开始调用 LLM 生成答案")
            response = await self.llm.chat(messages, stream=True)
            
            # 调试日志
            logger.info(f"LLM Response Type: {type(response)}")
            
            # 处理流式响应
            try:
                # 尝试异步迭代 (AsyncStream)
                async for chunk in response:
                    if hasattr(chunk, "choices") and chunk.choices:
                        delta = chunk.choices[0].delta
                        if hasattr(delta, "content") and delta.content:
                            yield json.dumps({"type": "token", "content": delta.content}, ensure_ascii=False)
            except TypeError:
                # 如果不是异步迭代器，尝试同步迭代 (以防万一)
                logger.warning("Response is not async iterable, trying sync iteration")
                try:
                    for chunk in response:
                        if hasattr(chunk, "choices") and chunk.choices:
                            delta = chunk.choices[0].delta
                            if hasattr(delta, "content") and delta.content:
                                yield json.dumps({"type": "token", "content": delta.content}, ensure_ascii=False)
                except Exception as e:
                    logger.error(f"Sync iteration failed: {e}")
                    raise e
            except Exception as e:
                logger.error(f"Async iteration failed: {e}")
                raise e

        except Exception as e:
            logger.error(f"RAG Chat Error: {e}")
            yield json.dumps({"type": "error", "content": str(e)}, ensure_ascii=False)

rag_service = RAGService()
