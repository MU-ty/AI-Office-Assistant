import json
from typing import Dict, List, Any, Optional
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

class LLMService:
    """
    LLM 服务层 - 专门处理与大模型 API 的交互
    目前主要适配 Qwen (通义千问) 模型，通过 OpenAI 兼容接口调用
    """

    def __init__(self):
        self.api_key = settings.QWEN_API_KEY
        self.base_url = settings.QWEN_BASE_URL
        self.model = settings.QWEN_MODEL_NAME
        self.client = None
        self._init_client()

    def _init_client(self):
        """初始化 OpenAI 客户端"""
        if not self.api_key:
            logger.warning("QWEN_API_KEY 未配置，LLM 服务将不可用")
            return

        logger.info(f"Initializing LLM Client with API Key (prefix): {self.api_key[:8]}...")
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        except ImportError:
            logger.error("openai 库未安装，请运行: pip install openai")
            self.client = None

    def check_availability(self) -> bool:
        """检查 LLM 服务是否可用"""
        return self.client is not None and bool(self.api_key)

    # 核心修复：这一行的缩进改为 4 个空格（之前是 3 个）
    async def get_embeddings(self, text: str, model: str = "text-embedding-v3") -> List[float]:
        """
        获取文本的向量表示 (Embedding)
        
        Args:
            text: 输入文本
            model: 模型名称，默认 text-embedding-v3 (OpenAI 兼容) 或 text-embedding-v1 (DashScope)
            
        Returns:
            向量列表 (List[float])
        """
        if not self.check_availability():
            logger.warning("LLM 服务不可用，无法生成 Embedding")
            return []
            
        try:
            # 移除换行符，避免影响 embedding 质量
            text = text.replace("\n", " ")
            
            response = await self.client.embeddings.create(
                input=[text],
                model=model
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"生成 Embedding 失败: {e}")
            # 如果是模型名称错误，尝试降级到 text-embedding-v1
            if "model" in str(e).lower() and model == "text-embedding-v3":
                logger.info("尝试降级到 text-embedding-v1")
                return await self.get_embeddings(text, model="text-embedding-v1")
            return []

    async def chat(self, messages: List[Dict[str, str]], stream: bool = False, temperature: float = 0.7) -> Any:
        """
        通用对话接口
        
        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            stream: 是否流式输出
            temperature: 温度参数
        """
        if not self.check_availability():
            if stream:
                async def error_gen():
                    yield "LLM 服务不可用"
                return error_gen()
            return "LLM 服务不可用"

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=stream
            )
            return response
        except Exception as e:
            logger.error(f"Chat 请求失败: {e}")
            if stream:
                async def error_gen():
                    yield f"Chat 请求失败: {str(e)}"
                return error_gen()
            return f"Chat 请求失败: {str(e)}"

    async def analyze_meeting_transcript(self, transcript: str) -> Dict[str, Any]:
        """
        分析会议转录文本，提取结构化信息
        
        提取内容包括：
        1. 摘要 (Summary)
        2. 议程 (Agendas)
        3. 话题 (Topics)
        4. 决议 (Decisions)
        5. 待办事项 (Action Items)
        
        Args:
            transcript: 会议转录文本
            
        Returns:
            包含上述信息的字典
        """
        if not self.check_availability():
            logger.warning("LLM 服务不可用，返回空结果")
            return self._get_empty_result()

        system_prompt = """你是一个专业的会议纪要助手。你的任务是分析会议转录文本，并提取关键信息。
请以纯 JSON 格式返回结果，不要包含 Markdown 格式标记（如 ```json）。
返回的 JSON 结构必须包含以下字段：
{
    "summary": "会议的执行摘要，200字以内",
    "topics": ["话题1", "话题2", "话题3"],
    "agendas": [
        {"title": "议程标题", "description": "议程描述"}
    ],
    "decisions": [
        "决议1", "决议2"
    ],
    "action_items": [
        {"content": "任务内容", "owner": "负责人（如果未提及则为'待定'）", "due_date": "截止日期（如果未提及则为'待定'）"}
    ],
    "key_points": ["关键点1", "关键点2"],
    "entities": {
        "persons": ["人名1", "人名2"],
        "organizations": ["机构名1", "机构名2"],
        "locations": ["地点1", "地点2"],
        "dates": ["日期1", "日期2"]
    }
}
如果某个字段没有相关信息，请返回空列表或空字符串。
"""

        user_prompt = f"以下是会议转录文本，请进行分析：\n\n{transcript[:50000]}" # 简单截断防止超长，实际应分块处理

        try:
            logger.info(f"开始调用 Qwen API 分析会议文本，模型: {self.model}")
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3, # 降低随机性，提高准确性
                response_format={"type": "json_object"} # 强制 JSON 输出 (如果模型支持)
            )

            content = response.choices[0].message.content
            logger.info("LLM 分析完成，正在解析 JSON")
            
            # 清理可能的 Markdown 标记
            content = content.replace("```json", "").replace("```", "").strip()
            
            result = json.loads(content)
            return self._validate_and_fix_result(result)

        except Exception as e:
            logger.error(f"LLM 分析失败: {e}")
            return self._get_empty_result()

    def _get_empty_result(self) -> Dict[str, Any]:
        """返回空的结果结构"""
        return {
            "summary": "无法生成摘要（LLM服务未配置或调用失败）",
            "topics": [],
            "agendas": [],
            "decisions": [],
            "action_items": [],
            "key_points": [],
            "entities": {
                "persons": [],
                "organizations": [],
                "locations": [],
                "dates": []
            }
        }

    def _validate_and_fix_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """验证并修复返回结果的结构"""
        default = self._get_empty_result()
        for key in default:
            if key not in result:
                result[key] = default[key]
        return result

    async def generate_document_summary(self, content: str) -> str:
        """生成文档摘要"""
        if not self.check_availability():
            return "无法生成摘要（LLM服务未配置）"
        
        system_prompt = "你是一个专业的文档分析助手。请为用户提供的文档内容生成一份简洁、准确的摘要，字数控制在300字以内。"
        user_prompt = f"请分析以下文档内容并生成摘要：\n\n{content[:20000]}" # 限制输入长度

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"生成摘要失败: {e}")
            return f"生成摘要失败: {str(e)}"

    async def extract_document_concepts(self, content: str) -> List[Dict[str, str]]:
        """提取文档关键概念"""
        if not self.check_availability():
            return []
        
        system_prompt = """你是一个专业的知识提取助手。请从文档中提取最核心的5-8个关键概念。
请以 JSON 数组格式返回，每个元素包含 'name' (概念名称) 和 'description' (在该文档背景下的简要定义)。
格式示例：[{"name": "概念A", "description": "定义..."}]
"""
        user_prompt = f"请从以下内容中提取关键概念：\n\n{content[:20000]}"

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            content_res = response.choices[0].message.content.strip()
            # 清理可能的 Markdown 标记
            content_res = content_res.replace("```json", "").replace("```", "").strip()
            return json.loads(content_res)
        except Exception as e:
            logger.error(f"提取概念失败: {e}")
            return []

    async def extract_document_citations(self, content: str) -> List[Dict[str, str]]:
        """提取文档中的引用/参考文献"""
        if not self.check_availability():
            return []
        
        system_prompt = """你是一个专业的学术文档助手。请从文档中识别并提取所有的参考文献、引用或提及的其他外部文档。
请以 JSON 数组格式返回，每个元素包含 'title' (标题) 和 'source' (来源/作者/年份等信息)。
如果文档中没有明确的引用，请返回空数组 []。
"""
        user_prompt = f"请从以下内容中提取引用信息：\n\n{content[:20000]}"

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            content_res = response.choices[0].message.content.strip()
            content_res = content_res.replace("```json", "").replace("```", "").strip()
            return json.loads(content_res)
        except Exception as e:
            logger.error(f"提取引用失败: {e}")
            return []

    def polish_weekly_report(self, summary: str, content: str) -> Dict[str, str]:
        """使用Qwen扩写与润色周报"""
        if not self.check_availability():
            return {"summary": summary, "content": content}

        system_prompt = (
            "你是专业的周报写作助手。"
            "请对用户提供的周报摘要与详细内容进行扩写和润色，"
            "保持结构清晰，包含：本周完成 / 问题与风险 / 下周计划。"
            "输出JSON对象，格式：{\"summary\": \"...\", \"content\": \"...\"}。"
        )
        user_prompt = (
            "摘要：\n" + summary + "\n\n" +
            "详细内容：\n" + content
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            content_res = response.choices[0].message.content.strip()
            content_res = content_res.replace("```json", "").replace("```", "").strip()
            data = json.loads(content_res)
            return {
                "summary": str(data.get("summary", summary)).strip(),
                "content": str(data.get("content", content)).strip()
            }
        except Exception as e:
            logger.error(f"周报润色失败: {e}")
            return {"summary": summary, "content": content}

    async def expand_ppt_bullets(self, title: str, slide_title: str, bullets: List[str]) -> List[str]:
        """扩展PPT大纲要点为更完整的表达（3-5句）"""
        if not self.check_availability():
            return bullets

        if not bullets:
            return bullets

        system_prompt = (
            "你是专业的PPT写作助手。请把要点扩展成3-5句简洁但完整的说明，"
            "保持专业、清晰、可直接放进PPT正文。"
            "仅输出JSON对象，格式：{\"bullets\": [\"...\", \"...\"]}。"
        )
        user_prompt = (
            f"演示主题：{title}\n"
            f"当前页标题：{slide_title}\n"
            "原始要点：\n"
            + "\n".join([f"- {b}" for b in bullets])
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content.strip()
            content = content.replace("```json", "").replace("```", "").strip()
            data = json.loads(content)

            if isinstance(data, dict):
                expanded = data.get("bullets") or data.get("sentences") or []
            else:
                expanded = data

            expanded = [str(item).strip() for item in expanded if str(item).strip()]
            return expanded or bullets
        except Exception as e:
            logger.error(f"扩展PPT要点失败: {e}")
            return bullets

# 全局实例git 
llm_service = LLMService()