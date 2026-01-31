# 流式处理服务 - 依赖项和环境配置

## Python依赖项

流式处理服务需要以下Python包：

### 必需依赖

```toml
# 在 pyproject.toml 中添加

[project]
dependencies = [
    # 核心Web框架
    "fastapi>=0.100.0",
    "uvicorn[standard]>=0.23.0",
    
    # 异步HTTP客户端 (用于调用远程API)
    "aiohttp>=3.8.0",
    
    # 数据验证
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    
    # 数据库 (可选，如果使用数据存储)
    "sqlalchemy>=2.0.0",
    "asyncpg>=0.27.0",  # PostgreSQL驱动
    
    # 日志和监控
    "python-json-logger>=2.0.0",
    
    # 工具库
    "python-dotenv>=1.0.0",
]
```

### 开发依赖

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "ruff>=0.0.200",
    "mypy>=1.0.0",
]
```

## 快速安装

### 使用UV (推荐)

```bash
# 进入项目目录
cd backend

# 创建虚拟环境
uv venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 安装依赖
uv pip install fastapi uvicorn aiohttp pydantic

# 或安装完整的项目依赖
uv sync
```

### 使用pip

```bash
pip install fastapi uvicorn aiohttp pydantic pydantic-settings
```

### 使用Poetry

```bash
poetry add fastapi uvicorn aiohttp pydantic
```

## 环境变量配置

创建 `backend/.env` 文件：

```env
# FastAPI配置
FASTAPI_ENV=development
API_HOST=0.0.0.0
API_PORT=8000

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# 数据库配置
DATABASE_URL=sqlite:///./data/app.db
# 或PostgreSQL:
# DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname

# 模型配置
DEFAULT_MODEL=Qwen3-8B
DEFAULT_TEMPERATURE=0.1
DEFAULT_MAX_TOKENS=1024

# API地址配置
QWEN_API_URL=http://localhost:8000/v1/chat/completions
DEEPSEEK_API_URL=http://localhost:8000/v1/chat/completions
OPENAI_API_KEY=sk-xxxxx  # 如果使用OpenAI
OPENAI_API_URL=https://api.openai.com/v1/chat/completions

# CORS配置
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
```

## Docker支持

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY pyproject.toml uv.lock ./

# 安装Python依赖
RUN pip install --no-cache-dir uv && \
    uv pip install --system -r requirements.txt

# 复制应用代码
COPY ./app ./app
COPY .env .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  # FastAPI应用
  api:
    build: ./backend
    container_name: ai-office-assistant
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/ai_office
      - LOG_LEVEL=INFO
    depends_on:
      - db
    volumes:
      - ./backend/logs:/app/logs
      - ./backend/uploads:/app/uploads
    networks:
      - app-network

  # PostgreSQL数据库
  db:
    image: postgres:15-alpine
    container_name: ai-office-db
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=ai_office
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docs/init_schema.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - app-network

  # Redis缓存 (可选)
  redis:
    image: redis:7-alpine
    container_name: ai-office-redis
    ports:
      - "6379:6379"
    networks:
      - app-network

  # Nginx反向代理 (可选)
  nginx:
    image: nginx:alpine
    container_name: ai-office-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - api
    networks:
      - app-network

volumes:
  postgres_data:

networks:
  app-network:
    driver: bridge
```

## 运行服务

### 开发模式

```bash
# 进入后端目录
cd backend

# 方式1: 直接运行
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 方式2: 使用启动脚本
python run_dev_server.py

# 方式3: 使用专业工具
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### 生产模式

```bash
# 使用Gunicorn + Uvicorn
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile - \
  --log-level info

# 或使用Docker
docker run -p 8000:8000 ai-office-assistant:latest
```

### Docker Compose运行

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f api

# 停止服务
docker-compose down
```

## 验证安装

```bash
# 检查Python版本
python --version  # 应该是3.9+

# 检查已安装的包
pip list | grep -E "fastapi|uvicorn|aiohttp"

# 测试导入
python -c "
from fastapi import FastAPI
from app.services.stream_service import StreamService, StreamProvider
print('✅ 所有依赖正确安装')
"

# 启动服务并测试
python -m uvicorn app.main:app --reload

# 在另一个终端测试API
curl http://localhost:8000/health
```

## 故障排除

### 问题: ModuleNotFoundError: No module named 'aiohttp'

**解决方案:**
```bash
pip install aiohttp
# 或
uv pip install aiohttp
```

### 问题: 端口8000已被占用

**解决方案:**
```bash
# 更改端口
python -m uvicorn app.main:app --port 8001

# 或杀死占用进程 (Linux/Mac)
lsof -i :8000
kill -9 <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### 问题: 数据库连接失败

**解决方案:**
```bash
# 检查.env文件中的DATABASE_URL
# 确保数据库服务已启动

# PostgreSQL启动示例
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:15

# 或使用Docker Compose
docker-compose up -d db
```

### 问题: 导入错误或循环依赖

**解决方案:**
```bash
# 清除缓存
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# 重新安装依赖
pip install --force-reinstall -r requirements.txt
```

## 性能优化

### 依赖版本优化

```toml
# 最新稳定版本
fastapi = "^0.104.0"
uvicorn = "^0.24.0"
aiohttp = "^3.9.0"
pydantic = "^2.5.0"
```

### 生产环境推荐配置

```bash
# 使用uvloop提高性能
pip install uvloop

# 配置ASGI服务器
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --worker-connections 1000 \
  --keepalive 65 \
  --timeout 120 \
  --access-logfile /var/log/gunicorn-access.log \
  --error-logfile /var/log/gunicorn-error.log
```

### 数据库优化

```python
# 使用连接池
from sqlalchemy.pool import NullPool, QueuePool

engine = create_async_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=0,
    echo=False
)
```

## 监控和日志

### 日志配置示例

```python
import logging
from logging.handlers import RotatingFileHandler

# 创建日志目录
import os
os.makedirs("logs", exist_ok=True)

# 配置日志
logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

# 文件日志处理器
fh = RotatingFileHandler(
    "logs/app.log",
    maxBytes=10485760,  # 10MB
    backupCount=10
)
fh.setLevel(logging.INFO)

# 格式化
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
fh.setFormatter(formatter)

logger.addHandler(fh)
```

### Prometheus监控

```bash
pip install prometheus-client
```

```python
from prometheus_client import Counter, Histogram
from fastapi import FastAPI
from prometheus_client import make_asgi_app

# 创建指标
request_count = Counter(
    'stream_requests_total',
    'Total stream requests',
    ['provider']
)

request_duration = Histogram(
    'stream_request_duration_seconds',
    'Stream request duration'
)

# 添加Prometheus端点
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

## 总结

- ✅ Python 3.9+ 环境
- ✅ 核心依赖: FastAPI, Uvicorn, Aiohttp
- ✅ 可选: PostgreSQL, Redis, Nginx
- ✅ 推荐: Docker + Docker Compose
- ✅ 监控: Prometheus + Grafana
- ✅ 日志: ELK Stack (可选)

详细信息参考项目文档。
