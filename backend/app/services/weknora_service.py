import httpx
from typing import Any, AsyncGenerator, Dict, Optional, List
import asyncio

from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class WeKnoraService:
    """
    WeKnora API 客户端封装
    """

    def __init__(self) -> None:
        self.base_url = settings.WEKNORA_BASE_URL.rstrip("/")
        self.api_key = settings.WEKNORA_API_KEY
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key if self.api_key else ""
        }
        self.timeout = 60.0

    async def _request(self, method: str, endpoint: str, **kwargs: Any) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.request(method, url, headers=self.headers, **kwargs)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error("WeKnora API 错误: %s - %s", e.response.status_code, e.response.text)
                raise
            except Exception as e:
                logger.error("WeKnora 请求异常: %s", str(e))
                raise

    async def stream_request(
        self, method: str, endpoint: str, **kwargs: Any
    ) -> AsyncGenerator[bytes, None]:
        url = f"{self.base_url}{endpoint}"
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(method, url, headers=self.headers, **kwargs) as response:
                response.raise_for_status()
                async for chunk in response.aiter_bytes():
                    yield chunk

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
        payload = {"id": doc_id}
        if title: payload["title"] = title
        if description: payload["description"] = description
        return await self._request("PUT", f"/knowledge/{doc_id}", json=payload)

    async def create_knowledge_base(self, name: str, description: str = "", embedding_model_id: str = None) -> Dict[str, Any]:
        """在 WeKnora 中创建新的知识库"""
        payload = {
            "name": name,
            "description": description,
            "embedding_model_id": embedding_model_id
        }
        return await self._request("POST", "/knowledge-bases", json=payload)

    async def upload_document_file(self, knowledge_base_id: str, file_path: str) -> Dict[str, Any]:
        """上传并解析文档到知识库"""
        url = f"{self.base_url}/knowledge-bases/{knowledge_base_id}/knowledge/file"
        async with httpx.AsyncClient(timeout=120.0) as client:
            with open(file_path, "rb") as f:
                files = {"file": f}
                response = await client.post(url, headers={"x-api-key": self.api_key}, files=files)
                response.raise_for_status()
                return response.json()

    async def upload_document_text(self, knowledge_base_id: str, title: str, content: str) -> Dict[str, Any]:
        """上传纯文本/Markdown 到知识库"""
        payload = {
            "title": title,
            "content": content,
        }
        return await self._request("POST", f"/knowledge-bases/{knowledge_base_id}/knowledge/manual", json=payload)

    async def knowledge_search(self, query: str, knowledge_base_ids: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """在指定知识库中进行语义检索"""
        payload = {
            "query": query,
            "knowledge_base_ids": knowledge_base_ids,
            "top_k": top_k
        }
        response = await self._request("POST", "/knowledge-search", json=payload)
        return response.get("data", [])

    async def list_models(self) -> List[Dict[str, Any]]:
        """获取 WeKnora 中的模型列表"""
        response = await self._request("GET", "/models")
        return response.get("data", [])

    # --- 知识库管理 ---

    async def list_knowledge_bases(self) -> Dict[str, Any]:
        """获取知识库列表"""
        return await self._request("GET", "/knowledge-bases")

    async def get_knowledge_base(self, kb_id: str) -> Dict[str, Any]:
        """获取知识库详情"""
        return await self._request("GET", f"/knowledge-bases/{kb_id}")

    async def create_knowledge_base(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """创建知识库"""
        # 支持传入字典或解包参数
        if isinstance(data, dict):
            payload = data
        else:
            # 兼容旧代码调用
            payload = {"name": data}
            
        return await self._request("POST", "/knowledge-bases", json=payload)

    async def update_knowledge_base(self, kb_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """更新知识库"""
        return await self._request("PUT", f"/knowledge-bases/{kb_id}", json=data)

    async def delete_knowledge_base(self, kb_id: str) -> Dict[str, Any]:
        """删除知识库"""
        return await self._request("DELETE", f"/knowledge-bases/{kb_id}")

    # --- 知识内容管理 ---

    async def list_knowledge(self, kb_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取知识列表"""
        return await self._request("GET", f"/knowledge-bases/{kb_id}/knowledge", params=params)

    async def upload_knowledge_file(self, kb_id: str, file_name: str, file_bytes: bytes, content_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """上传文件到知识库"""
        url = f"{self.base_url}/knowledge-bases/{kb_id}/knowledge/file"
        async with httpx.AsyncClient(timeout=120.0) as client:
            files = {"file": (file_name, file_bytes, content_type)}
            response = await client.post(url, headers={"x-api-key": self.api_key}, files=files, data=data)
            response.raise_for_status()
            return response.json()

    async def create_knowledge_url(self, kb_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """从 URL 创建知识"""
        return await self._request("POST", f"/knowledge-bases/{kb_id}/knowledge/url", json=data)

    async def get_knowledge(self, knowledge_id: str) -> Dict[str, Any]:
        """获取知识详情"""
        return await self._request("GET", f"/knowledge/{knowledge_id}")

    async def delete_knowledge(self, knowledge_id: str) -> Dict[str, Any]:
        """删除知识"""
        return await self._request("DELETE", f"/knowledge/{knowledge_id}")

    # --- 检索与问答 ---

    async def knowledge_search(self, data: Any, knowledge_base_ids: List[str] = None, top_k: int = 5) -> Any:
        """知识库搜索"""
        # 兼容旧代码调用: knowledge_search(query, kb_ids, top_k)
        if not isinstance(data, dict):
            return await self._old_knowledge_search(data, knowledge_base_ids, top_k)
            
        return await self._request("POST", "/knowledge-search", json=data)

    async def knowledge_chat_stream(self, session_id: str, data: Dict[str, Any]) -> AsyncGenerator[bytes, None]:
        """知识库问答流"""
        async for chunk in self.stream_request("POST", f"/knowledge-chat/{session_id}", json=data):
            yield chunk

    async def agent_chat_stream(self, session_id: str, data: Dict[str, Any]) -> AsyncGenerator[bytes, None]:
        """Agent 问答流"""
        async for chunk in self.stream_request("POST", f"/agent-chat/{session_id}", json=data):
            yield chunk

    # 为了兼容旧代码的辅助方法
    async def _old_knowledge_search(self, query: str, knowledge_base_ids: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        payload = {
            "query": query,
            "knowledge_base_ids": knowledge_base_ids,
            "top_k": top_k
        }
        response = await self._request("POST", "/knowledge-search", json=payload)
        return response.get("data", [])


weknora_service = WeKnoraService()
