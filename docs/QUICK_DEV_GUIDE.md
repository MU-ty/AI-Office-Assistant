# 后端开发快速指南

## 项目现状

✅ **已完成**:
- FastAPI应用框架
- 数据库配置
- 日志系统
- 所有API路由定义 (8个模块)
- Service类框架
- 项目依赖配置

⏳ **待实现**:
- ORM数据模型 (`models/`)
- Pydantic验证schema (`schemas/`)
- 业务逻辑代码 (`services/` 中的具体实现)
- 异步任务处理 (`tasks/`)
- 单元测试 (`tests/`)

---

## 按优先级开发顺序

### 优先级 P0 (基础架构) - Week 1

#### 1. 实现用户模型和服务 (2天)

**文件**:
- `app/models/user.py` - User, UserSession, APIKey, UserProfile
- `app/schemas/user.py` - UserCreate, UserResponse, UserUpdate, UserLogin

**关键方法**:
```python
# UserService 需要实现的方法
- register_user(user_data: UserCreate)           # 新用户注册
- login_user(username, password)                 # 用户登录,返回JWT
- refresh_access_token(refresh_token)            # 刷新令牌
- get_user_by_id(user_id)                        # 获取用户信息
- update_user(user_id, user_data)                # 更新用户
- verify_password(plain, hashed)                 # 密码验证
- generate_jwt_token(user_id)                    # JWT生成
```

**完成标志**: 能在 `/api/docs` 中测试注册和登录端点

---

#### 2. 实现会议数据模型 (2天)

**文件**:
- `app/models/meeting.py` - 8个关联表
- `app/schemas/meeting.py` - 对应的Pydantic模型

**核心表**:
```python
Meeting
  ├─ MeetingParticipant
  ├─ MeetingContent (转录文本)
  ├─ MeetingAgenda
  ├─ MeetingDecision
  ├─ ActionItem
  └─ MeetingMinutes
```

**完成标志**: 能创建会议并存储到数据库

---

#### 3. 实现文献数据模型 (2天)

**文件**:
- `app/models/document.py` - 6个关联表
- `app/schemas/document.py` - 对应的Pydantic模型

**核心表**:
```python
Document
  ├─ DocumentSummary (3个级别的摘要)
  ├─ DocumentConcept (关键概念)
  ├─ DocumentCitation (引用关系)
  ├─ DocumentVector (向量存储)
  ├─ DocumentTag (标签)
  └─ DocumentCollection (集合)
```

**完成标志**: 能上传和存储文献文档

---

### 优先级 P1 (核心业务) - Week 2-3

#### 4. 实现会议处理服务 (3天)

**MeetingService 核心方法**:
```python
async def upload_media(meeting_id, file):
    # 1. 验证文件
    # 2. 保存文件到存储
    # 3. 创建MeetingContent记录
    # 4. 触发转录任务 (Celery)
    
async def start_transcription(meeting_id):
    # 调用 meeting_tasks.transcribe_meeting_audio(meeting_id)
    
async def generate_minutes(meeting_id):
    # 1. 获取转录文本
    # 2. 提取议程、决议、Action Items
    # 3. 生成执行摘要
    # 4. 保存 MeetingMinutes 记录
```

**异步任务** (`tasks/meeting_tasks.py`):
```python
@celery_app.task
def transcribe_meeting_audio(meeting_id: str):
    # 使用 Whisper 模型转录
    
@celery_app.task
def extract_meeting_entities(meeting_id: str):
    # NER 提取参与人、议程等
    
@celery_app.task
def extract_action_items(meeting_id: str):
    # 依存分析提取 Action Items
```

**完成标志**: 能上传音频并生成初步纪要

---

#### 5. 实现文献处理服务 (3天)

**DocumentService 核心方法**:
```python
async def create_document(title, file):
    # 1. 保存文件
    # 2. 解析PDF/文本
    # 3. 提取元数据
    # 4. 触发概念提取和向量化任务
    
async def generate_summary(doc_id, level):
    # 调用 BART/Pegasus 模型生成摘要
    
async def extract_concepts(doc_id):
    # NER + SciBERT 提取学术术语
    
async def search_similar(query, limit):
    # 向量相似度搜索
```

**异步任务** (`tasks/document_tasks.py`):
```python
@celery_app.task
def extract_document_concepts(doc_id: str):
    # 使用 spaCy 和 SciBERT
    
@celery_app.task
def vectorize_document(doc_id: str):
    # 向量化并上传到 Pinecone
```

**完成标志**: 能上传文献并生成多级摘要

---

### 优先级 P2 (其他模块) - Week 3-4

#### 6. 实现学术润色服务 (2天)

**PolishService**:
```python
async def create_task(task_data):
    # 触发语法检查任务
    
async def get_issues(task_id):
    # 返回问题列表
```

**异步任务**:
```python
@celery_app.task
def check_grammar_and_style(task_id: str):
    # 使用 LanguageTool 和自定义规则
```

---

#### 7. 实现翻译服务 (2天)

**TranslationService**:
```python
async def create_task(task_data):
    # 触发翻译任务
```

**异步任务**:
```python
@celery_app.task
def translate_text(task_id: str):
    # 调用翻译API (DeepL/Google/Azure)
```

---

#### 8. 实现PPT生成服务 (2天)

**PPTService**:
```python
async def generate_slides(project_id):
    # 生成幻灯片
```

**异步任务**:
```python
@celery_app.task
def generate_ppt_slides(project_id: str):
    # 使用 python-pptx 生成
```

---

#### 9. 实现周报服务 (2天)

**ReportService**:
```python
async def create_report(report_data):
    # 聚合工作日志
    
async def generate_weekly_report(user_id, week):
    # 自动生成周报内容
```

---

## 具体实现示例

### 示例 1: 实现用户注册

**Step 1**: 创建 `models/user.py`
```python
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_email_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
```

**Step 2**: 创建 `schemas/user.py`
```python
from pydantic import BaseModel, EmailStr
from uuid import UUID

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str

class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    full_name: str
    is_active: bool
    
    class Config:
        from_attributes = True
```

**Step 3**: 在 `services/user_service.py` 中实现逻辑
```python
async def register_user(self, user_data: UserCreate) -> UserResponse:
    # 检查用户是否存在
    existing = await self.db.execute(
        select(User).where(User.email == user_data.email)
    )
    if existing.scalar():
        raise UserAlreadyExistsError("邮箱已被注册")
    
    # 密码加密
    hashed_pwd = await self.hash_password(user_data.password)
    
    # 创建用户
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pwd,
        full_name=user_data.full_name
    )
    self.db.add(new_user)
    await self.db.commit()
    await self.db.refresh(new_user)
    
    return UserResponse.from_orm(new_user)
```

---

## 测试你的实现

### 运行单个服务测试
```bash
pytest tests/test_users.py -v
```

### 通过API文档测试
```
1. 启动应用: uvicorn app.main:app --reload
2. 访问: http://localhost:8000/api/docs
3. 在Swagger UI中测试端点
```

### 检查日志
```bash
tail -f logs/office_assistant.log
```

---

## 关键实现提示

### 1. 使用异步数据库操作
```python
# ✅ 正确
result = await db.execute(select(User))

# ❌ 错误
result = db.execute(select(User))
```

### 2. 总是处理异常
```python
try:
    await service.create_user(data)
except UserAlreadyExistsError:
    raise HTTPException(status_code=400, detail="用户已存在")
except Exception as e:
    logger.error(f"创建用户失败: {e}")
    raise HTTPException(status_code=500, detail="服务器错误")
```

### 3. 记录关键操作
```python
logger.info(f"创建新用户: {user_data.email}")
logger.error(f"邮件验证失败: {error}")
```

### 4. 使用Celery处理长操作
```python
# 不要在API中做这个
# ❌ await transcribe_audio(file)  # 可能要5分钟

# 改为异步任务
# ✅ transcribe_audio.delay(meeting_id)  # 立即返回
```

---

## 常见错误和解决

| 问题 | 原因 | 解决 |
|------|------|------|
| `No such table` | 模型没创建表 | 运行: `python scripts/init_db.py` |
| `Timeout` | 数据库连接问题 | 检查PostgreSQL是否运行 |
| `JWT error` | 令牌过期 | 使用refresh_token获取新令牌 |
| `CORS error` | 前端请求被拦截 | 检查 `config.py` 中的CORS设置 |

---

## 提交代码检查清单

- [ ] 所有方法都有类型注解
- [ ] 关键操作都有日志记录
- [ ] 异常都被正确处理
- [ ] 数据验证使用了Pydantic schemas
- [ ] 代码通过了 `black` 和 `flake8` 检查
- [ ] 编写了基本的单元测试
- [ ] 在 `http://localhost:8000/api/docs` 中能测试

---

## 联系方式

有问题请查看:
1. [规划书](./../../详细技术规划书.md)
2. [数据库设计](./../../完整数据库设计.md)
3. [FastAPI官方文档](https://fastapi.tiangolo.com/)

---

**更新时间**: 2026-01-24
**下一阶段**: 实现 UserService 和会议模型
**预计用时**: 1-2周
