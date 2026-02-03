from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class KnowledgeBasePayload(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: Optional[str] = Field(default=None, description="知识库名称")
    description: Optional[str] = Field(default=None, description="知识库描述")


class KnowledgeUrlCreate(BaseModel):
    url: str = Field(..., description="知识来源 URL")
    enable_multimodel: Optional[bool] = Field(default=None, description="是否启用多模态")


class KnowledgeSearchRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    query: str = Field(..., description="搜索文本")
    knowledge_base_id: Optional[str] = Field(default=None, description="单知识库 ID")
    knowledge_base_ids: Optional[List[str]] = Field(default=None, description="多知识库 ID 列表")
    knowledge_ids: Optional[List[str]] = Field(default=None, description="知识文件 ID 列表")


class KnowledgeChatRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    query: str = Field(..., description="提问内容")
    knowledge_base_ids: Optional[List[str]] = Field(default=None, description="知识库 ID 列表")
    knowledge_ids: Optional[List[str]] = Field(default=None, description="知识文件 ID 列表")


class AgentChatRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    query: str = Field(..., description="提问内容")
    agent_enabled: Optional[bool] = Field(default=True, description="是否启用 Agent")
    knowledge_base_ids: Optional[List[str]] = Field(default=None, description="知识库 ID 列表")
    knowledge_ids: Optional[List[str]] = Field(default=None, description="知识文件 ID 列表")
