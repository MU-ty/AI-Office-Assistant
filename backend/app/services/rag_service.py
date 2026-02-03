
from typing import List, Dict, Any, Optional
from app.services.weknora_service import weknora_service
from app.services.llm_service import llm_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

class RAGService:
    """
    RAG (检索增强生成) 服务
    整合 WeKnora 的检索能力和 LLM 的生成能力
    """

    def __init__(self):
        self.weknora = weknora_service
        self.llm = llm_service
        # 简单对话历史存储 {session_id: [messages]}
        # 注意：实际生产环境应使用 Redis 或 数据库存储
        self.history = {}

    async def answer_with_knowledge(
        self, 
        query: str, 
        knowledge_base_ids: List[str],
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        基于知识库内容回答问题，支持多轮对话
        """
        logger.info(f"开始 RAG 问答 (Session: {session_id}): {query}")

        # 1. 从 WeKnora 检索相关上下文
        retrieval_results = await self.weknora.knowledge_search(query, knowledge_base_ids)
        
        # 2. 提取并格式化上下文
        context = ""
        if isinstance(retrieval_results, list):
            for i, item in enumerate(retrieval_results):
                content = item.get("content", "")
                source = item.get("source", "未知来源")
                context += f"资料[{i+1}] (来源: {source}):\n{content}\n\n"
        
        # 3. 构造系统 Prompt
        system_prompt = f"""你是一个智能办公助手。请根据提供的资料回答用户的问题。
如果资料中没有相关内容，请告知用户你无法根据现有资料回答。
请保持回答的专业性、准确性和简洁性。

参考资料：
{context}
"""
        
        # 4. 获取历史对话记录
        messages = []
        if session_id:
            # 如果是该会话的第一条消息，添加系统提示词
            if session_id not in self.history:
                self.history[session_id] = []
            
            # 获取历史（限制最近 10 轮对话以防 token 超限）
            history_messages = self.history[session_id][-10:]
            messages.extend(history_messages)

        # 添加当前问题
        messages.append({"role": "user", "content": query})

        # 5. 调用 LLM 生成回答
        if self.llm.check_availability():
            from openai import OpenAI
            client = self.llm.client
            
            # 在消息列表最前面插入系统提示词（包含最新的 RAG 上下文）
            full_messages = [{"role": "system", "content": system_prompt}] + messages
            
            response = client.chat.completions.create(
                model=self.llm.model,
                messages=full_messages,
                temperature=0.3
            )
            answer = response.choices[0].message.content
            
            # 6. 更新历史记录
            if session_id:
                self.history[session_id].append({"role": "user", "content": query})
                self.history[session_id].append({"role": "assistant", "content": answer})
                # 限制历史长度
                if len(self.history[session_id]) > 20:
                    self.history[session_id] = self.history[session_id][-20:]

            return {
                "answer": answer,
                "sources": retrieval_results,
                "session_id": session_id
            }
        else:
            return {
                "answer": "LLM 服务暂不可用",
                "sources": retrieval_results,
                "session_id": session_id
            }

# 全局单例
rag_service = RAGService()
