import httpx
from typing import Any, AsyncGenerator, Dict, Optional

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
        self.timeout = settings.WEKNORA_TIMEOUT

    def _ensure_config(self) -> None:
        if not self.base_url:
            raise RuntimeError("WEKNORA_BASE_URL 未配置")
        if not self.api_key:
            raise RuntimeError("WEKNORA_API_KEY 未配置")

    def _headers(self, content_type: Optional[str] = "application/json") -> Dict[str, str]:
        headers = {"X-API-Key": self.api_key}
        if content_type:
            headers["Content-Type"] = content_type
        return headers

    async def _request(self, method: str, endpoint: str, **kwargs: Any) -> Dict[str, Any]:
        self._ensure_config()
        url = f"{self.base_url}{endpoint}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.request(method, url, headers=self._headers(), **kwargs)
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
        self._ensure_config()
        url = f"{self.base_url}{endpoint}"
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(method, url, headers=self._headers(), **kwargs) as response:
                response.raise_for_status()
                async for chunk in response.aiter_bytes():
                    yield chunk

    # =====================
    # Knowledge Bases
    # =====================
    async def list_knowledge_bases(self) -> Dict[str, Any]:
        return await self._request("GET", "/knowledge-bases")

    async def create_knowledge_base(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._request("POST", "/knowledge-bases", json=payload)

    async def get_knowledge_base(self, kb_id: str) -> Dict[str, Any]:
        return await self._request("GET", f"/knowledge-bases/{kb_id}")

    async def update_knowledge_base(self, kb_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._request("PUT", f"/knowledge-bases/{kb_id}", json=payload)

    async def delete_knowledge_base(self, kb_id: str) -> Dict[str, Any]:
        return await self._request("DELETE", f"/knowledge-bases/{kb_id}")

    # =====================
    # Knowledge
    # =====================
    async def list_knowledge(self, kb_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        return await self._request("GET", f"/knowledge-bases/{kb_id}/knowledge", params=params)

    async def upload_knowledge_file(
        self,
        kb_id: str,
        file_name: str,
        file_bytes: bytes,
        content_type: Optional[str],
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        self._ensure_config()
        url = f"{self.base_url}/knowledge-bases/{kb_id}/knowledge/file"
        files = {"file": (file_name, file_bytes, content_type or "application/octet-stream")}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, headers={"X-API-Key": self.api_key}, data=data, files=files)
            response.raise_for_status()
            return response.json()

    async def create_knowledge_url(self, kb_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._request("POST", f"/knowledge-bases/{kb_id}/knowledge/url", json=payload)

    async def get_knowledge(self, knowledge_id: str) -> Dict[str, Any]:
        return await self._request("GET", f"/knowledge/{knowledge_id}")

    async def delete_knowledge(self, knowledge_id: str) -> Dict[str, Any]:
        return await self._request("DELETE", f"/knowledge/{knowledge_id}")

    # =====================
    # Search & Chat
    # =====================
    async def knowledge_search(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._request("POST", "/knowledge-search", json=payload)

    async def knowledge_chat_stream(self, session_id: str, payload: Dict[str, Any]) -> AsyncGenerator[bytes, None]:
        return self.stream_request("POST", f"/knowledge-chat/{session_id}", json=payload)

    async def agent_chat_stream(self, session_id: str, payload: Dict[str, Any]) -> AsyncGenerator[bytes, None]:
        return self.stream_request("POST", f"/agent-chat/{session_id}", json=payload)

    # =====================
    # Models
    # =====================
    async def list_models(self) -> list:
        """获取模型列表"""
        result = await self._request("GET", "/models")
        # 返回 data 字段中的模型列表，如果是列表则直接返回
        if isinstance(result, dict):
            return result.get("data", []) if isinstance(result.get("data"), list) else [result]
        return result if isinstance(result, list) else []

    async def create_model(
        self, name: str, model_type: str, source: str, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """创建模型"""
        payload = {
            "name": name,
            "type": model_type,
            "source": source,
            "parameters": parameters,
        }
        return await self._request("POST", "/models", json=payload)

    async def get_model(self, model_id: str) -> Dict[str, Any]:
        """获取模型详情"""
        return await self._request("GET", f"/models/{model_id}")

    async def update_model(self, model_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """更新模型"""
        return await self._request("PUT", f"/models/{model_id}", json=payload)

    async def delete_model(self, model_id: str) -> Dict[str, Any]:
        """删除模型"""
        return await self._request("DELETE", f"/models/{model_id}")


weknora_service = WeKnoraService()
