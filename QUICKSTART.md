# 快速开始指南 - 认证与授权系统

## 🚀 5 分钟快速启动

### 步骤 1：环境准备

```bash
# 进入项目目录
cd /mnt/f/officeAgent/AI-Office-Assistant

# 检查容器状态
docker compose ps
```

应该能看到 9 个中间件容器都在运行。

### 步骤 2：构建并启动后端服务

```bash
# 方法 A: 直接构建和启动（推荐）
docker compose up -d --build backend

# 方法 B: 仅构建（不启动）
docker build -t office-assistant-backend:latest -f backend/Dockerfile .

# 方法 C: 本地开发（不用 Docker）
cd backend
pip install -r requirements.txt
cp .env.example ../.env
# 编辑 .env 文件
uvicorn app.main:app --reload
```

### 步骤 3：验证服务是否运行

```bash
# 检查后端容器
docker compose ps | grep backend

# 查看日志
docker compose logs -f backend

# 测试 API
curl http://localhost:8000/health
```

预期输出：

```json
{ "status": "ok", "version": "1.0.0" }
```

### 步骤 4：访问 API 文档

打开浏览器访问：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📝 测试认证流程

### 1. 用户注册

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass123",
    "full_name": "Test User"
  }'
```

预期响应：

```json
{
  "message": "注册成功，请登录",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "testuser",
  "email": "test@example.com"
}
```

### 2. 用户登录

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPass123"
  }'
```

预期响应：

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 1800
}
```

**保存 `access_token`，以下使用 `<token>` 表示**

### 3. 获取当前用户

```bash
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer <token>"
```

### 4. 刷新令牌

```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "<refresh_token>"
  }'
```

---

## 🔧 配置说明

### 配置文件位置

1. **后端配置**: `backend/app/core/config.py`
2. **环境变量**: `.env` (复制自 `backend/.env.example`)
3. **数据库配置**: `docker-compose.yml` (数据库连接信息)

### 关键环境变量

```bash
# JWT 配置
JWT_SECRET_KEY=your-secret-key                    # 修改为强密钥！
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30               # 访问令牌过期时间
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7                  # 刷新令牌过期时间

# 数据库
DATABASE_HOST=office_assistant_postgres
DATABASE_NAME=office_assistant
DATABASE_USER=office_user
DATABASE_PASSWORD=office_password

# Redis
REDIS_HOST=office_assistant_redis
REDIS_PORT=6379

# 密码策略
PASSWORD_MIN_LENGTH=8
PASSWORD_REQUIRE_UPPERCASE=True
PASSWORD_REQUIRE_NUMBERS=True
```

### 生成强密钥

```bash
# Python
python -c "import secrets; print(secrets.token_hex(32))"

# Shell
openssl rand -hex 32
```

---

## 📂 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI 应用入口
│   ├── schemas.py                   # Pydantic 数据模型
│   ├── core/
│   │   ├── config.py               # 配置管理
│   │   └── __init__.py
│   ├── auth/
│   │   ├── jwt.py                  # JWT 处理
│   │   ├── password.py             # 密码加密
│   │   ├── dependencies.py         # 依赖注入
│   │   └── __init__.py
│   ├── db/
│   │   ├── database.py             # 数据库连接
│   │   ├── models.py               # SQLAlchemy 模型
│   │   └── __init__.py
│   └── api/
│       ├── __init__.py
│       └── routes/
│           ├── auth.py             # 认证路由
│           ├── users.py            # 用户路由
│           └── __init__.py
├── Dockerfile
├── .dockerignore
├── requirements.txt
└── .env.example
```

---

## 🐛 常见问题

### Q: 启动后端时出现数据库连接错误

**A**:

1. 确保 PostgreSQL 容器已启动: `docker compose ps | grep postgres`
2. 检查 `.env` 中的数据库配置是否正确
3. 等待 30 秒让数据库完全启动

### Q: 访问 API 提示 404 Not Found

**A**:

1. 确认后端容器正在运行: `docker compose ps backend`
2. 访问 `http://localhost:8000/health` 测试基本连接
3. 检查 API 路径是否正确 (应该是 `/api/v1/...`)

### Q: 登录后提示 Token 无效

**A**:

1. 确保 `JWT_SECRET_KEY` 在 `.env` 中设置了
2. 不要修改 `JWT_ALGORITHM` (应该保持为 `HS256`)
3. 检查请求头格式: `Authorization: Bearer <token>`

### Q: 密码验证失败

**A**:

- 密码必须至少 8 个字符
- 必须包含至少一个大写字母
- 必须包含至少一个数字
- 可选：包含特殊字符 (!@#$%^&\*)

---

## 📊 监控和日志

### 查看实时日志

```bash
# 所有服务日志
docker compose logs -f

# 仅后端日志
docker compose logs -f backend

# 仅数据库日志
docker compose logs -f postgres
```

### 进入容器调试

```bash
# 进入后端容器
docker compose exec backend bash

# 在容器内运行 Python
docker compose exec backend python
>>> from app.db.database import SessionLocal
>>> db = SessionLocal()
>>> print(db.query(User).count())
```

---

## 🚀 下一步

完成认证系统后，可以继续开发：

1. **前端应用** - React + TypeScript + Vite
2. **API 网关** - Nginx 配置
3. **其他业务逻辑** - 文献处理、会议纪要等
4. **微服务扩展** - 任务处理器、AI 服务等

详见 [容器化规划方案.md](容器化规划方案.md)

---

## 📚 完整文档

详细的 API 文档、安全最佳实践、高级配置见 [认证授权系统文档.md](认证授权系统文档.md)

---

## 💡 开发提示

### 本地快速测试

```bash
# 1. 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 2. 安装依赖
pip install -r backend/requirements.txt

# 3. 设置环境变量
export DATABASE_HOST=localhost  # 确保能访问本地 Docker
export REDIS_HOST=localhost

# 4. 运行开发服务器
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 数据库迁移（如需要）

```bash
# 初始化 alembic
alembic init migrations

# 自动生成迁移脚本
alembic revision --autogenerate -m "initial migration"

# 应用迁移
alembic upgrade head
```

---

最后更新: 2024-01-23
快速开始指南版本: 1.0
