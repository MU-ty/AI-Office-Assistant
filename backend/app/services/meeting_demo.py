"""
会议纪要功能使用示例和演示

这个文件展示了如何使用各个服务模块和API端点

运行方式：
  python app/services/meeting_demo.py        (从backend目录)
  python -m app.services.meeting_demo        (从backend目录)
"""

import sys
import os

# 支持从 backend 目录直接运行
if __name__ == "__main__" and __package__ is None:
    # 添加当前目录的父目录到路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(os.path.dirname(current_dir))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)

# ============================================================
# 1. NLPService 使用示例
# ============================================================

"""
NLP文本处理服务演示
"""

from app.services.nlp_service import nlp_service

# 示例文本：真实的会议转录文本
meeting_transcript = """
各位好，欢迎参加Q1产品规划会。今天我们要讨论三个主要议题：产品功能规划、技术方案评审、以及市场推广计划。

首先，让我们看一下产品功能规划。根据市场需求分析，用户最关注的是性能优化和用户界面改进。我们计划在2月底完成第一版原型。技术团队需要确定使用React还是Vue框架。

接下来是技术方案评审。后端使用Python FastAPI，前端框架待定。数据库选择PostgreSQL。我们需要在本周内确定选型。李建负责后端架构设计，张晓负责前端技术选型。

最后是市场推广计划。市场部计划从3月开始进行推广，目标是获得1000个种子用户。市场团队需要在下周提交详细的推广方案。

决议如下：
1. 产品功能以性能和UI为重点
2. 确定使用Python FastAPI和PostgreSQL作为后端技术栈
3. 前端框架在下周内确定，由技术团队投票决议
4. 市场推广方案下周提交

Action Items：
- 李建：完成后端架构设计文档，截止日期2月1日
- 张晓：完成前端框架对比分析，截止日期1月30日
- 王刚：准备详细的推广方案，截止日期2月2日
- 所有人：下周五前提供对技术选型的意见

今天的会议就到这里，感谢大家的参与。
"""


def demo_nlp_service():
    """演示NLPService的各项功能"""
    
    print("=" * 60)
    print("NLPService 演示")
    print("=" * 60)
    
    # 1. 分句
    print("\n【分句结果】")
    sentences = nlp_service.split_sentences(meeting_transcript)
    for i, sent in enumerate(sentences[:5], 1):
        print(f"{i}. {sent}")
    print(f"... 共{len(sentences)}句")
    
    # 2. 提取关键词
    print("\n【关键词提取】(TF-IDF)")
    keywords = nlp_service.extract_keywords(meeting_transcript, top_k=10, withWeight=True)
    for kw, weight in keywords:
        print(f"  {kw}: {weight:.3f}")
    
    # 3. 提取关键句
    print("\n【关键句提取】")
    key_sents = nlp_service.extract_key_sentences(meeting_transcript, top_k=5)
    for i, sent in enumerate(key_sents, 1):
        print(f"{i}. {sent}")
    
    # 4. 实体识别
    print("\n【实体识别】")
    entities = nlp_service.extract_entities(meeting_transcript)
    print(f"  日期: {entities['dates']}")
    print(f"  时间: {entities['times']}")
    
    # 5. 文本统计
    print("\n【文本统计】")
    stats = nlp_service.get_text_stats(meeting_transcript)
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 6. 中文分词
    print("\n【中文分词】(前10个词)")
    tokens = nlp_service.tokenize(meeting_transcript)
    print(f"  {' / '.join(tokens[:10])}")
    print(f"  ... 共{len(tokens)}个词")


# ============================================================
# 2. DocumentGenerationService 使用示例
# ============================================================

"""
文档生成服务演示
"""

from app.services.document_generation_service import document_generation_service

# 处理后的会议数据结构
processed_meeting_data = {
    'date': '2026-01-25',
    'participants': ['王总', '李建', '张晓', '王刚', '市场部负责人'],
    'agendas': [
        {'title': '产品功能规划', 'description': '讨论Q1产品功能重点和目标'},
        {'title': '技术方案评审', 'description': '确定技术栈选型'},
        {'title': '市场推广计划', 'description': '制定市场推广策略'}
    ],
    'key_points': [
        '产品功能以性能优化和UI改进为重点',
        '后端确定使用Python FastAPI和PostgreSQL',
        '前端框架需要在下周内确定',
        '市场推广从3月开始，目标1000个种子用户'
    ],
    'decisions': [
        '产品功能以性能和UI为重点，原型完成期限为2月底',
        '后端技术栈确定：Python FastAPI + PostgreSQL',
        '前端框架在下周内确定，由技术团队投票决议',
        '市场推广方案需要在2月2日前提交'
    ],
    'action_items': [
        {
            'content': '完成后端架构设计文档',
            'owner': '李建',
            'due_date': '2026-02-01'
        },
        {
            'content': '完成前端框架对比分析',
            'owner': '张晓',
            'due_date': '2026-01-30'
        },
        {
            'content': '准备详细的市场推广方案',
            'owner': '王刚',
            'due_date': '2026-02-02'
        },
        {
            'content': '技术选型意见收集',
            'owner': '所有人',
            'due_date': '2026-01-31'
        }
    ],
    'transcription': meeting_transcript
}


def demo_document_generation():
    """演示DocumentGenerationService的各项功能"""
    
    print("\n" + "=" * 60)
    print("DocumentGenerationService 演示")
    print("=" * 60)
    
    title = "Q1产品规划会议纪要 - 2026年1月25日"
    
    # 1. 生成Markdown
    print("\n【生成Markdown】")
    md_content = document_generation_service.generate_markdown(title, processed_meeting_data)
    print(md_content[:500] + "...")
    
    # 2. 生成JSON
    print("\n【生成JSON】")
    json_str = document_generation_service.generate_json(processed_meeting_data)
    print(json_str[:300] + "...")
    
    # 3. 生成PDF（需要reportlab）
    print("\n【生成PDF】")
    try:
        success = document_generation_service.generate_pdf(
            title,
            processed_meeting_data,
            "/tmp/meeting_minutes.pdf"
        )
        if success:
            print("  ✓ PDF生成成功: /tmp/meeting_minutes.pdf")
        else:
            print("  ✗ PDF生成失败")
    except Exception as e:
        print(f"  ✗ 需要安装reportlab: pip install reportlab")
    
    # 4. 生成Word（需要python-docx）
    print("\n【生成Word】")
    try:
        success = document_generation_service.generate_docx(
            title,
            processed_meeting_data,
            "/tmp/meeting_minutes.docx"
        )
        if success:
            print("  ✓ Word文档生成成功: /tmp/meeting_minutes.docx")
        else:
            print("  ✗ Word文档生成失败")
    except Exception as e:
        print(f"  ✗ 需要安装python-docx: pip install python-docx")


# ============================================================
# 3. API 使用示例
# ============================================================

"""
API端点使用示例
"""

import httpx
import asyncio


async def demo_api_usage():
    """演示API端点的调用"""
    
    print("\n" + "=" * 60)
    print("API 使用示例")
    print("=" * 60)
    
    base_url = "http://localhost:8000/api/v1"
    
    async with httpx.AsyncClient() as client:
        
        # 1. 创建会议
        print("\n【步骤1：创建会议】")
        response = await client.post(
            f"{base_url}/meetings",
            json={
                "title": "Q1产品规划会",
                "meeting_type": "planning",
                "start_time": "2026-01-25T14:00:00",
                "location": "会议室A"
            }
        )
        if response.status_code == 201:
            meeting = response.json()
            meeting_id = meeting.get('id', 'meeting_001')
            print(f"✓ 会议创建成功: {meeting_id}")
        else:
            print(f"✗ 创建失败: {response.status_code}")
            meeting_id = "meeting_001"
        
        # 2. 上传音视频（模拟）
        print("\n【步骤2：上传音视频】")
        print("  (在实际应用中，这里需要上传真实的音视频文件)")
        print(f"  POST /api/v1/meetings/{meeting_id}/upload")
        print("  Content-Type: multipart/form-data")
        print("  Body: file=<audio.mp3>")
        
        # 3. 处理转录文本
        print("\n【步骤3：处理转录文本】")
        response = await client.post(
            f"{base_url}/meetings/{meeting_id}/process",
            json={
                "transcription_text": meeting_transcript
            }
        )
        if response.status_code == 200:
            print("✓ 转录文本处理成功")
            processed_data = response.json()
            print(f"  提取关键词: {len(processed_data.get('keywords', []))}个")
            print(f"  提取议程: {len(processed_data.get('agendas', []))}个")
            print(f"  提取决议: {len(processed_data.get('decisions', []))}个")
            print(f"  提取Action Items: {len(processed_data.get('action_items', []))}个")
        else:
            print(f"✗ 处理失败: {response.status_code}")
        
        # 4. 生成纪要
        print("\n【步骤4：生成纪要（多格式）】")
        response = await client.post(
            f"{base_url}/meetings/{meeting_id}/generate-minutes",
            json={
                "meeting_data": processed_meeting_data,
                "formats": ["markdown", "json", "pdf", "docx"]
            }
        )
        if response.status_code == 200:
            print("✓ 纪要生成成功")
            result = response.json()
            for fmt in result.get('formats', {}):
                print(f"  - {fmt}: {result['formats'][fmt]}")
        else:
            print(f"✗ 生成失败: {response.status_code}")
        
        # 5. 邮件发送
        print("\n【步骤5：邮件发送】")
        response = await client.post(
            f"{base_url}/meetings/{meeting_id}/send-email",
            json={
                "recipients": ["team@company.com"],
                "format": "pdf"
            }
        )
        if response.status_code == 200:
            print("✓ 邮件发送成功")
        else:
            print(f"✗ 发送失败: {response.status_code}")
        
        # 6. 获取会议信息
        print("\n【步骤6：查询会议信息】")
        endpoints = [
            f"/meetings/{meeting_id}/agendas (议程)",
            f"/meetings/{meeting_id}/decisions (决议)",
            f"/meetings/{meeting_id}/action-items (Action Items)",
            f"/meetings/{meeting_id}/participants (参与人)"
        ]
        for endpoint in endpoints:
            print(f"  GET {endpoint}")


# ============================================================
# 4. 在其他功能中复用的示例
# ============================================================

"""
展示如何在其他功能（如周报、PPT等）中复用核心服务
"""

class WeeklyReportGenerator:
    """周报生成器 - 复用NLP和文档生成服务"""
    
    def __init__(self):
        self.nlp = nlp_service
        self.doc_gen = document_generation_service
    
    def generate_report(self, weekly_summary: str, output_formats: list = None):
        """
        从周活动总结生成周报
        
        参数:
            weekly_summary: 周活动的自由文本描述
            output_formats: 输出格式列表
        
        返回:
            包含各种格式周报的字典
        """
        if output_formats is None:
            output_formats = ['markdown', 'docx']
        
        # 使用NLP提取关键信息
        key_activities = self.nlp.extract_key_sentences(weekly_summary, top_k=5)
        keywords = self.nlp.extract_keywords(weekly_summary, top_k=10)
        entities = self.nlp.extract_entities(weekly_summary)
        
        # 组织为周报数据
        report_data = {
            'week': '2026-01-20 ~ 2026-01-26',
            'key_activities': key_activities,
            'keywords': [kw[0] if isinstance(kw, tuple) else kw for kw in keywords],
            'next_deadlines': entities.get('dates', []),
            'full_content': weekly_summary
        }
        
        # 生成多种格式
        results = {}
        for fmt in output_formats:
            if fmt == 'markdown':
                results['markdown'] = self.doc_gen.generate_markdown('周报', report_data)
            elif fmt == 'docx':
                self.doc_gen.generate_docx('周报', report_data, './weekly_report.docx')
                results['docx'] = './weekly_report.docx'
            elif fmt == 'json':
                results['json'] = self.doc_gen.generate_json(report_data)
        
        return results


def demo_weekly_report():
    """演示周报生成的复用场景"""
    
    print("\n" + "=" * 60)
    print("周报生成器演示（复用NLP和文档生成）")
    print("=" * 60)
    
    weekly_text = """
    本周主要工作成果：
    1. 完成了用户认证模块的开发和测试
    2. 修复了5个线上bug
    3. 召开了两次项目评审会
    4. 准备了下周的技术分享
    
    计划下周完成的任务：
    1. 支付模块的集成（截止2月2日）
    2. 数据库性能优化
    3. 编写技术文档
    """
    
    generator = WeeklyReportGenerator()
    report = generator.generate_report(weekly_text, ['markdown', 'json'])
    
    print("\n生成的周报（Markdown）:")
    print(report['markdown'][:300] + "...")
    print("\n生成的周报（JSON）:")
    print(report['json'][:200] + "...")


# ============================================================
# 主函数
# ============================================================

def main():
    """运行所有演示"""
    
    print("\n" + "=" * 60)
    print("会议纪要功能完整演示")
    print("=" * 60)
    
    # 演示NLPService
    demo_nlp_service()
    
    # 演示DocumentGenerationService
    demo_document_generation()
    
    # 演示周报生成（复用）
    demo_weekly_report()
    
    # 演示API（需要服务器运行）
    print("\n" + "=" * 60)
    print("API 端点演示")
    print("=" * 60)
    print("\n要运行API演示，请确保FastAPI服务已启动：")
    print("  uvicorn app.main:app --reload")
    print("\n或取消下面的注释运行异步演示:")
    # asyncio.run(demo_api_usage())


if __name__ == "__main__":
    main()
