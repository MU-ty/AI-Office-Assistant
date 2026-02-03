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


weknora_service = WeKnoraService()
