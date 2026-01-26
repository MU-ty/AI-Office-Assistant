# 会议纪要功能实现指南

## 📋 概述

基于表格和流程图，实现了完整的会议纪要处理系统。核心特点：

- ✅ **模块化设计**：表格标黄部分已独立成可复用的服务模块
- ✅ **完整流程**：按照流程图的23个步骤实现端到端的处理
- ✅ **多格式输出**：支持Markdown、PDF、Word、JSON格式
- ✅ **灵活拓展**：各个服务模块可独立使用和组合

---

## 🏗️ 架构设计

### 服务层次结构

```
API层 (api/meetings.py)
    ↓
MeetingService (services/meeting_service.py)
    ├── MeetingMinutesService (services/meeting_minutes_service.py)
    │   ├── NLPService (services/nlp_service.py) ← 表格标黄
    │   └── DocumentGenerationService (services/document_generation_service.py) ← 表格标黄
    └── DatabaseLayer (core/database.py)
```

---

## 📦 核心服务模块

### 1. NLPService - 文本处理服务

**位置**：`backend/app/services/nlp_service.py`

**功能模块**：

| 功能 | 方法 | 说明 | 优先级 |
|------|------|------|--------|
| 分句与分段 | `split_sentences()`, `split_paragraphs()` | 将文本按标点和换行符分割 | p0 |
| 关键词提取 | `extract_keywords()` | 使用TF-IDF算法提取关键词 | p1 |
| 关键句提取 | `extract_key_sentences()` | 基于关键词频率提取重要句子 | p1 |
| 中文分词 | `tokenize()`, `tokenize_with_pos()` | 使用jieba进行分词和词性标注 | p0 |
| 实体识别 | `extract_entities()` | 提取人名、机构、日期等 | p1 |
| 文本统计 | `get_text_stats()` | 获取字数、词数、句数等统计信息 | p2 |
| 文本清洗 | `clean_text()` | 清洗和标准化文本 | p0 |

**使用示例**：

```python
from app.services.nlp_service import nlp_service

# 分句
sentences = nlp_service.split_sentences("这是第一句。这是第二句！")
# ['这是第一句', '这是第二句']

# 提取关键词
text = "Python是一门编程语言。Java也是编程语言。"
keywords = nlp_service.extract_keywords(text, top_k=5, withWeight=True)
# [('编程', 0.85), ('语言', 0.82), ...]

# 提取关键句
key_sents = nlp_service.extract_key_sentences(text, top_k=2)
# ['Python是一门编程语言', 'Java也是编程语言']

# 获取文本统计
stats = nlp_service.get_text_stats(text)
# {'char_count': 30, 'word_count': 15, 'sentence_count': 2, ...}
```

### 2. DocumentGenerationService - 文档生成服务

**位置**：`backend/app/services/document_generation_service.py`

**功能模块**：

| 格式 | 方法 | 库 | 说明 | 优先级 |
|------|------|-----|------|--------|
| Markdown | `generate_markdown()` | - | 生成可编辑的Markdown格式 | p1 |
| PDF | `generate_pdf()` | reportlab | 生成专业的PDF文档 | p1 |
| Word | `generate_docx()` | python-docx | 生成Microsoft Word格式 | p2 |
| JSON | `generate_json()` | json | 生成结构化数据 | p0 |

**使用示例**：

```python
from app.services.document_generation_service import document_generation_service

meeting_data = {
    'date': '2026-01-25',
    'participants': ['张三', '李四', '王五'],
    'agendas': ['讨论项目计划', '技术方案评审', '资源分配'],
    'key_points': ['确定了项目截止期限', '通过了技术方案'],
    'decisions': ['决议1：采用方案A', '决议2：增加3人团队'],
    'action_items': [
        {'content': '编写详细技术文档', 'owner': '张三', 'due_date': '2026-02-01'},
        {'content': '准备演示方案', 'owner': '李四', 'due_date': '2026-01-30'},
    ]
}

# 生成Markdown
md_content = document_generation_service.generate_markdown(
    "Q1项目启动会议纪要",
    meeting_data
)

# 生成PDF
success = document_generation_service.generate_pdf(
    "Q1项目启动会议纪要",
    meeting_data,
    "./minutes.pdf"
)

# 生成Word
success = document_generation_service.generate_docx(
    "Q1项目启动会议纪要",
    meeting_data,
    "./minutes.docx"
)

# 生成JSON
json_str = document_generation_service.generate_json(meeting_data)
```

### 3. MeetingMinutesService - 纪要处理服务

**位置**：`backend/app/services/meeting_minutes_service.py`

**核心流程**：

```
上传和转录        文本处理        生成纪要        分享
(1-3步)          (4-9步)         (10-19步)      (20-23步)
    ↓               ↓                ↓             ↓
upload_and_    process_          generate_      send_email
transcribe     transcription      meeting_       share_
               minutes_           minutes
```

**主要方法**：

```python
# 步骤1-3：上传和转录
await service.upload_and_transcribe(meeting_id, file)

# 步骤4-9：处理转录文本
await service.process_transcription(meeting_id, transcription_text)

# 步骤10-19：生成纪要（多格式）
await service.generate_meeting_minutes(
    meeting_id,
    meeting_data,
    formats=['markdown', 'pdf', 'docx', 'json']
)

# 步骤20：邮件发送
await service.send_minutes_email(meeting_id, recipients, format='pdf')

# 步骤21-23：分享
await service.share_minutes(meeting_id, share_targets)
```

### 4. MeetingService - 会议管理服务

**位置**：`backend/app/services/meeting_service.py`

**职责**：

- 会议生命周期管理（创建、更新、删除）
- 集成MeetingMinutesService的各种处理
- 提供查询接口（参与人、议程、决议等）

---

## 🔌 API 端点完整列表

### CRUD 操作

```
POST   /api/v1/meetings                      创建会议
GET    /api/v1/meetings                      列表会议
GET    /api/v1/meetings/{meeting_id}         获取详情
PUT    /api/v1/meetings/{meeting_id}         更新会议
DELETE /api/v1/meetings/{meeting_id}         删除会议
```

### 会议处理流程

```
POST   /api/v1/meetings/{meeting_id}/upload              上传音视频 + 开始转录
POST   /api/v1/meetings/{meeting_id}/transcribe          手动触发转录
POST   /api/v1/meetings/{meeting_id}/process             处理转录文本 (NLP分析)
POST   /api/v1/meetings/{meeting_id}/generate-minutes    生成纪要 (多格式)
GET    /api/v1/meetings/{meeting_id}/minutes             获取纪要
POST   /api/v1/meetings/{meeting_id}/export              导出纪要
POST   /api/v1/meetings/{meeting_id}/send-email          邮件发送
POST   /api/v1/meetings/{meeting_id}/share               分享到其他平台
```

### 信息查询

```
GET    /api/v1/meetings/{meeting_id}/participants        获取参与人
GET    /api/v1/meetings/{meeting_id}/agendas            获取议程
GET    /api/v1/meetings/{meeting_id}/decisions          获取决议
GET    /api/v1/meetings/{meeting_id}/action-items       获取Action Items
```

---

## 🔄 完整使用流程

### 第1步：创建会议

```python
POST /api/v1/meetings
{
    "title": "Q1项目启动会",
    "meeting_type": "strategic_planning",
    "start_time": "2026-01-25T10:00:00",
    "location": "会议室A"
}

Response:
{
    "id": "meeting_001",
    "status": "created",
    "title": "Q1项目启动会",
    ...
}
```

### 第2步：上传音视频并开始转录

```python
POST /api/v1/meetings/meeting_001/upload
Form Data:
  file: <audio.mp3>

Response:
{
    "meeting_id": "meeting_001",
    "file_path": "./uploads/meeting_001_20260125_100000_audio.mp3",
    "transcription_task_id": "task_meeting_001_1706154000",
    "status": "transcribing",
    "message": "转录任务已启动"
}
```

### 第3步：处理转录文本（获取转录后）

```python
POST /api/v1/meetings/meeting_001/process
{
    "transcription_text": "各位好，今天我们来讨论Q1的项目计划......"
}

Response:
{
    "meeting_id": "meeting_001",
    "sentences": ["各位好", "今天我们来讨论Q1的项目计划", ...],
    "keywords": [("项目", 0.95), ("计划", 0.92), ...],
    "key_sentences": ["项目计划涉及三个部分...", ...],
    "entities": {
        "dates": ["2026-01-25"],
        "times": ["10:00"],
        ...
    },
    "topics": ["项目计划", "技术方案", "资源分配"],
    "agendas": ["议题: 项目计划", ...],
    "decisions": ["决议: 采用方案A", ...],
    "action_items": [
        {
            "content": "编写技术文档",
            "owner": "张三",
            "due_date": "待定"
        }
    ],
    "text_stats": {
        "char_count": 1500,
        "word_count": 750,
        "sentence_count": 45,
        ...
    }
}
```

### 第4步：生成纪要（多格式）

```python
POST /api/v1/meetings/meeting_001/generate-minutes
{
    "meeting_data": {
        // 来自处理步骤的数据
    },
    "formats": ["markdown", "pdf", "docx", "json"]
}

Response:
{
    "meeting_id": "meeting_001",
    "title": "会议纪要 - Q1项目启动会",
    "formats": {
        "markdown": {
            "content": "# 会议纪要\n...",
            "path": "./uploads/meeting_001_minutes.md"
        },
        "pdf": {
            "path": "./uploads/meeting_001_minutes.pdf"
        },
        "docx": {
            "path": "./uploads/meeting_001_minutes.docx"
        },
        "json": {
            "content": "{...}",
            "path": "./uploads/meeting_001_minutes.json"
        }
    }
}
```

### 第5步：邮件发送

```python
POST /api/v1/meetings/meeting_001/send-email
{
    "recipients": ["manager@company.com", "team@company.com"],
    "format": "pdf"
}

Response:
{
    "status": "sent",
    "recipients": 2,
    "format": "pdf",
    "message": "已发送至2个收件人"
}
```

### 第6步：分享到其他平台

```python
POST /api/v1/meetings/meeting_001/share
{
    "share_targets": {
        "wechat": ["group_id_123"],
        "dingtalk": ["dept_456"],
        "lark": ["channel_789"]
    }
}

Response:
{
    "status": "shared",
    "targets": {
        "wechat": {"status": "success", "count": 1},
        "dingtalk": {"status": "success", "count": 1},
        "lark": {"status": "success", "count": 1}
    }
}
```

---

## 🎯 如何复用表格标黄功能

### 场景1：在其他功能中提取关键词

```python
from app.services.nlp_service import nlp_service

# 文档总结
keywords = nlp_service.extract_keywords(document_text, top_k=10)

# 邮件分类
entities = nlp_service.extract_entities(email_body)

# 通知提醒
key_sentences = nlp_service.extract_key_sentences(notification_text)
```

### 场景2：生成不同类型的文档

```python
from app.services.document_generation_service import document_generation_service

# 周报生成
doc_service.generate_markdown("周报", weekly_data)
doc_service.generate_docx("周报", weekly_data, "./weekly_report.docx")

# PPT转录稿生成
doc_service.generate_pdf("演讲稿", ppt_data, "./speech.pdf")

# 项目总结
doc_service.generate_json(project_summary)
```

### 场景3：创建新的处理服务

```python
from app.services.nlp_service import nlp_service
from app.services.document_generation_service import document_generation_service

class WeeklyReportService:
    """周报生成服务 - 复用NLP和文档生成模块"""
    
    def __init__(self):
        self.nlp = nlp_service
        self.doc_gen = document_generation_service
    
    async def generate_weekly_report(self, activities: str):
        # 提取关键活动
        key_points = self.nlp.extract_key_sentences(activities, top_k=5)
        
        # 提取待办项
        todos = self.nlp.extract_entities(activities)
        
        # 生成周报
        report_data = {
            'week': '2026-01-20 to 2026-01-26',
            'key_activities': key_points,
            'todos': todos['dates']
        }
        
        # 输出多种格式
        markdown = self.doc_gen.generate_markdown('周报', report_data)
        self.doc_gen.generate_docx('周报', report_data, './weekly.docx')
```

---

## 🚀 依赖安装

### 必需依赖

```bash
# 已在 pyproject.toml 中配置
jieba               # 中文分词
transformers        # NLP模型
reportlab           # PDF生成
python-docx         # Word文档生成
```

### 可选依赖

```bash
# 增强NLP功能
python-dateutil     # 日期处理
spacy              # 更高级的NER
torch              # GPU支持

# 增强文档生成
Jinja2             # 模板引擎
weasyprint         # HTML转PDF
```

---

## ⚙️ 配置

### 环境变量 (core/config.py)

```python
# 文件上传
UPLOAD_DIR: str = "./uploads"
MAX_UPLOAD_SIZE: int = 500 * 1024 * 1024  # 500MB

# AI/ML配置
HF_MODEL_DEVICE: str = "cuda"  # 或 "cpu"
SUMMARIZATION_MODEL: str = "facebook/bart-large-cnn"
EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

# LLM API（可选）
QWEN_API_KEY: str = ""  # 用于高级话题划分和决议识别

# 邮件配置
SMTP_SERVER: str = "smtp.gmail.com"
SMTP_PORT: int = 587
SMTP_USER: str = ""
SMTP_PASSWORD: str = ""
```

---

## 📊 数据流图

```
输入: 音视频文件
  ↓
[上传和转录] (API: /upload, /transcribe)
  ↓
输出: 转录文本
  ↓
[NLP处理] (API: /process, Service: NLPService)
  ├─ 分句分段 → 句子列表
  ├─ 关键词提取 → 关键词列表
  ├─ 关键句提取 → 关键句
  ├─ 实体识别 → 人名、日期等
  ├─ 话题划分 → 话题列表
  └─ 决议提取 → 决议和Action Items
  ↓
输出: 结构化数据
  ↓
[文档生成] (API: /generate-minutes, Service: DocumentGenerationService)
  ├─ Markdown格式
  ├─ PDF格式
  ├─ Word格式
  └─ JSON格式
  ↓
输出: 多种格式纪要
  ↓
[分享和发送] (API: /send-email, /share)
  ├─ 邮件发送
  ├─ 企业微信
  ├─ 钉钉
  └─ 飞书
  ↓
结束
```

---

## 🔍 测试和验证

### 单元测试示例

```python
from app.services.nlp_service import nlp_service
from app.services.document_generation_service import document_generation_service

# 测试关键词提取
def test_keyword_extraction():
    text = "Python是一门编程语言。Java也是编程语言。"
    keywords = nlp_service.extract_keywords(text, top_k=3)
    assert len(keywords) <= 3
    assert all(isinstance(kw, tuple) for kw in keywords)

# 测试Markdown生成
def test_markdown_generation():
    data = {
        'date': '2026-01-25',
        'participants': ['张三'],
        'agendas': ['议题1'],
        'decisions': ['决议1']
    }
    result = document_generation_service.generate_markdown("测试", data)
    assert "# 测试" in result
    assert "会议日期" in result
```

---

## 💡 最佳实践

1. **分离关注点**：使用专门的服务处理特定功能
2. **错误处理**：所有服务方法都应该包含try-except并记录日志
3. **缓存优化**：对频繁使用的NLP模型进行缓存
4. **异步处理**：长时间操作（转录、生成文档）使用异步任务
5. **参数验证**：API端点应验证输入数据的合法性

---

## 📝 更新日志

**v1.0.0** (2026-01-25)
- ✅ 实现完整的会议纪要处理系统
- ✅ 集成NLP文本处理模块
- ✅ 支持多格式文档生成
- ✅ 完成API端点设计
