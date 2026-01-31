# 办公助手Agent - Docker 一键启动指南

本项目已完成完整的容器化配置，您可以使用 Docker Compose 一键启动所有服务（包括前后端、数据库、中间件及监控系统）。

## 🚀 快速启动

1. **环境准备**
   - 确保您的系统中已安装 [Docker](https://docs.docker.com/get-docker/) 和 [Docker Compose](https://docs.docker.com/compose/install/)。
   - 确保 80, 5432, 6379, 9000, 3001 等端口未被占用。

2. **配置环境变量**
   - 项目根目录下已生成 `.env` 文件。
   - 请在 `.env` 中填入您的 `QWEN_API_KEY`（阿里云 DashScope）或其他必要的 AI 模型 API Key。

3. **一键启动**
   ```bash
   # 在项目根目录下执行
   docker-compose up -d --build
   ```

## 🌐 访问地址

启动成功后，您可以通过以下地址访问各项服务：

- **前端应用**: [http://localhost](http://localhost) (由 Nginx 转发)
- **后端接口文档**: [http://localhost/api/docs](http://localhost/api/docs)
- **MinIO 管理后台**: [http://localhost:9001](http://localhost:9001) (用户名: `minio_user`, 密码: `minio_password`)
- **Grafana 监控面板**: [http://localhost:3001](http://localhost:3001) (用户名: `admin`, 密码: `admin_password`)
- **RabbitMQ 管理后台**: [http://localhost:15672](http://localhost:15672) (用户名: `rabbitmq_user`, 密码: `rabbitmq_password`)

## 🛠️ 常用维护命令

- **查看日志**:
  ```bash
  docker-compose logs -f
  ```
- **停止并移除容器**:
  ```bash
  docker-compose down
  ```
- **重启特定服务** (例如后端):
  ```bash
  docker-compose restart backend
  ```
- **更新代码后重新构建**:
  ```bash
  docker-compose up -d --build
  ```

## 💾 数据持久化与迁移

### 1. 用户数据 (Database)
- **新用户**: 默认使用 PostgreSQL 容器，数据保存在 Docker 卷 `postgres_data` 中。
- **老用户 (已有 SQLite 数据)**:
    - **方案 A (继续使用 SQLite)**: 
      1. 修改 `.env` 文件：`DB_TYPE="sqlite"` 和 `SQLITE_DB_PATH="/app/data/office_assistant.db"`。
      2. 启动后，系统将自动读取宿主机 `./backend/data/office_assistant.db` 中的数据。
    - **方案 B (迁移到 PostgreSQL - 推荐)**:
      1. 启动 Docker 容器：`docker-compose up -d`。
      2. 运行迁移脚本：`python backend/migrate_data.py`。
      3. 迁移完成后，修改 `.env` 中的 `DB_TYPE="postgresql"` 并重启后端容器。

### 2. 知识库 (Knowledge Base / RAG)
- **数据存储**: Weaviate 的向量数据持久化在宿主机的 `./backend/data/weaviate` 目录下。
- **自动初始化**: 后端服务启动时会自动运行 `initialize_weknora()`，在 Weaviate 中创建必要的 Embedding 和 QA 模型配置。
- **现有文档**: 如果您之前在本地运行过 Weaviate，可以将数据目录拷贝至 `./backend/data/weaviate`。如果是新启动，上传的文档将自动索引并存储在该目录中。

### 3. 文件存储 (MinIO)
- 所有上传的原始文件（PDF、音频等）都保存在 Docker 卷 `minio_data` 中。
- 宿主机 `./backend/data/uploads` 目录也通过卷挂载到了容器内部，确保文件访问的一致性。

## ⚠️ 注意事项

- **首次构建**: 由于后端包含大型 AI 依赖库（如 torch, transformers），首次构建镜像可能需要较长时间（视网速而定，建议使用镜像加速）。
- **数据持久化**: 数据库和存储数据保存在 Docker 命名卷中，即使容器被删除，数据依然存在。
- **内存建议**: 建议运行环境至少具备 4GB 以上空闲内存。
