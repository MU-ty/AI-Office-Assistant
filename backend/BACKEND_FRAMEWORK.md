# 办公助手Agent - 后端框架设计文档

## 项目概述

这是一个基于 **FastAPI + PostgreSQL + Redis** 的高性能后端框架，为6个功能模块提供支持。框架采用分层架构，便于逐个实现业务逻辑。

---

## 目录结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI应用入口
│   │
│   ├── core/                        # 核心配置
│   │   ├── __init__.py
│   │   ├── config.py                # 环境变量和配置 ✅
│   │   └── database.py              # 数据库连接管理 ✅
│   │
│   ├── api/                         # API路由层 (已完成框架)
│   │   ├── __init__.py
│   │   ├── health.py                # 健康检查 ✅
│   │   ├── users.py                 # 用户认证 ✅
│   │   ├── meetings.py              # 会议纪要 ✅
│   │   ├── documents.py             # 文献摘要 ✅
│   │   ├── polish_tasks.py          # 学术润色 ✅
│   │   ├── translation_tasks.py     # 多语言翻译 ✅
│   │   ├── ppt_projects.py          # PPT生成 ✅
│   │   └── weekly_reports.py        # 周报生成 ✅
│   │
│   ├── services/                    # 业务逻辑层 (框架已建立)
│   │   ├── __init__.py
│   │   ├── base.py                  # 基础服务类
│   │   ├── user_service.py          # 用户服务 (框架 + 待实现)
│   │   ├── meeting_service.py       # 会议服务 (框架 + 待实现)
│   │   ├── document_service.py      # 文献服务 (框架 + 待实现)
│   │   ├── polish_service.py        # 润色服务
│   │   ├── translation_service.py   # 翻译服务
│   │   ├── ppt_service.py           # PPT服务
│   │   ├── report_service.py        # 报告服务
│   │   └── base_services.py         # 其他模块占位符 ✅
│   │
│   ├── models/                      # 数据模型层 (ORM模型)
│   │   ├── __init__.py
│   │   ├── base.py                  # 基础模型
│   │   ├── user.py                  # 用户模型
│   │   ├── meeting.py               # 会议模型
│   │   ├── document.py              # 文献模型
│   │   ├── polish.py                # 润色模型
│   │   ├── translation.py           # 翻译模型
│   │   ├── ppt.py                   # PPT模型
│   │   └── report.py                # 报告模型
│   │
│   ├── schemas/                     # 数据验证层 (Pydantic模型)
│   │   ├── __init__.py
│   │   ├── base.py                  # 基础schema
│   │   ├── user.py                  # 用户schema
│   │   ├── meeting.py               # 会议schema
│   │   ├── document.py              # 文献schema
│   │   ├── polish.py                # 润色schema
│   │   ├── translation.py           # 翻译schema
│   │   ├── ppt.py                   # PPT schema
│   │   └── report.py                # 报告schema
│   │
│   ├── utils/                       # 工具模块
│   │   ├── __init__.py
│   │   ├── logger.py                # 日志系统 ✅
│   │   ├── exceptions.py            # 自定义异常
│   │   ├── auth.py                  # JWT认证工具
│   │   ├── cache.py                 # Redis缓存工具
│   │   ├── file_handler.py          # 文件处理工具
│   │   └── validators.py            # 数据验证器
│   │
│   └── tasks/                       # 异步任务 (Celery)
│       ├── __init__.py
│       ├── celery_config.py         # Celery配置
│       ├── meeting_tasks.py         # 会议处理任务
│       ├── document_tasks.py        # 文献处理任务
│       ├── polish_tasks.py          # 润色处理任务
│       ├── translation_tasks.py     # 翻译处理任务
│       ├── ppt_tasks.py             # PPT生成任务
│       └── report_tasks.py          # 报告生成任务
│
├── migrations/                      # 数据库迁移 (Alembic)
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 001_initial_schema.py
│
├── tests/                           # 单元测试
│   ├── conftest.py                  # pytest配置
│   ├── test_users.py
│   ├── test_meetings.py
│   ├── test_documents.py
│   └── ...
│
├── scripts/                         # 工具脚本
│   ├── init_db.py                   # 初始化数据库
│   ├── seed_data.py                 # 导入测试数据
│   └── generate_docs.py             # 生成API文档
│
├── .env.example                     # 环境变量示例
├── .gitignore
├── pyproject.toml                   # 项目配置 (UV管理)
├── requirements.txt
├── docker-compose.yml               # Docker编排
├── Dockerfile                       # Docker镜像
├── README.md
└── BACKEND_DEV_GUIDE.md             # 开发指南
```

---

## 架构层次说明

### 1. API 路由层 (`api/`)
**职责**: 接收HTTP请求，参数验证，调用服务层

```python
# 示例: users.py
@router.post("/register")
async def register(user_data: UserCreate, db = Depends(get_db)):
    service = UserService(db)
    return await service.register_user(user_data)
```

**现状**: ✅ 所有8个模块的路由框架已完成

---

### 2. 服务业务层 (`services/`)
**职责**: 处理业务逻辑，调用模型层，触发异步任务

```python
# 示例: user_service.py
class UserService:
    async def register_user(self, user_data: UserCreate):
        # TODO: 检查用户是否存在
        # TODO: 密码加密
        # TODO: 创建用户记录
        # TODO: 返回结果
        pass
```

**现状**: 
- ✅ Service类框架已建立
- ⏳ 具体业务逻辑需要实现 (待开发)

---

### 3. 数据模型层 (`models/`)
**职责**: SQLAlchemy ORM模型，定义数据库表结构

**需要实现**:
```python
# 示例: models/user.py
from sqlalchemy import Column, String, UUID
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(UUID, primary_key=True)
    username = Column(String(50), unique=True)
    email = Column(String(100), unique=True)
    hashed_password = Column(String(255))
    # ... 其他字段
```

---

### 4. 数据验证层 (`schemas/`)
**职责**: Pydantic模型，验证请求和响应数据

**需要实现**:
```python
# 示例: schemas/user.py
from pydantic import BaseModel, EmailStr

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
```

---

### 5. 异步任务层 (`tasks/`)
**职责**: Celery异步任务，处理长时间运行的操作

**需要实现**:
```python
# 示例: tasks/meeting_tasks.py
@celery_app.task
def transcribe_meeting_audio(meeting_id: str):
    # 1. 获取音频文件
    # 2. 使用Whisper模型转录
    # 3. 保存转录文本
    # 4. 触发NLP处理
    pass
```

---

## 开发步骤指南

### Phase 1: 基础设施 (已完成 ✅)
- [x] 数据库连接配置
- [x] FastAPI应用设置
- [x] 中间件和异常处理
- [x] 日志系统
- [x] API路由框架
- [x] Service类框架

### Phase 2: 数据模型实现 (待做)

**第1步**: 实现所有ORM模型 (`models/`)
```bash
# 模型列表
- models/user.py           # 用户模型
- models/meeting.py        # 会议及相关模型
- models/document.py       # 文献及相关模型
- models/polish.py         # 润色模型
- models/translation.py    # 翻译模型
- models/ppt.py            # PPT模型
- models/report.py         # 报告模型
```

参考: `init_schema.sql` 中的表结构

### Phase 3: 数据验证实现 (待做)

**第2步**: 实现所有Pydantic schemas (`schemas/`)
```bash
- schemas/user.py
- schemas/meeting.py
- schemas/document.py
- schemas/polish.py
- schemas/translation.py
- schemas/ppt.py
- schemas/report.py
```

### Phase 4: 业务逻辑实现 (待做)

**第3步**: 按功能优先级实现服务层
```
优先级1 (第1周): 
  - UserService (用户认证)
  - MeetingService (核心模块)
  - DocumentService (核心模块)

优先级2 (第2周):
  - PolishService
  - TranslationService

优先级3 (第3周):
  - PPTService
  - ReportService
```

### Phase 5: 异步任务实现 (待做)

**第4步**: 实现Celery异步任务
```
- 音频转录任务
- 文献处理任务
- 文本润色任务
- PPT生成任务
- 周报编译任务
```

### Phase 6: 测试和部署 (待做)

**第5步**: 编写单元测试
```bash
- tests/test_users.py
- tests/test_meetings.py
- tests/test_documents.py
- ...
```

---

## 快速启动

### 1. 安装依赖
```bash
cd backend
pip install -r requirements.txt
# 或使用UV
uv sync
```

### 2. 配置环境
```bash
cp .env.example .env
# 编辑 .env 填入PostgreSQL和Redis连接信息
```

### 3. 初始化数据库
```bash
# 使用SQL脚本初始化
psql -U postgres -d office_assistant -f ../init_schema.sql

# 或使用Alembic迁移
alembic upgrade head
```

### 4. 启动应用
```bash
# 开发模式 (自动重载)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或使用
uvicorn app.main:app --reload
```

### 5. 查看API文档
```
http://localhost:8000/api/docs
```

---

## 关键文件说明

| 文件 | 说明 | 状态 |
|------|------|------|
| `main.py` | FastAPI应用入口 | ✅ 完成 |
| `config.py` | 环境配置 | ✅ 完成 |
| `database.py` | 数据库连接 | ✅ 完成 |
| `logger.py` | 日志系统 | ✅ 完成 |
| `api/*.py` | API路由 | ✅ 完成 |
| `services/*.py` | 业务逻辑 | ⏳ 框架完成, 逻辑待实现 |
| `models/*.py` | 数据模型 | ⏳ 待实现 |
| `schemas/*.py` | 数据验证 | ⏳ 待实现 |
| `tasks/*.py` | 异步任务 | ⏳ 待实现 |

---

## 技术栈

| 模块 | 技术 | 版本 |
|------|------|------|
| Web框架 | FastAPI | 0.104+ |
| 异步服务器 | Uvicorn | 最新 |
| ORM | SQLAlchemy | 2.0+ |
| 数据库 | PostgreSQL | 15+ |
| 缓存 | Redis | 7.0+ |
| 任务队列 | Celery | 5.3+ |
| 数据验证 | Pydantic | 2.0+ |
| 测试框架 | pytest | 最新 |

---

## 下一步行动

1. **完成数据模型** (`models/`)
   - 参考 `init_schema.sql` 创建SQLAlchemy模型
   - 确保所有表和关系正确映射

2. **实现数据验证** (`schemas/`)
   - 为每个API端点创建请求/响应schema
   - 添加字段验证和类型检查

3. **实现业务逻辑** (`services/`)
   - 从UserService开始
   - 逐个实现每个模块的核心功能

4. **配置异步任务** (`tasks/`)
   - 设置Celery worker
   - 实现长时间运行的处理任务

5. **编写测试** (`tests/`)
   - 为每个服务层编写单元测试
   - 集成测试API端点

---

## 参考资源

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy 官方文档](https://docs.sqlalchemy.org/)
- [Pydantic 官方文档](https://docs.pydantic.dev/)
- [PostgreSQL 官方文档](https://www.postgresql.org/docs/)
- [Redis 官方文档](https://redis.io/documentation)

---

**框架完成时间**: 2026-01-24
**下一阶段**: 数据模型实现
**预计工期**: 13周 (根据3人团队计划)
