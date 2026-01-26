# 🚀 API 服务启动指南

## ✅ 现在可以使用的状态

API 服务已成功配置并可以运行！

---

## 📌 快速启动

### 方式1：使用启动脚本（推荐）

```bash
cd backend
python run_dev_server.py
```

### 方式2：直接使用 Uvicorn

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8001
```

---

## 🌐 访问地址

启动成功后，您可以访问：

| 项目 | URL | 说明 |
|------|-----|------|
| **API 文档** | http://127.0.0.1:8001/docs | Swagger UI 交互式文档 |
| **API 文档** | http://127.0.0.1:8001/redoc | ReDoc 文档 |
| **根路径** | http://127.0.0.1:8001/ | 应用首页 |

---

## ✨ 启动成功的标志

看到这样的输出表示启动成功：

```
✓ 工作目录: C:\Users\34176\Desktop\办公助手\backend
✓ Python 路径已配置

启动命令: ...uvicorn app.main:app --reload --port 8001 --host 0.0.0.0
访问地址: http://127.0.0.1:8001
API 文档: http://127.0.0.1:8001/docs

============================================================
INFO:     Will watch for changes in these directories: [...]
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using StatReload

...

✅ 数据库表创建完成
✅ 数据库初始化完成
INFO:     Application startup complete.
```

---

## 📊 系统配置

### 数据库

- **类型**: SQLite（开发环境）
- **路径**: `./data/office_assistant.db`
- **表**:
  - `users` - 用户表
  - `meetings` - 会议表
  - `meeting_minutes` - 会议纪要表
  - `documents` - 文档表
  - `polish_tasks` - 文本润色任务表
  - `translation_tasks` - 翻译任务表
  - `ppt_projects` - PPT 项目表
  - `weekly_reports` - 周报表

### API 功能

✅ **已实现的模块**:
- 用户管理 (Users)
- 会议管理 (Meetings)
- 会议纪要处理 (Meeting Minutes)
- 文档管理 (Documents)
- 会议 API 端点 (16 个)
- NLP 服务 (7 个方法)
- 文档生成 (4 种格式)

---

## 🔧 配置修改

如果需要修改配置，编辑 `app/core/config.py`:

### 切换到 PostgreSQL（生产环境）

```python
# 在 config.py 中修改：
DB_TYPE: str = "postgresql"  # 改为 postgresql

# 配置 PostgreSQL 连接信息：
POSTGRES_USER: str = "postgres"
POSTGRES_PASSWORD: str = "your_password"
POSTGRES_HOST: str = "localhost"
POSTGRES_PORT: int = 5432
POSTGRES_DB: str = "office_assistant"
```

### 修改 API 端口

```bash
# 使用不同的端口启动
python -m uvicorn app.main:app --reload --port 8002
```

---

## 🛑 停止服务

按 **Ctrl+C** 停止服务器。

---

## 📝 环境依赖

已安装的关键依赖：
- fastapi (web 框架)
- uvicorn (ASGI 服务器)
- sqlalchemy (ORM)
- aiosqlite (SQLite 异步驱动)
- jieba (NLP 中文分词)
- reportlab (PDF 生成)
- python-docx (Word 文档生成)
- pydantic (数据验证)

---

## 🐛 故障排查

### 端口已占用

如果看到 `Address already in use` 错误，改用其他端口：

```bash
python -m uvicorn app.main:app --reload --port 8002
```

### 数据库错误

数据库文件会自动创建在 `./data/` 目录中。如果有问题，删除数据库文件重新启动：

```bash
rm -r data/  # 删除数据库
python run_dev_server.py  # 重新启动
```

### 导入错误

如果看到 `ModuleNotFoundError`，确保：
1. 当前目录是 `backend` 文件夹
2. 所有依赖已安装：`pip install -r requirements.txt`

---

## 📚 后续开发

API 现在已经准备就绪！可以：

1. **查看已有端点**: 访问 http://127.0.0.1:8001/docs
2. **运行演示代码**: `python app/services/meeting_demo.py`
3. **开发新功能**: 在 `app/api/` 中添加新的端点
4. **集成数据库**: 模型已准备好，可以开始持久化数据

---

**祝您使用愉快！** 🎉

有问题？查看 TROUBLESHOOTING.md
