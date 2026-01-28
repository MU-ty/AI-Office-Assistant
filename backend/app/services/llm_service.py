
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

        try:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        except ImportError:
            logger.error("openai 库未安装，请运行: pip install openai")
            self.client = None

    def check_availability(self) -> bool:
        """检查 LLM 服务是否可用"""
        return self.client is not None and bool(self.api_key)

    def analyze_meeting_transcript(self, transcript: str) -> Dict[str, Any]:
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
            response = self.client.chat.completions.create(
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

# 全局实例git 
llm_service = LLMService()
