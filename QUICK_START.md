# 🚀 快速开始指南

## 系统要求

- Windows/Linux/macOS
- Python 3.10 或更高版本
- Node.js 16 或更高版本
- Docker 和 Docker Compose
- PostgreSQL 15（通过Docker运行）
- Redis 7（通过Docker运行）

## 📦 一键启动（推荐）

### Windows (PowerShell)

```powershell
# 1. 启动所有后端依赖服务
docker-compose up -d

# 2. 启动后端
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -e ".[dev]"
cp .env.example .env
python scripts/init_db.py
python main.py

# 3. 在新终端启动前端
cd frontend
npm install
npm run dev
```

### Linux / macOS

```bash
# 1. 启动所有后端依赖服务
docker-compose up -d

# 2. 启动后端
cd backend
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
python scripts/init_db.py
python main.py

# 3. 在新终端启动前端
cd frontend
npm install
npm run dev
```

## 🔍 验证安装

启动后检查以下地址：

- **前端应用**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **数据库**: 通过DBeaver连接到 `localhost:5432`
- **Redis**: 连接到 `localhost:6379`

## 📋 详细安装步骤

### Step 1: 启动Docker服务

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

这会启动：
- PostgreSQL (端口 5432)
- Redis (端口 6379)
- Weaviate (端口 8080)

### Step 2: 配置后端

```bash
cd backend

# 创建Python虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -e ".[dev]"

# 复制环境文件
cp .env.example .env

# 编辑 .env 文件（可选，使用默认配置）
# .env 中的默认配置应该可以正常工作
```

### Step 3: 初始化数据库

```bash
# 在 backend 目录下运行
python scripts/init_db.py

# 输出应该包含:
# 开始初始化数据库...
# 数据库表创建成功
# 示例用户创建成功: admin
# 数据库初始化完成！
```

### Step 4: 启动后端服务

```bash
# 在 backend 目录下运行
python main.py

# 或使用 uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 输出应该包含:
# 启动应用: Office Assistant Agent v0.1.0
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 5: 启动前端应用

打开新终端：

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 输出应该包含:
# VITE v5.0.0  ready in XXX ms
# ➜  Local:   http://localhost:3000/
```

## 🧪 测试连接

打开浏览器访问：

```
http://localhost:3000
```

应该看到：
- 办公助手Agent主页
- 系统状态卡片显示 "✓ 运行中"
- 六个功能模块的介绍卡片

## ⚙️ 环境变量配置

### 后端 (.env)

```bash
# 应用配置
APP_NAME=Office Assistant Agent
APP_VERSION=0.1.0
DEBUG=true
LOG_LEVEL=INFO

# 数据库配置（使用Docker的默认值）
DATABASE_URL=postgresql://office_user:office_password@localhost:5432/office_assistant
REDIS_URL=redis://localhost:6379/0

# JWT配置
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256

# LLM配置（可选，后续需要配置）
QWEN_API_KEY=your-qwen-api-key
OPENAI_API_KEY=your-openai-api-key

# 翻译服务
DEEPL_API_KEY=your-deepl-api-key
```

### 前端配置

前端通过 `vite.config.ts` 配置API代理，自动将 `/api` 请求转发到后端。

## 🔧 常见问题排查

### 问题1: 端口被占用

```bash
# 查看端口占用情况
# Windows:
netstat -ano | findstr :8000

# Linux/Mac:
lsof -i :8000

# 杀死进程后重试
```

### 问题2: 数据库连接失败

```bash
# 检查Docker服务是否运行
docker-compose ps

# 如果PostgreSQL未运行：
docker-compose up -d postgres

# 检查连接
psql -h localhost -U office_user -d office_assistant -c "SELECT 1"
```

### 问题3: 前端无法连接后端

- 检查后端是否运行在 `http://localhost:8000`
- 检查 `vite.config.ts` 中的代理配置
- 检查浏览器控制台的网络错误

### 问题4: npm依赖安装慢

```bash
# 使用淘宝镜像
npm install -g cnpm --registry=https://registry.npm.taobao.org
cnpm install
```

### 问题5: Python虚拟环境问题

```bash
# 删除旧的虚拟环境
rm -rf backend/venv  # Linux/Mac
rmdir /s backend\venv  # Windows

# 重新创建
python -m venv venv
```

## 📚 常用命令

### 后端开发

```bash
# 启动开发服务（自动重载）
python main.py

# 运行测试
pytest tests/ -v

# 代码格式化
black app/ tests/

# 代码检查
ruff check app/

# 类型检查
mypy app/
```

### 前端开发

```bash
# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 代码检查
npm run lint

# 预览构建结果
npm run preview
```

### Docker命令

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 查看日志
docker-compose logs -f

# 进入PostgreSQL容器
docker-compose exec postgres psql -U office_user -d office_assistant

# 清理所有数据
docker-compose down -v
```

## 📖 下一步

1. **阅读开发指南**
   - [后端开发指南](../docs/BACKEND_DEV_GUIDE.md)
   - [前端开发指南](../docs/FRONTEND_DEV_GUIDE.md)

2. **配置IDE**
   - VS Code Python扩展
   - Prettier和ESLint
   - Thunder Client或Postman测试API

3. **开始开发**
   - 实现会议纪要处理模块
   - 实现文献摘要提取模块
   - 实现学术文献润色模块
   - ... 其他功能模块

4. **部署**
   - Docker镜像构建
   - 云平台部署（AWS/阿里云/腾讯云）
   - CI/CD流程配置

## 🆘 获取帮助

- 查看项目文档：[docs/](../docs/)
- 查看API文档：http://localhost:8000/docs
- GitHub Issue：[报告问题]
- 邮件支持：team@officeassistant.com

## ✅ 快速检查清单

- [ ] Docker已安装并运行
- [ ] PostgreSQL容器已启动
- [ ] Redis容器已启动
- [ ] 后端虚拟环境已激活
- [ ] 后端依赖已安装
- [ ] 数据库已初始化
- [ ] 后端服务运行在 http://localhost:8000
- [ ] 前端依赖已安装
- [ ] 前端应用运行在 http://localhost:3000
- [ ] 能够访问前端首页
- [ ] 能够访问API文档 http://localhost:8000/docs

---

**如果一切正常，恭喜！🎉 您已经成功启动了办公助手Agent应用！**

**现在可以开始开发了！** 💻
