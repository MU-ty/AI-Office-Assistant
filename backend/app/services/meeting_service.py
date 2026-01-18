"""会议纪要处理服务"""

import json
from typing import Dict, Any, List
from .llm_service import llm_service
from ..models.task import Task, TaskStatus

MEETING_MINUTES_PROMPT = """
你是一个专业的会议秘书。请将以下会议转录文本整理成结构化的会议纪要。
会议文本：
{text}

请输出以下格式的JSON字符串（且仅输出JSON）：
{{
    "title": "会议标题",
    "participants": ["参与人1", "参与人2"],
    "summary": "会议概况（200字以内）",
    "agenda": ["议程项1", "议程项2"],
    "decisions": ["決议1", "决议2"],
    "action_items": [
        {{"task": "任务描述", "assignee": "负责人", "due_date": "截止时间（如有）"}}
    ],
    "next_steps": ["下一步计划1"]
}}
"""

class MeetingService:
    """会议纪要服务类"""
    
    async def process_meeting_minutes(self, text: str) -> Dict[str, Any]:
        """处理会议文本生成纪要"""
        prompt = MEETING_MINUTES_PROMPT.format(text=text)
        
        messages = [
            {"role": "system", "content": "你是一个严谨的会议记录专家，善于总结核心要点和待办事项。"},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response_text = await llm_service.chat(messages, temperature=0.3)
            # 尝试解析JSON
            # 有时模型会输出 ```json ... ``` 块，需要清理
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:-3].strip()
            elif cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:-3].strip()
                
            return json.loads(cleaned_text)
        except Exception as e:
            print(f"Error processing meeting minutes: {e}")
            raise Exception(f"会议纪要生成失败: {str(e)}")

    def format_to_markdown(self, data: Dict[str, Any]) -> str:
        """将JSON纪要转换为Markdown格式"""
        md = f"# {data.get('title', '会议纪要')}\n\n"
        
        md += "## 参与人员\n"
        md += ", ".join(data.get('participants', [])) + "\n\n"
        
        md += "## 会议概况\n"
        md += data.get('summary', '') + "\n\n"
        
        md += "## 会后议程\n"
        for item in data.get('agenda', []):
            md += f"- {item}\n"
        md += "\n"
        
        md += "## 会议决议\n"
        for item in data.get('decisions', []):
            md += f"- {item}\n"
        md += "\n"
        
        md += "## 待办事项 (Action Items)\n"
        for item in data.get('action_items', []):
            task = item.get('task', '')
            assignee = item.get('assignee', '待定')
            due = item.get('due_date', '-')
            md += f"- **{task}** (负责人: {assignee}, 截止: {due})\n"
        md += "\n"
        
        md += "## 下一步计划\n"
        for item in data.get('next_steps', []):
            md += f"- {item}\n"
            
        return md

meeting_service = MeetingService()
