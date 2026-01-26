"""
周报生成功能快速使用指南
"""

# 快速开始

## 环境设置

### 1. 安装依赖
```bash
cd backend
pip install -r requirements.txt
# 或使用 UV
uv sync
```

### 2. 启动后端服务
```bash
# 方式1: 使用开发脚本
python run_dev_server.py

# 方式2: 直接使用 uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 方式3: 使用 UV
uv run python -m uvicorn app.main:app --reload
```

服务启动后，可以访问:
- API 文档: http://localhost:8000/api/docs
- ReDoc 文档: http://localhost:8000/api/redoc
- OpenAPI JSON: http://localhost:8000/api/openapi.json

## 基本操作流程

### 场景1: 记录日常工作

#### 步骤 1: 创建工作日志
在一天结束时，记录今天的工作:

```bash
curl -X POST http://localhost:8000/api/weekly_reports/logs \
  -H "Content-Type: application/json" \
  -d '{
    "work_type": "编码开发",
    "task_description": "实现用户认证API和密码加密功能",
    "hours_spent": 6.0
  }'
```

响应:
```json
{
  "id": 1,
  "user_id": null,
  "work_type": "编码开发",
  "task_description": "实现用户认证API和密码加密功能",
  "hours_spent": 6.0,
  "log_date": "2025-01-26T10:30:00",
  "created_at": "2025-01-26T10:30:00"
}
```

#### 步骤 2: 继续记录其他工作
```bash
curl -X POST http://localhost:8000/api/weekly_reports/logs \
  -H "Content-Type: application/json" \
  -d '{
    "work_type": "代码审查",
    "task_description": "审查会议纪要模块的代码",
    "hours_spent": 2.0
  }'

curl -X POST http://localhost:8000/api/weekly_reports/logs \
  -H "Content-Type: application/json" \
  -d '{
    "work_type": "文档编写",
    "task_description": "更新API文档",
    "hours_spent": 1.5
  }'
```

### 场景2: 生成周报

#### 步骤 1: 生成周报
周末时生成周报，系统会自动:
- 聚合本周所有工作日志
- 计算总工时
- 生成工作摘要

```bash
curl -X POST http://localhost:8000/api/weekly_reports/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "2025年第4周工作总结",
    "week_start_date": "2025-01-20T00:00:00",
    "week_end_date": "2025-01-26T23:59:59"
  }'
```

响应:
```json
{
  "id": 1,
  "user_id": null,
  "title": "2025年第4周工作总结",
  "week": "2025-W04",
  "week_start_date": "2025-01-20T00:00:00",
  "week_end_date": "2025-01-26T23:59:59",
  "summary": "本周工作总结:\n- 编码开发: 6.0小时\n- 代码审查: 2.0小时\n- 文档编写: 1.5小时",
  "content": null,
  "status": "draft",
  "total_hours": 9.5,
  "created_at": "2025-01-26T15:00:00",
  "updated_at": "2025-01-26T15:00:00"
}
```

#### 步骤 2: 编辑周报详情
在摘要基础上添加更多内容:

```bash
curl -X PUT http://localhost:8000/api/weekly_reports/1 \
  -H "Content-Type: application/json" \
  -d '{
    "content": "## 本周主要成就\n1. 完成了用户认证模块\n2. 优化了会议纪要处理\n3. 文档更新完成\n\n## 下周计划\n1. 开始PPT生成模块\n2. 添加单元测试"
  }'
```

#### 步骤 3: 提交审核
```bash
curl -X POST http://localhost:8000/api/weekly_reports/1/submit
```

响应会显示状态已变为 "submitted"

#### 步骤 4: 审核周报
管理员审核周报:

```bash
# 批准
curl -X POST http://localhost:8000/api/weekly_reports/1/review \
  -H "Content-Type: application/json" \
  -d '{
    "status": "approved",
    "review_feedback": "很好的工作总结，继续保持"
  }'

# 或驳回
curl -X POST http://localhost:8000/api/weekly_reports/1/review \
  -H "Content-Type: application/json" \
  -d '{
    "status": "rejected",
    "review_feedback": "需要补充更多技术细节"
  }'
```

### 场景3: 查询和导出

#### 查询所有周报
```bash
curl http://localhost:8000/api/weekly_reports/?skip=0&limit=10
```

#### 按状态查询
```bash
# 查询待审核的周报
curl http://localhost:8000/api/weekly_reports/?status=submitted

# 查询已批准的周报
curl http://localhost:8000/api/weekly_reports/?status=approved
```

#### 导出为Markdown
```bash
curl http://localhost:8000/api/weekly_reports/1/export?format=markdown
```

输出:
```
# 2025年第4周工作总结

**周期**: 2025-01-20 至 2025-01-26

**总工时**: 9.5小时

**状态**: submitted

## 摘要

本周工作总结:
- 编码开发: 6.0小时
- 代码审查: 2.0小时
- 文档编写: 1.5小时

## 详细内容

## 本周主要成就
1. 完成了用户认证模块
...
```

#### 导出为HTML
```bash
curl http://localhost:8000/api/weekly_reports/1/export?format=html
```

## API参考

### 工作日志 APIs

#### 创建日志
```
POST /api/weekly_reports/logs
Content-Type: application/json

{
  "work_type": "string",              # 必需
  "task_description": "string",       # 必需
  "hours_spent": float,               # 必需 (0-24)
  "log_date": "datetime"              # 可选
}
```

#### 获取日志列表
```
GET /api/weekly_reports/logs
参数:
  date_from: 起始日期 (YYYY-MM-DD)
  date_to: 结束日期 (YYYY-MM-DD)
  skip: 分页偏移 (default: 0)
  limit: 页面大小 (default: 100, max: 1000)
```

#### 更新日志
```
PUT /api/weekly_reports/logs/{log_id}
Content-Type: application/json

{
  "work_type": "string",              # 可选
  "task_description": "string",       # 可选
  "hours_spent": float                # 可选
}
```

#### 删除日志
```
DELETE /api/weekly_reports/logs/{log_id}
```

### 周报 APIs

#### 生成周报
```
POST /api/weekly_reports/
Content-Type: application/json

{
  "title": "string",                  # 可选
  "week_start_date": "datetime",      # 必需
  "week_end_date": "datetime"         # 必需
}
```

#### 获取周报列表
```
GET /api/weekly_reports/
参数:
  status: draft/submitted/approved/rejected (可选)
  skip: 分页偏移 (default: 0)
  limit: 页面大小 (default: 10, max: 100)
```

#### 获取周报详情
```
GET /api/weekly_reports/{report_id}
```

#### 更新周报
```
PUT /api/weekly_reports/{report_id}
Content-Type: application/json

{
  "title": "string",                  # 可选
  "summary": "string",                # 可选
  "content": "string"                 # 可选
}

注: 只能编辑 draft 状态的周报
```

#### 删除周报
```
DELETE /api/weekly_reports/{report_id}

注: 只能删除 draft 状态的周报
```

#### 提交审核
```
POST /api/weekly_reports/{report_id}/submit
```

#### 审核周报
```
POST /api/weekly_reports/{report_id}/review
Content-Type: application/json

{
  "status": "approved",               # 必需: approved 或 rejected
  "review_feedback": "string"         # 可选
}
```

#### 导出周报
```
POST /api/weekly_reports/{report_id}/export
参数:
  format: markdown (default) 或 html
```

## 状态码说明

- `200 OK`: 请求成功
- `201 Created`: 资源创建成功
- `204 No Content`: 删除成功
- `400 Bad Request`: 请求格式或业务规则错误
- `404 Not Found`: 资源不存在
- `500 Internal Server Error`: 服务器错误

## 常见问题

### Q: 如何修改已提交的周报？
A: 已提交的周报不能直接修改。需要管理员驳回后重新编辑。

### Q: 周报摘要如何生成？
A: 系统自动从该周的工作日志按工作类型统计生成。

### Q: 可以跨周期生成周报吗？
A: 可以。指定任意的周期日期即可生成周报。

### Q: 如何批量导出周报？
A: 可以通过获取周报列表，然后逐个导出。未来可考虑添加批量导出功能。

### Q: 删除日志会影响已生成的周报吗？
A: 不会。周报在生成时已经记录了数据快照。

## 故障排除

### 数据库连接失败
- 检查 `.env` 配置文件
- 确保数据库服务正在运行
- 对于 SQLite，检查目录权限

### 周报生成失败
- 确保日期格式正确 (ISO 8601)
- 检查该周期的周报是否已存在
- 查看服务器日志获取错误详情

### API 返回 422 错误
- 检查请求体的 JSON 格式
- 确保所有必需字段都已提供
- 验证数据类型是否正确

## 最佳实践

1. **每日记录**: 在工作结束时及时记录日志，不要堆积到周末
2. **准确工时**: 记录实际花费的时间，便于工作量评估
3. **清晰描述**: 使用清晰的任务描述，便于周报总结和审核
4. **及时提交**: 完成周报后及时提交审核
5. **反馈回复**: 如果周报被驳回，及时修改并重新提交

## 技术支持

如有问题或建议，请联系技术团队或提交Issue。
