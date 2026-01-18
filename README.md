# 主项目README

# 🎓 办公助手Agent - 学术与职场场景智能支持系统

> 一个全能型的"数字研友"和"职场预演伙伴"

## 📋 项目概述

办公助手Agent是一个智能办公助手系统，专为学生和职场人士设计，包含6个核心功能模块：

- 🎤 **会议纪要处理** - 自动处理会议音频/文字，生成结构化纪要
- 📚 **文献摘要提取** - 快速提取学术论文的核心要点
- ✍️ **学术文献润色** - 提升学术写作的规范性和表达质量
- 🌐 **多语言处理** - 支持跨语言的翻译和润色服务
- 🎨 **PPT智能生成** - 从内容自动生成专业演示文稿
- 📋 **实习周报生成** - 智能化生成周报，记录实习进度

## 🚀 快速开始

### 前置要求

- Python 3.10+
- Node.js 16+
- Docker & Docker Compose
- PostgreSQL 15
- Redis 7

### 项目结构

```
办公助手/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── core/              # 核心配置
│   │   ├── api/               # API路由
│   │   ├── models/            # 数据模型
│   │   ├── services/          # 业务逻辑
│   │   ├── db/                # 数据库
│   │   └── utils/             # 工具函数
│   ├── tests/                 # 测试
│   ├── main.py                # 应用入口
│   └── pyproject.toml         # 项目配置
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── components/        # React组件
│   │   ├── pages/             # 页面
│   │   ├── services/          # 服务层
│   │   ├── store/             # 状态管理
│   │   ├── types/             # 类型定义
│   │   ├── utils/             # 工具函数
│   │   └── hooks/             # 自定义Hooks
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml         # Docker服务编排
├── docs/                      # 文档
└── config/                    # 配置文件
```

### 安装和运行

#### 1. 启动后端依赖服务

```bash
# 启动PostgreSQL、Redis、Weaviate
docker-compose up -d

# 等待服务启动完成
docker-compose logs -f
```

#### 2. 启动后端服务

```bash
cd backend

# 创建虚拟环境（可选）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -e ".[dev]"

# 复制环境配置文件
cp .env.example .env

# 初始化数据库
python scripts/init_db.py

# 启动开发服务
python main.py
# 或
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

服务将在 http://localhost:8000 启动，可访问 http://localhost:8000/docs 查看API文档

#### 3. 启动前端应用

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务
npm run dev
```

前端将在 http://localhost:3000 启动

### 环境变量配置

在 `backend/.env` 中配置：

```
DATABASE_URL=postgresql://office_user:office_password@localhost:5432/office_assistant
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
QWEN_API_KEY=your-qwen-api-key
```

## 📖 API文档

启动后端后，访问 http://localhost:8000/docs 获取完整的Swagger API文档

### 主要端点

- `GET /` - 根路由
- `GET /api/v1/health` - 健康检查
- `GET /api/v1/users` - 用户列表
- `GET /api/v1/users/{user_id}` - 用户详情

## 🛠️ 开发指南

### 后端开发

添加新API端点：

```python
# backend/app/api/features.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/features", tags=["features"])

@router.get("")
async def list_features():
    return {"features": []}
```

然后在 `app/main.py` 中注册：

```python
from app.api.features import router as features_router
app.include_router(features_router)
```

### 前端开发

添加新页面：

```typescript
// src/pages/NewFeature.tsx
export default function NewFeaturePage() {
  return <div>New Feature</div>
}
```

在 `src/App.tsx` 中添加路由：

```typescript
<Route path="/new-feature" element={<NewFeaturePage />} />
```

## 🧪 测试

### 后端测试

```bash
cd backend
pytest tests/ -v
```

### 前端测试

```bash
cd frontend
npm test
```

## 📦 构建和部署

### 构建前端

```bash
cd frontend
npm run build
# 输出在 dist/ 目录
```

### 构建Docker镜像

```bash
# 后端
docker build -f backend/Dockerfile -t office-assistant-backend .

# 前端
docker build -f frontend/Dockerfile -t office-assistant-frontend .
```

## 📊 项目进度

- ✅ 第一阶段：基础架构搭建
- ⏳ 第二阶段：核心模块开发
- ⏳ 第三阶段：扩展功能开发
- ⏳ 第四阶段：集成与测试
- ⏳ 第五阶段：部署与上线

## 📝 技术栈

### 后端
- FastAPI
- SQLAlchemy
- PostgreSQL
- Redis
- LangChain
- Dashscope

### 前端
- React 18
- TypeScript
- Material-UI
- Zustand
- Axios

### 基础设施
- Docker & Docker Compose
- Nginx

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

MIT License

## 📞 联系方式

- 项目主页: [项目地址]
- 问题反馈: [Issue Tracker]
- 邮箱: team@officeassistant.com

---

**最后更新**: 2026年1月18日
