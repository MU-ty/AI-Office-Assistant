# Office Assistant Agent - 后端

## 快速开始

### 1. 环境设置

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -e ".[dev]"
```

### 2. 配置数据库

```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env 文件，设置数据库连接信息
# 需要先启动 PostgreSQL 和 Redis
```

### 3. 初始化数据库

```bash
# 使用 Alembic 迁移
alembic init migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 4. 启动服务

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

服务将在 `http://localhost:8000` 启动

### 5. 访问API文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 项目结构

```
backend/
├── app/
│   ├── core/              # 核心配置
│   │   └── config.py      # 应用配置
│   ├── api/               # API路由
│   │   ├── health.py      # 健康检查
│   │   └── users.py       # 用户接口
│   ├── models/            # 数据库模型
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── task.py
│   │   └── document.py
│   ├── services/          # 业务逻辑层
│   │   └── base.py
│   ├── db/                # 数据库连接
│   │   └── database.py
│   ├── utils/             # 工具函数
│   │   ├── logger.py
│   │   └── exceptions.py
│   └── main.py            # 应用工厂
├── tests/                 # 测试
├── main.py                # 应用入口
├── pyproject.toml         # 项目配置
├── .env.example           # 环境变量示例
└── README.md              # 项目文档
```

## 依赖说明

- **fastapi**: Web框架
- **uvicorn**: ASGI服务器
- **sqlalchemy**: ORM框架
- **pydantic**: 数据验证
- **langchain**: LLM集成
- **dashscope**: 阿里云通义千问API
- **python-pptx**: PPT生成
- **redis**: 缓存

## 开发规范

### 代码风格

使用 Black 进行代码格式化：
```bash
black app/ tests/ main.py
```

使用 Ruff 进行linting：
```bash
ruff check app/ tests/
```

### 类型检查

```bash
mypy app/
```

### 测试

```bash
pytest tests/ -v
```

## 接口设计

### 基础接口

- `GET /` - 根路由
- `GET /api/v1/health` - 健康检查
- `GET /api/v1/health/ready` - 就绪检查

### 用户接口

- `GET /api/v1/users` - 获取用户列表
- `GET /api/v1/users/{user_id}` - 获取用户详情

## 下一步

1. 实现各功能模块的服务层
2. 完成数据库迁移
3. 添加认证和授权
4. 实现业务逻辑API
5. 添加单元测试和集成测试
