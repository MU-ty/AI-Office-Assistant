# 学术润色模块 - API 集成指南

## 快速开始

### 1. 启动后端服务

```bash
cd backend
python run_dev_server.py
```

服务将在 `http://localhost:8000` 启动

### 2. 访问API文档

打开浏览器访问：
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI 规范**: http://localhost:8000/api/openapi.json

## API 基本信息

- **基础URL**: `http://localhost:8000/api/v1/polish`
- **认证**: 目前无需认证（可根据需要添加）
- **响应格式**: JSON

## 完整 API 端点列表

### 1. 创建润色任务

**端点**: `POST /api/v1/polish`

**请求示例**:
```bash
curl -X POST http://localhost:8000/api/v1/polish \
  -H "Content-Type: application/json" \
  -d '{
    "original_text": "我们的研究进行了详细分析。这样做很好。",
    "polish_level": "academic",
    "auto_fix_enabled": false
  }'
```

**请求参数**:

| 字段 | 类型 | 必需 | 说明 | 示例 |
|------|------|------|------|------|
| original_text | string | ✓ | 需要润色的文本 | "文本内容..." |
| polish_level | string | | 润色级别 | "standard"/"academic"/"formal" |
| auto_fix_enabled | boolean | | 是否自动修复 | false |
| document_id | integer | | 关联的文档ID | 123 |

**响应示例**:
```json
{
  "code": 200,
  "message": "任务创建成功",
  "data": {
    "id": 1,
    "status": "completed",
    "polish_level": "academic",
    "total_issues": 5,
    "fixed_issues": 0,
    "accuracy": 0.0,
    "terminology_issues": [
      {
        "id": 1,
        "original_content": "我们的研究",
        "suggested_content": "本研究",
        "reason": "将非正式术语替换为学术术语",
        "severity": "minor",
        "confidence": 0.95
      }
    ],
    "tense_issues": [],
    "style_issues": [],
    "thesis_issues": [
      {
        "id": 2,
        "original_content": "这样做很好",
        "suggested_content": "结果良好",
        "reason": "学位论文规范检查：表述方式调整",
        "severity": "medium",
        "confidence": 0.85
      }
    ],
    "created_at": "2026-01-26T10:00:00",
    "completed_at": "2026-01-26T10:00:05"
  }
}
```

### 2. 获取任务列表

**端点**: `GET /api/v1/polish`

**请求示例**:
```bash
curl "http://localhost:8000/api/v1/polish?skip=0&limit=10&status=completed"
```

**查询参数**:

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| skip | integer | 0 | 跳过数量 |
| limit | integer | 10 | 返回数量(最大100) |
| status | string | - | 状态筛选 |

**响应示例**:
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "total": 50,
    "skip": 0,
    "limit": 10,
    "items": [
      {
        "id": 1,
        "status": "completed",
        "polish_level": "academic",
        "total_issues": 5,
        "fixed_issues": 2,
        "accuracy": 0.4,
        "created_at": "2026-01-26T10:00:00",
        "updated_at": "2026-01-26T10:00:05"
      }
    ]
  }
}
```

### 3. 获取任务详情

**端点**: `GET /api/v1/polish/{task_id}`

**请求示例**:
```bash
curl http://localhost:8000/api/v1/polish/1
```

**响应示例**:
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": 1,
    "status": "completed",
    "original_text": "我们的研究进行了详细分析...",
    "polished_text": "本研究完成了详细分析...",
    "total_issues": 5,
    "fixed_issues": 2,
    "accuracy": 0.4,
    "issues": [...]
  }
}
```

### 4. 更新任务

**端点**: `PUT /api/v1/polish/{task_id}`

**请求示例**:
```bash
curl -X PUT http://localhost:8000/api/v1/polish/1 \
  -H "Content-Type: application/json" \
  -d '{
    "original_text": "新的文本内容...",
    "polish_level": "formal"
  }'
```

### 5. 删除任务

**端点**: `DELETE /api/v1/polish/{task_id}`

**请求示例**:
```bash
curl -X DELETE http://localhost:8000/api/v1/polish/1
```

**响应**: 204 No Content

### 6. 获取任务问题列表

**端点**: `GET /api/v1/polish/{task_id}/issues`

**请求示例**:
```bash
curl "http://localhost:8000/api/v1/polish/1/issues?filter_type=terminology"
```

**查询参数**:

| 参数 | 说明 |
|------|------|
| filter_type | terminology/tense/style/thesis |

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "task_id": 1,
    "total": 3,
    "issues": [
      {
        "id": 1,
        "issue_type": "terminology",
        "severity": "minor",
        "original_content": "我们的研究",
        "suggested_content": "本研究",
        "reason": "将非正式术语替换为学术术语",
        "status": "pending",
        "confidence": 0.95,
        "rule_id": "TERM_001"
      }
    ]
  }
}
```

### 7. 接受建议

**端点**: `POST /api/v1/polish/{task_id}/issues/{issue_id}/accept`

**请求示例**:
```bash
curl -X POST http://localhost:8000/api/v1/polish/1/issues/5/accept \
  -H "Content-Type: application/json" \
  -d '{
    "feedback": "同意这个建议"
  }'
```

**响应示例**:
```json
{
  "code": 200,
  "message": "建议已接受",
  "data": {
    "id": 5,
    "status": "accepted",
    "accepted_at": "2026-01-26T10:05:00"
  }
}
```

### 8. 拒绝建议

**端点**: `POST /api/v1/polish/{task_id}/issues/{issue_id}/reject`

**请求示例**:
```bash
curl -X POST http://localhost:8000/api/v1/polish/1/issues/5/reject \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "这个建议不适合"
  }'
```

### 9. 导出结果

**端点**: `POST /api/v1/polish/{task_id}/export`

**请求示例**:
```bash
curl -X POST http://localhost:8000/api/v1/polish/1/export \
  -H "Content-Type: application/json" \
  -d '{
    "format": "json",
    "include_comments": true
  }'
```

**支持的格式**:
- `json`: 结构化JSON数据
- `txt`: 人类可读的纯文本报告

### 10. 获取统计信息

**端点**: `GET /api/v1/polish/statistics`

**请求示例**:
```bash
curl http://localhost:8000/api/v1/polish/statistics
```

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "total_tasks": 100,
    "completed_tasks": 85,
    "pending_tasks": 15,
    "average_accuracy": 0.92,
    "total_issues_found": 500,
    "total_issues_fixed": 460
  }
}
```

## Python SDK 示例

```python
import httpx
import json

class PolishClient:
    def __init__(self, base_url="http://localhost:8000/api/v1/polish"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def create_task(self, text, level="standard"):
        """创建润色任务"""
        response = await self.client.post(
            self.base_url,
            json={
                "original_text": text,
                "polish_level": level
            }
        )
        return response.json()["data"]
    
    async def get_task(self, task_id):
        """获取任务详情"""
        response = await self.client.get(f"{self.base_url}/{task_id}")
        return response.json()["data"]
    
    async def get_issues(self, task_id, filter_type=None):
        """获取问题列表"""
        params = {}
        if filter_type:
            params["filter_type"] = filter_type
        response = await self.client.get(
            f"{self.base_url}/{task_id}/issues",
            params=params
        )
        return response.json()["data"]["issues"]
    
    async def accept_suggestion(self, task_id, issue_id):
        """接受建议"""
        response = await self.client.post(
            f"{self.base_url}/{task_id}/issues/{issue_id}/accept"
        )
        return response.json()["data"]

# 使用示例
async def main():
    client = PolishClient()
    
    # 创建任务
    task = await client.create_task(
        "我们的研究进行了详细分析。这样做很好。",
        level="academic"
    )
    print(f"任务ID: {task['id']}")
    print(f"发现问题: {task['total_issues']}")
    
    # 获取问题
    issues = await client.get_issues(task['id'])
    for issue in issues:
        print(f"问题: {issue['original_content']} -> {issue['suggested_content']}")
        
        # 接受建议
        await client.accept_suggestion(task['id'], issue['id'])
```

## JavaScript 示例

```javascript
class PolishClient {
  constructor(baseUrl = "http://localhost:8000/api/v1/polish") {
    this.baseUrl = baseUrl;
  }
  
  async createTask(text, level = "standard") {
    const response = await fetch(this.baseUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        original_text: text,
        polish_level: level
      })
    });
    return response.json();
  }
  
  async getTask(taskId) {
    const response = await fetch(`${this.baseUrl}/${taskId}`);
    return response.json();
  }
  
  async getIssues(taskId, filterType = null) {
    let url = `${this.baseUrl}/${taskId}/issues`;
    if (filterType) {
      url += `?filter_type=${filterType}`;
    }
    const response = await fetch(url);
    return response.json();
  }
  
  async acceptSuggestion(taskId, issueId) {
    const response = await fetch(
      `${this.baseUrl}/${taskId}/issues/${issueId}/accept`,
      { method: "POST" }
    );
    return response.json();
  }
}

// 使用示例
const client = new PolishClient();

async function main() {
  // 创建任务
  const result = await client.createTask(
    "我们的研究进行了详细分析。"
  );
  const taskId = result.data.id;
  console.log(`任务ID: ${taskId}`);
  
  // 获取问题
  const issuesResult = await client.getIssues(taskId);
  for (const issue of issuesResult.data.issues) {
    console.log(`问题: ${issue.original_content} -> ${issue.suggested_content}`);
    
    // 接受建议
    await client.acceptSuggestion(taskId, issue.id);
  }
}

main();
```

## 错误处理

### 常见错误响应

**400 Bad Request**:
```json
{
  "code": 400,
  "message": "请求参数错误",
  "detail": "文本不能为空"
}
```

**404 Not Found**:
```json
{
  "code": 404,
  "message": "任务 123 不存在"
}
```

**500 Internal Server Error**:
```json
{
  "code": 500,
  "message": "服务器内部错误"
}
```

## 集成建议

1. **前端集成**:
   - 使用提供的JavaScript SDK或直接调用API
   - 实现进度反馈UI
   - 支持批量处理

2. **后端集成**:
   - 使用异步任务队列处理长文本
   - 实现结果缓存
   - 添加请求限流

3. **性能优化**:
   - 对大文本进行分段处理
   - 实现客户端侧的结果缓存
   - 使用WebSocket进行实时更新

## 监控和日志

所有API请求都会被记录，可以通过以下方式查看：

```bash
# 查看服务日志
tail -f backend/logs/app.log

# 查看特定任务的日志
grep "task_id=1" backend/logs/app.log
```

## 支持和反馈

如有任何问题或建议，请联系：
- 📧 Email: support@example.com
- 🐛 Issues: https://github.com/example/issues
- 📖 文档: [POLISH_MODULE_GUIDE.md](./POLISH_MODULE_GUIDE.md)
