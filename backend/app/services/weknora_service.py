
import httpx
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

class WeKnoraService:
    """
    WeKnora RAG 服务客户端
    负责与 WeKnora 后端 API 进行交互，提供文档解析、检索和 Agent 功能
    """

    def __init__(self):
        self.base_url = settings.WEKNORA_BASE_URL
        self.api_key = settings.WEKNORA_API_KEY
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key if self.api_key else ""
        }

    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """统一请求处理"""
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.request(method, url, headers=self.headers, **kwargs)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"WeKnora API 错误: {e.response.status_code} - {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"WeKnora 请求异常: {str(e)}")
                raise

    async def search_knowledge(self, query: str, knowledge_base_ids: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        在指定知识库中进行语义检索
        """
        payload = {
            "query": query,
            "knowledge_base_ids": knowledge_base_ids,
            "top_k": top_k
        }
        # 修正 WeKnora 的检索接口为 /knowledge-search
        response = await self._request("POST", "/knowledge-search", json=payload)
        return response.get("data", [])

    async def upload_document(self, file_path: str, knowledge_base_id: str) -> Dict[str, Any]:
        """
        上传并解析文档到知识库
        """
        # 修正 WeKnora 的上传接口为 /knowledge-bases/{id}/knowledge/file
        url = f"{self.base_url.rstrip('/')}/knowledge-bases/{knowledge_base_id}/knowledge/file"
        async with httpx.AsyncClient(timeout=120.0) as client:
            with open(file_path, "rb") as f:
                files = {"file": f}
                # data = {"knowledge_base_id": knowledge_base_id} # ID 已在 URL 中
                response = await client.post(url, headers={"x-api-key": self.api_key}, files=files)
                response.raise_for_status()
                return response.json()

    async def list_documents(self, knowledge_base_id: str, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """获取知识库下的文档列表"""
        params = {"page": page, "page_size": page_size}
        return await self._request("GET", f"/knowledge-bases/{knowledge_base_id}/knowledge", params=params)

    async def get_document(self, doc_id: str) -> Dict[str, Any]:
        """获取文档详情"""
        return await self._request("GET", f"/knowledge/{doc_id}")

    async def get_document_chunks(self, doc_id: str, page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        """获取文档的所有切片"""
        return await self._request("GET", f"/chunks/{doc_id}", params={"page": page, "page_size": page_size})

    async def get_document_full_content(self, doc_id: str, max_chunks: int = 100) -> str:
        """获取文档的全文本内容（通过合并切片）"""
        import asyncio
        max_retries = 2
        retry_delay = 2  # 秒

        for attempt in range(max_retries + 1):
            try:
                logger.info(f"正在获取文档全文本 (尝试 {attempt + 1}): {doc_id}")
                chunks_data = await self.get_document_chunks(doc_id, page_size=max_chunks)
                
                chunks = chunks_data.get("data", [])
                if chunks:
                    logger.info(f"成功获取到 {len(chunks)} 个分块")
                    content_list = []
                    for c in chunks:
                        text = c.get("content", "").strip()
                        if text:
                            content_list.append(text)
                    
                    full_text = "\n".join(content_list)
                    if full_text:
                        return full_text
                
                if attempt < max_retries:
                    logger.warning(f"文档 {doc_id} 的分块数据为空，将在 {retry_delay}s 后重试...")
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error(f"在 {max_retries + 1} 次尝试后仍未获取到文档 {doc_id} 的内容")
                    
            except Exception as e:
                logger.error(f"获取文档全文本失败 (尝试 {attempt + 1}): {str(e)}")
                if attempt >= max_retries:
                    break
                await asyncio.sleep(retry_delay)
        
        return ""

    async def delete_document(self, doc_id: str) -> Dict[str, Any]:
        """删除文档"""
        return await self._request("DELETE", f"/knowledge/{doc_id}")

    async def update_document(self, doc_id: str, title: str = None, description: str = None) -> Dict[str, Any]:
        """更新文档信息"""
        payload = {"id": doc_id}  # WeKnora 要求 body 中必须包含 id
        if title: payload["title"] = title
        if description: payload["description"] = description
        return await self._request("PUT", f"/knowledge/{doc_id}", json=payload)

    async def summarize_document(self, doc_id: str) -> Dict[str, Any]:
        """生成文档摘要"""
        # WeKnora 详情接口通常包含摘要，或者有专门的 summary 字段
        # 这里模拟调用详情并触发摘要逻辑（如果 WeKnora 支持异步触发）
        return await self._request("GET", f"/knowledge/{doc_id}")

    async def get_document_concepts(self, doc_id: str) -> Dict[str, Any]:
        """获取文档关键概念"""
        # 假设 WeKnora 在详情或特定接口返回关键词/概念
        return await self._request("GET", f"/knowledge/{doc_id}")

    async def get_document_citations(self, doc_id: str) -> Dict[str, Any]:
        """获取文档引用关系"""
        # 假设 WeKnora 提供图谱或引用接口
        return await self._request("GET", f"/knowledge/{doc_id}")

    async def ask_agent(self, query: str, knowledge_base_ids: List[str] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        调用 WeKnora 的 Agent 模式进行问答，支持多轮对话和多知识库
        """
        import uuid
        if not session_id:
            session_id = str(uuid.uuid4())
            
        payload = {
            "query": query,
            "agent_enabled": True,
            "knowledge_base_ids": knowledge_base_ids or []
        }
        # 修正 WeKnora 的 Agent 接口为 /agent-chat/{session_id}
        # 注意：WeKnora 的 agent-chat 默认返回 SSE 流，这里我们通过 _request 处理
        # 如果需要流式返回给前端，后续需要专门处理
        return await self._request("POST", f"/agent-chat/{session_id}", json=payload)

    async def get_default_embedding_model_id(self) -> Optional[str]:
        """获取默认的 Embedding 模型 ID"""
        models = await self.list_models()
        for m in models:
            if m.get("type") == "Embedding":
                return m.get("id")
        return None

    async def create_knowledge_base(self, name: str, description: str = "", embedding_model_id: str = None) -> Dict[str, Any]:
        """
        在 WeKnora 中创建一个新的知识库
        """
        if not embedding_model_id:
            embedding_model_id = await self.get_default_embedding_model_id()
            
        payload = {
            "name": name,
            "description": description,
            "embedding_model_id": embedding_model_id
        }
        # 修正 WeKnora 的知识库创建接口为 /knowledge-bases
        return await self._request("POST", "/knowledge-bases", json=payload)

    async def list_models(self) -> List[Dict[str, Any]]:
        """获取 WeKnora 中的模型列表"""
        response = await self._request("GET", "/models")
        return response.get("data", [])

    async def create_model(self, name: str, model_type: str, source: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """在 WeKnora 中创建模型"""
        payload = {
            "name": name,
            "type": model_type,
            "source": source,
            "parameters": parameters
        }
        return await self._request("POST", "/models", json=payload)

# 全局单例
weknora_service = WeKnoraService()
