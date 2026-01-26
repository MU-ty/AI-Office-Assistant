"""
周报生成API测试用例和集成指南
"""

# API 集成测试用例

## 测试工具准备

### 使用 curl (命令行)
```bash
# 创建日志
curl -X POST http://localhost:8000/api/weekly_reports/logs \
  -H "Content-Type: application/json" \
  -d '{...}'

# 查询日志
curl http://localhost:8000/api/weekly_reports/logs

# 生成周报
curl -X POST http://localhost:8000/api/weekly_reports/ \
  -H "Content-Type: application/json" \
  -d '{...}'
```

### 使用 Postman
1. 导入 API 文档
2. 自动生成集合
3. 配置环境变量
4. 运行测试脚本

### 使用 Swagger UI
访问 http://localhost:8000/api/docs，直接在网页中测试

## 完整的测试场景

### 场景 1: 单个用户周报工作流

#### 第一天: 创建日志
```bash
# POST /api/weekly_reports/logs
{
  "work_type": "编码开发",
  "task_description": "实现用户认证API端点",
  "hours_spent": 6.0
}

# 响应 (201 Created)
{
  "id": 1,
  "user_id": null,
  "work_type": "编码开发",
  "task_description": "实现用户认证API端点",
  "hours_spent": 6.0,
  "log_date": "2025-01-22T10:30:00",
  "created_at": "2025-01-22T10:30:00"
}
```

#### 第二天: 继续添加日志
```bash
# POST /api/weekly_reports/logs
{
  "work_type": "单元测试",
  "task_description": "编写认证模块的单元测试",
  "hours_spent": 3.0
}

# POST /api/weekly_reports/logs
{
  "work_type": "代码审查",
  "task_description": "审查会议模块代码",
  "hours_spent": 1.5
}
```

#### 周末: 生成周报
```bash
# POST /api/weekly_reports/
{
  "title": "2025年第4周工作总结",
  "week_start_date": "2025-01-20T00:00:00",
  "week_end_date": "2025-01-26T23:59:59"
}

# 响应 (201 Created)
{
  "id": 1,
  "user_id": null,
  "title": "2025年第4周工作总结",
  "week": "2025-W04",
  "week_start_date": "2025-01-20T00:00:00",
  "week_end_date": "2025-01-26T23:59:59",
  "summary": "本周工作总结:\n- 编码开发: 6.0小时\n- 单元测试: 3.0小时\n- 代码审查: 1.5小时",
  "content": null,
  "status": "draft",
  "total_hours": 10.5,
  "created_at": "2025-01-26T15:00:00",
  "updated_at": "2025-01-26T15:00:00"
}
```

#### 编辑周报
```bash
# PUT /api/weekly_reports/1
{
  "content": "## 本周主要成就\n1. 完成了用户认证API\n2. 编写了完整的单元测试\n3. 代码质量得到改进"
}

# 响应
{
  "id": 1,
  ...
  "content": "## 本周主要成就\n1. 完成了用户认证API\n...",
  "updated_at": "2025-01-26T16:00:00"
}
```

#### 提交审核
```bash
# POST /api/weekly_reports/1/submit

# 响应
{
  "id": 1,
  ...
  "status": "submitted"
}
```

#### 管理员审核
```bash
# POST /api/weekly_reports/1/review
{
  "status": "approved",
  "review_feedback": "很好的工作，继续保持！"
}

# 响应
{
  "id": 1,
  ...
  "status": "approved",
  "review_feedback": "很好的工作，继续保持！",
  "reviewer_id": null,
  "reviewed_at": "2025-01-27T09:00:00"
}
```

#### 导出周报
```bash
# POST /api/weekly_reports/1/export?format=markdown

# 响应
{
  "report_id": 1,
  "format": "markdown",
  "content": "# 2025年第4周工作总结\n\n**周期**: 2025-01-20 至 2025-01-26\n\n..."
}
```

### 场景 2: 列表查询和过滤

#### 获取所有日志
```bash
# GET /api/weekly_reports/logs?skip=0&limit=100

# 响应
{
  "total": 3,
  "skip": 0,
  "limit": 100,
  "items": [
    {
      "id": 3,
      "work_type": "代码审查",
      ...
    },
    {
      "id": 2,
      "work_type": "单元测试",
      ...
    },
    {
      "id": 1,
      "work_type": "编码开发",
      ...
    }
  ]
}
```

#### 日期范围查询
```bash
# GET /api/weekly_reports/logs?date_from=2025-01-20&date_to=2025-01-26

# 响应: 该日期范围内的所有日志
```

#### 获取周报列表
```bash
# GET /api/weekly_reports/?skip=0&limit=10

# 响应
{
  "total": 1,
  "skip": 0,
  "limit": 10,
  "items": [
    {
      "id": 1,
      "title": "2025年第4周工作总结",
      ...
    }
  ]
}
```

#### 按状态过滤
```bash
# 获取待审核的周报
# GET /api/weekly_reports/?status=submitted

# 获取已批准的周报
# GET /api/weekly_reports/?status=approved

# 获取草稿
# GET /api/weekly_reports/?status=draft
```

### 场景 3: 错误处理

#### 日期格式错误
```bash
# GET /api/weekly_reports/logs?date_from=2025/01/20

# 响应 (400 Bad Request)
{
  "detail": "date_from 格式错误，请使用 YYYY-MM-DD"
}
```

#### 资源不存在
```bash
# GET /api/weekly_reports/999

# 响应 (404 Not Found)
{
  "detail": "周报不存在: 999"
}
```

#### 验证失败
```bash
# POST /api/weekly_reports/logs
{
  "work_type": "",  # 空值
  "task_description": "test",
  "hours_spent": -1  # 负数
}

# 响应 (422 Unprocessable Entity)
{
  "detail": [
    {
      "loc": ["body", "work_type"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length"
    },
    {
      "loc": ["body", "hours_spent"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

#### 业务规则违反
```bash
# PUT /api/weekly_reports/1
# (当周报已提交时尝试编辑)

# 响应 (400 Bad Request)
{
  "detail": "只能编辑草稿状态的周报"
}
```

## 前端集成示例

### 使用 JavaScript/Fetch API

```javascript
// 创建日志
async function createWorkLog(logData) {
  const response = await fetch('/api/weekly_reports/logs', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(logData)
  });
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return await response.json();
}

// 使用
try {
  const log = await createWorkLog({
    work_type: '编码开发',
    task_description: '实现用户认证',
    hours_spent: 6.5
  });
  console.log('日志创建成功:', log);
} catch (error) {
  console.error('创建失败:', error);
}

// 生成周报
async function generateWeeklyReport(reportData) {
  const response = await fetch('/api/weekly_reports/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(reportData)
  });
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return await response.json();
}

// 获取周报列表
async function getWeeklyReports(status = null, skip = 0, limit = 10) {
  let url = `/api/weekly_reports/?skip=${skip}&limit=${limit}`;
  if (status) {
    url += `&status=${status}`;
  }
  
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return await response.json();
}

// 导出周报
async function exportWeeklyReport(reportId, format = 'markdown') {
  const response = await fetch(
    `/api/weekly_reports/${reportId}/export?format=${format}`,
    { method: 'POST' }
  );
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return await response.json();
}

// 提交审核
async function submitWeeklyReport(reportId) {
  const response = await fetch(
    `/api/weekly_reports/${reportId}/submit`,
    { method: 'POST' }
  );
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return await response.json();
}

// 审核周报
async function reviewWeeklyReport(reportId, status, feedback = '') {
  const response = await fetch(
    `/api/weekly_reports/${reportId}/review`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        status: status,
        review_feedback: feedback
      })
    }
  );
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return await response.json();
}
```

### 使用 Axios

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: '/api'
});

// 创建日志
async function createWorkLog(logData) {
  try {
    const response = await api.post('/weekly_reports/logs', logData);
    return response.data;
  } catch (error) {
    handleError(error);
  }
}

// 获取周报列表
async function getWeeklyReports(params = {}) {
  try {
    const response = await api.get('/weekly_reports/', { params });
    return response.data;
  } catch (error) {
    handleError(error);
  }
}

// 导出周报
async function exportWeeklyReport(reportId, format = 'markdown') {
  try {
    const response = await api.post(
      `/weekly_reports/${reportId}/export`,
      {},
      { params: { format } }
    );
    return response.data;
  } catch (error) {
    handleError(error);
  }
}

function handleError(error) {
  if (error.response) {
    // 服务器响应了错误状态
    console.error('Error:', error.response.data);
  } else if (error.request) {
    // 请求已发出但没有收到响应
    console.error('No response:', error.request);
  } else {
    // 其他错误
    console.error('Error:', error.message);
  }
}
```

### 使用 React Hook

```javascript
import { useState, useEffect } from 'react';

function useWeeklyReports() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async (status = null, skip = 0, limit = 10) => {
    setLoading(true);
    try {
      let url = `/api/weekly_reports/?skip=${skip}&limit=${limit}`;
      if (status) {
        url += `&status=${status}`;
      }
      
      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to fetch');
      
      const data = await response.json();
      setReports(data.items);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const createLog = async (logData) => {
    try {
      const response = await fetch('/api/weekly_reports/logs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(logData)
      });
      if (!response.ok) throw new Error('Failed to create log');
      return await response.json();
    } catch (err) {
      setError(err.message);
    }
  };

  return { reports, loading, error, fetchReports, createLog };
}

// 使用
function WeeklyReportPage() {
  const { reports, loading, error, fetchReports, createLog } = useWeeklyReports();

  return (
    <div>
      {loading && <p>Loading...</p>}
      {error && <p>Error: {error}</p>}
      {reports.map(report => (
        <div key={report.id}>
          <h3>{report.title}</h3>
          <p>Status: {report.status}</p>
        </div>
      ))}
    </div>
  );
}
```

## 性能考虑

### 分页最佳实践
```javascript
// 不好 - 一次加载所有数据
const all = await fetch('/api/weekly_reports/?limit=10000');

// 好 - 使用分页
const page1 = await fetch('/api/weekly_reports/?skip=0&limit=10');
const page2 = await fetch('/api/weekly_reports/?skip=10&limit=10');
```

### 缓存策略
```javascript
// 缓存周报列表
const reportCache = new Map();

async function getCachedReports(status) {
  const cacheKey = `reports_${status}`;
  
  if (reportCache.has(cacheKey)) {
    return reportCache.get(cacheKey);
  }
  
  const reports = await fetch(`/api/weekly_reports/?status=${status}`);
  const data = await reports.json();
  
  reportCache.set(cacheKey, data);
  
  // 5分钟后清除缓存
  setTimeout(() => reportCache.delete(cacheKey), 5 * 60 * 1000);
  
  return data;
}
```

## 常见集成问题

### Q: 如何处理日期选择？
A: 使用日期选择器库 (如 react-datepicker)，格式化为 ISO 8601 格式

### Q: 如何显示导出的内容？
A: 可以使用 markdown-to-html 库转换后显示，或直接在 textarea 中显示

### Q: 如何实现实时更新？
A: 使用 WebSocket 或定时轮询 API

### Q: 如何处理离线场景？
A: 使用本地缓存，连接恢复时同步

---

详见 API 文档: http://localhost:8000/api/docs
