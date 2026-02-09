
from elasticsearch import AsyncElasticsearch
from app.core.config import settings
from app.utils.logger import get_logger
from typing import List, Dict, Any, Optional

logger = get_logger(__name__)

class SearchService:
    """Elasticsearch 搜索服务"""

    def __init__(self):
        self.client = AsyncElasticsearch(
            settings.ELASTICSEARCH_URL,
            basic_auth=(settings.ELASTICSEARCH_USERNAME, settings.ELASTICSEARCH_PASSWORD) if settings.ELASTICSEARCH_USERNAME else None,
            verify_certs=settings.ELASTICSEARCH_VERIFY_CERTS,
            # 强制指定兼容 ES 8.x，防止客户端发送 compatible-with=9 导致 400 错误
            headers={"Accept": "application/vnd.elasticsearch+json; compatible-with=8"}
        )
        self.index_name = "office_documents"
        self.chunk_index_name = "office_document_chunks"

    async def init_index(self):
        """初始化索引 Mapping"""
        # 1. 初始化文档索引
        if not await self.client.indices.exists(index=self.index_name):
            await self._create_doc_index()
            
        # 2. 初始化切片索引 (用于 RAG)
        if not await self.client.indices.exists(index=self.chunk_index_name):
            await self._create_chunk_index()
        else:
            # 检查现有索引的向量维度是否匹配
            try:
                mapping = await self.client.indices.get_mapping(index=self.chunk_index_name)
                props = mapping[self.chunk_index_name]["mappings"]["properties"]
                if "vector" in props:
                    current_dims = props["vector"].get("dims")
                    if current_dims != 1024:
                        logger.warning(f"检测到索引 {self.chunk_index_name} 维度 ({current_dims}) 与配置 (1024) 不匹配，正在重建索引...")
                        await self.client.indices.delete(index=self.chunk_index_name)
                        await self._create_chunk_index()
            except Exception as e:
                logger.error(f"检查索引维度失败: {e}")

    async def _create_doc_index(self):
        """创建文档索引"""
        mapping = {
            "mappings": {
                "properties": {
                    "title": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart"},
                    "content": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart"},
                    "tags": {"type": "keyword"},
                    "document_type": {"type": "keyword"},
                    "knowledge_base_id": {"type": "integer"},
                    "directory_id": {"type": "integer"},
                    "user_id": {"type": "integer"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"}
                }
            }
        }
        await self._create_index_with_fallback(self.index_name, mapping)

    async def _create_chunk_index(self):
        """创建切片索引"""
        mapping = {
            "mappings": {
                "properties": {
                    "doc_id": {"type": "integer"},
                    "chunk_index": {"type": "integer"},
                    "content": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart"},
                    "vector": {
                        "type": "dense_vector",
                        "dims": 1024,  # 修正：从 1536 改为 1024，以匹配 qwen-embedding 模型
                        "index": True,
                        "similarity": "cosine"
                    },
                    "knowledge_base_id": {"type": "integer"},
                    "metadata": {"type": "object"}
                }
            }
        }
        await self._create_index_with_fallback(self.chunk_index_name, mapping)

    async def _create_index_with_fallback(self, index_name: str, mapping: Dict):
        """尝试创建索引，如果 IK 分词器不存在则降级"""
        try:
            await self.client.indices.create(index=index_name, body=mapping)
            logger.info(f"ES 索引 {index_name} 创建成功")
        except Exception as e:
            if "analyzer [ik_max_word] not found" in str(e) or "resource_already_exists_exception" not in str(e):
                logger.warning(f"尝试使用 IK 分词器创建索引 {index_name} 失败，尝试使用 standard 分词器: {e}")
                # 递归替换 analyzer
                def replace_analyzer(obj):
                    if isinstance(obj, dict):
                        for k, v in obj.items():
                            if k in ["analyzer", "search_analyzer"] and v.startswith("ik_"):
                                obj[k] = "standard"
                            else:
                                replace_analyzer(v)
                
                replace_analyzer(mapping)
                try:
                    await self.client.indices.create(index=index_name, body=mapping)
                    logger.info(f"ES 索引 {index_name} 创建成功 (Standard Analyzer)")
                except Exception as e2:
                    logger.error(f"创建索引 {index_name} 最终失败: {e2}")

    async def index_document(self, doc_id: int, data: Dict[str, Any]):
        """索引文档"""
        try:
            await self.client.index(index=self.index_name, id=str(doc_id), document=data)
            logger.info(f"文档 {doc_id} 已索引到 ES")
        except Exception as e:
            logger.error(f"ES 索引失败: {e}")

    async def delete_document(self, doc_id: int):
        """删除文档索引"""
        try:
            await self.client.delete(index=self.index_name, id=str(doc_id))
            # 同时删除切片
            await self.client.delete_by_query(
                index=self.chunk_index_name,
                body={"query": {"term": {"doc_id": doc_id}}}
            )
        except Exception as e:
            logger.warning(f"ES 删除文档失败 (可能不存在): {e}")

    async def index_chunks(self, chunks: List[Dict[str, Any]]):
        """批量索引切片"""
        if not chunks:
            return
            
        # 使用 bulk API 批量写入
        body = []
        for chunk in chunks:
            # chunk 结构: {doc_id, chunk_index, content, vector, knowledge_base_id, metadata}
            # 生成唯一 ID
            chunk_id = f"{chunk['doc_id']}_{chunk['chunk_index']}"
            
            action = {"index": {"_index": self.chunk_index_name, "_id": chunk_id}}
            body.append(action)
            body.append(chunk)
            
        try:
            resp = await self.client.bulk(operations=body)
            if resp.get("errors"):
                logger.error(f"ES 批量索引切片存在错误: {resp}")
            else:
                logger.info(f"成功索引 {len(chunks)} 个切片")
        except Exception as e:
            logger.error(f"ES 批量索引切片失败: {e}")

    async def search_hybrid(self, query_text: str, query_vector: List[float], 
                          knowledge_base_ids: List[int] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        混合检索 (向量 + 文本)
        """
        # 构建过滤器
        filters = []
        if knowledge_base_ids:
            filters.append({"terms": {"knowledge_base_id": knowledge_base_ids}})
            
        # 构建 KNN 查询
        knn_query = {
            "field": "vector",
            "query_vector": query_vector,
            "k": top_k,
            "num_candidates": 100,
            "filter": filters
        }
        
        # 构建全文检索查询 (作为备选或加权)
        # 这里我们使用 ES 的 RRF (Reciprocal Rank Fusion) 或者简单的 hybrid
        # 由于 ES 8.x 的 knn search 可以直接返回结果，我们可以结合 bool query
        
        # 简单策略：使用 kNN 搜索，同时匹配文本关键词以提升相关性
        # 或者直接使用 kNN，因为向量通常包含了语义
        
        try:
            response = await self.client.search(
                index=self.chunk_index_name,
                knn=knn_query,
                # 可选：添加文本匹配来重排序或过滤
                query={
                    "bool": {
                        "must": [
                             {"match": {"content": query_text}}
                        ],
                        "filter": filters
                    }
                } if query_text else None,
                size=top_k,
                _source=["doc_id", "chunk_index", "content", "knowledge_base_id", "metadata", "score"]
            )
            
            results = []
            for hit in response["hits"]["hits"]:
                item = hit["_source"]
                item["score"] = hit["_score"]
                item["id"] = hit["_id"]
                # 移除 vector 以减少传输量
                if "vector" in item:
                    del item["vector"]
                results.append(item)
                
            return results
        except Exception as e:
            logger.error(f"ES 混合检索失败: {e}")
            return []

    async def search(self, query: str, filters: Dict[str, Any] = None, page: int = 1, size: int = 10) -> Dict[str, Any]:
        """全文搜索"""
        must_clauses = [
            {"multi_match": {
                "query": query,
                # 增加 content 字段的权重，同时保留 title 的高权重
                # 之前 content 没有加权，可能导致匹配分值较低
                "fields": ["title^3", "content^1"],  
                "fuzziness": "AUTO",
                "operator": "or", # 默认是 OR，可以显式指定
                "type": "best_fields"
            }}
        ]

        filter_clauses = []
        if filters:
            for k, v in filters.items():
                if v is not None:
                    if isinstance(v, list):
                        filter_clauses.append({"terms": {k: v}})
                    else:
                        filter_clauses.append({"term": {k: v}})

        body = {
            "from": (page - 1) * size,
            "size": size,
            "query": {
                "bool": {
                    "must": must_clauses,
                    "filter": filter_clauses
                }
            },
            "highlight": {
                "fields": {
                    "title": {},
                    "content": {"fragment_size": 150, "number_of_fragments": 3}
                }
            }
        }

        try:
            response = await self.client.search(index=self.index_name, body=body)
            return self._format_response(response)
        except Exception as e:
            logger.error(f"ES 搜索失败: {e}")
            return {"total": 0, "items": []}

    def _format_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        hits = response["hits"]["hits"]
        total = response["hits"]["total"]["value"]
        
        items = []
        for hit in hits:
            source = hit["_source"]
            highlight = hit.get("highlight", {})
            
            # 使用高亮覆盖原始内容
            if "title" in highlight:
                source["title_highlight"] = highlight["title"][0]
            if "content" in highlight:
                source["content_highlight"] = highlight["content"]
            
            source["id"] = int(hit["_id"])
            source["score"] = hit["_score"]
            items.append(source)
            
        return {"total": total, "items": items}

search_service = SearchService()
