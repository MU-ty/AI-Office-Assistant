# 学术润色模块 - 使用指南

## 概述

学术润色模块是基于流程图中的**2.3.3学术规范化子模块**实现的完整后端系统。该模块包含四个核心功能：

1. **2.3.3.1 学术术语替换** - 检查和替换非正式术语
2. **2.3.3.2 时态调整** - 检查和调整不规范的时态表达
3. **2.3.3.3 风格一致性检查** - 检查文本格式、缩写、数字表示的一致性
4. **2.3.3.4 学位论文规定检查** - 检查论文规范（称谓、表述、逻辑词、引用等）

## 系统架构

```
后端结构：
├── models/polish.py                      # 数据模型
│   ├── PolishTask                        # 润色任务模型
│   └── PolishIssue                       # 问题记录模型
├── schemas/polish.py                     # 数据验证模型
├── services/
│   ├── polish_normalization_service.py   # 核心规范化处理逻辑
│   └── base_services.py (PolishService)  # 数据库操作服务
└── api/polish_tasks.py                   # API端点
```

## 核心功能详解

### 1. 数据模型 (models/polish.py)

#### PolishTask（润色任务）
```python
- id: 任务ID
- document_id: 关联的文档ID
- original_text: 原始文本
- polished_text: 润色后的文本
- status: 任务状态 (pending/processing/completed/failed)
- polish_level: 润色级别 (standard/academic/formal)
- total_issues: 检测到的总问题数
- fixed_issues: 已修复的问题数
- accuracy: 修复准确率
- terminology_issues: 术语问题列表（JSON存储）
- tense_issues: 时态问题列表（JSON存储）
- style_issues: 风格问题列表（JSON存储）
- thesis_issues: 论文规范问题列表（JSON存储）
```

#### PolishIssue（问题记录）
```python
- id: 问题ID
- task_id: 关联的任务ID
- issue_type: 问题类型 (terminology/tense/style/thesis)
- severity: 严重程度 (minor/medium/major)
- original_content: 原始内容
- suggested_content: 建议修改内容
- reason: 修改原因
- status: 问题状态 (pending/accepted/rejected/ignored)
- confidence: 建议的置信度 (0-1)
- rule_id: 应用的规范规则ID
```

### 2. 核心服务 (polish_normalization_service.py)

#### 术语替换检查 (check_terminology)
- 检测非正式术语并提出替换建议
- 识别常见错误表述
- 返回置信度和规则ID

**示例：**
```
输入: "我们的研究进行了分析"
问题: 
  - "我们的" -> "本" (confidence: 0.95)
  - "进行了分析" -> "分析" (confidence: 0.90)
```

#### 时态调整检查 (check_tense)
- 检测进行时表达
- 识别非正式时态标记
- 建议改用完成时或一般过去时

**示例：**
```
输入: "在进行着实验"
问题: "在进行着" 应改为 "已进行" (confidence: 0.85)
```

#### 风格一致性检查 (check_style_consistency)
- 检查数字表示方式的一致性
- 检查缩写形式的一致性
- 检查单位表示的一致性

**示例：**
```
输入: "第1个数据...第二个数据"
问题: 数字表示格式不一致 (confidence: 0.75)
```

#### 论文规范检查 (check_thesis_requirements)
- **称谓规范**: 改"我们的"为"本"
- **表述规范**: 改"可以看出"为"研究表明"
- **逻辑词规范**: 改"所以"为"因此"
- **引用规范**: 要求正式引用格式

### 3. 数据库操作服务 (PolishService in base_services.py)

主要方法：

#### create_task(task_data)
```python
# 创建新的润色任务
# 1. 保存原始文本
# 2. 执行规范化分析
# 3. 保存问题到数据库
# 4. 返回任务ID和问题列表

response = await service.create_task({
    "original_text": "文本内容",
    "polish_level": "academic",
    "auto_fix_enabled": True
})
```

#### list_tasks(skip, limit, status)
```python
# 获取任务列表
response = await service.list_tasks(skip=0, limit=10, status="completed")
# 返回: {total, items: [task1, task2, ...]}
```

#### get_task(task_id)
```python
# 获取单个任务详情
task = await service.get_task(1)
```

#### get_issues(task_id, filter_type)
```python
# 获取任务的所有问题
# filter_type: "terminology" | "tense" | "style" | "thesis"
issues = await service.get_issues(1, filter_type="terminology")
```

#### accept_suggestion(task_id, issue_id)
```python
# 接受某个建议，更新问题状态为accepted
# 自动更新任务的fixed_issues计数和accuracy
result = await service.accept_suggestion(1, 5)
```

#### reject_suggestion(task_id, issue_id)
```python
# 拒绝某个建议，问题状态变为rejected
result = await service.reject_suggestion(1, 5)
```

#### export_result(task_id, format_type)
```python
# 导出结果
# format_type: "json" | "txt"
result = await service.export_result(1, format_type="json")
```

## API 端点

所有API端点基础路径: `/api/v1/polish`

### 创建润色任务
```
POST /api/v1/polish

请求体：
{
    "original_text": "需要润色的文本内容...",
    "polish_level": "standard|academic|formal",  // 默认: standard
    "auto_fix_enabled": false,                    // 默认: false
    "document_id": null                           // 可选
}

响应：
{
    "code": 200,
    "message": "任务创建成功",
    "data": {
        "id": 1,
        "status": "completed",
        "total_issues": 5,
        "fixed_issues": 0,
        "accuracy": 0.0,
        "terminology_issues": [...],
        "tense_issues": [...],
        "style_issues": [...],
        "thesis_issues": [...]
    }
}
```

### 获取任务列表
```
GET /api/v1/polish?skip=0&limit=10&status=completed

参数：
- skip: 跳过数量 (默认: 0)
- limit: 返回数量 (默认: 10, 最大: 100)
- status: 筛选状态 (pending/processing/completed/failed)

响应：
{
    "code": 200,
    "data": {
        "total": 50,
        "skip": 0,
        "limit": 10,
        "items": [...]
    }
}
```

### 获取任务详情
```
GET /api/v1/polish/{task_id}

响应：
{
    "code": 200,
    "data": {
        "id": 1,
        "status": "completed",
        "original_text": "...",
        "polished_text": "...",
        "total_issues": 5,
        "issues": [...]  // 包含所有问题详情
    }
}
```

### 更新任务
```
PUT /api/v1/polish/{task_id}

请求体：
{
    "original_text": "新的文本内容",  // 可选
    "polish_level": "academic",      // 可选
    "auto_fix_enabled": true         // 可选
}
```

### 删除任务
```
DELETE /api/v1/polish/{task_id}

返回: 204 No Content
```

### 获取任务问题列表
```
GET /api/v1/polish/{task_id}/issues?filter_type=terminology

参数：
- filter_type: terminology|tense|style|thesis (可选)

响应：
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
                "reason": "将非正式术语'我们的'替换为学术术语'本'",
                "status": "pending",
                "confidence": 0.95
            },
            ...
        ]
    }
}
```

### 接受建议
```
POST /api/v1/polish/{task_id}/issues/{issue_id}/accept

请求体：
{
    "feedback": "反馈意见（可选）"
}

响应：
{
    "code": 200,
    "data": {
        "id": 1,
        "status": "accepted",
        "accepted_at": "2024-01-26T10:00:00"
    }
}
```

### 拒绝建议
```
POST /api/v1/polish/{task_id}/issues/{issue_id}/reject

请求体：
{
    "reason": "拒绝原因（可选）"
}
```

### 导出结果
```
POST /api/v1/polish/{task_id}/export

请求体：
{
    "format": "json|txt",             // 导出格式
    "include_comments": true          // 是否包含注释
}
```

### 获取统计信息
```
GET /api/v1/polish/statistics

响应：
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

## 使用示例

### Python 示例
```python
import httpx
import asyncio

async def example():
    client = httpx.AsyncClient()
    
    # 1. 创建润色任务
    response = await client.post(
        "http://localhost:8000/api/v1/polish",
        json={
            "original_text": "我们的研究进行了详细分析。这样做很好。",
            "polish_level": "academic"
        }
    )
    task = response.json()["data"]
    task_id = task["id"]
    
    # 2. 获取问题列表
    response = await client.get(f"http://localhost:8000/api/v1/polish/{task_id}/issues")
    issues = response.json()["data"]["issues"]
    
    for issue in issues:
        print(f"问题: {issue['original_content']} -> {issue['suggested_content']}")
        
        # 3. 接受建议
        await client.post(
            f"http://localhost:8000/api/v1/polish/{task_id}/issues/{issue['id']}/accept"
        )
    
    # 4. 导出结果
    response = await client.post(
        f"http://localhost:8000/api/v1/polish/{task_id}/export",
        json={"format": "json"}
    )
    result = response.json()["data"]
    print(f"最终准确率: {result['task']['accuracy']}")

asyncio.run(example())
```

### cURL 示例
```bash
# 创建任务
curl -X POST http://localhost:8000/api/v1/polish \
  -H "Content-Type: application/json" \
  -d '{
    "original_text": "我们的研究表明这样做很好。",
    "polish_level": "academic"
  }'

# 获取问题列表
curl http://localhost:8000/api/v1/polish/1/issues?filter_type=terminology

# 接受建议
curl -X POST http://localhost:8000/api/v1/polish/1/issues/5/accept

# 导出结果
curl -X POST http://localhost:8000/api/v1/polish/1/export \
  -H "Content-Type: application/json" \
  -d '{"format": "json"}'
```

## 检查规则详解

### 术语替换规则 (Rule ID: TERM_001, TERM_002)

| 非学术术语 | 学术术语 | 置信度 |
|----------|--------|--------|
| 超级 | 非常 | 0.95 |
| 特别 | 尤其 | 0.95 |
| 老是 | 始终 | 0.95 |
| 怎么 | 如何 | 0.95 |
| 那么 | 因此 | 0.90 |
| 这样 | 如此 | 0.90 |
| 挺 | 相当 | 0.90 |
| 真 | 确实 | 0.85 |

### 时态调整规则 (Rule ID: TENSE_001, TENSE_002)

- **进行时表达**: 避免"在...着"、"正在...着"等进行时表达
- **非正式标记**: 移除"呢"、"啊"、"吧"等非正式语气词

### 论文规范检查规则 (Rule ID: THESIS_*)

1. **称谓规范**: 
   - "我们的研究" -> "本研究"
   - "笔者认为" -> "根据研究结果"

2. **表述规范**:
   - "可以看出" -> "研究表明"
   - "应该" -> "应当"

3. **逻辑词规范**:
   - "所以" -> "因此"
   - "而且还有" -> "此外"

4. **引用规范**:
   - 要求标准引用格式: (Author Year)

## 配置说明

在 `core/config.py` 中可以配置：

```python
# 润色模块配置（可选扩展）
POLISH_DEFAULT_LEVEL = "standard"
POLISH_AUTO_FIX_THRESHOLD = 0.85  # 自动修复的置信度阈值
POLISH_MAX_TEXT_LENGTH = 50000    # 最大文本长度限制
```

## 错误处理

API 返回的错误响应格式：

```json
{
    "code": 400,
    "message": "请求参数错误",
    "detail": "具体错误信息"
}
```

常见错误码：
- `400`: 请求参数错误
- `404`: 资源不存在
- `500`: 服务器内部错误

## 性能优化

1. **批量处理**: 对大量文本，建议分段提交
2. **缓存**: 相同的分析结果可以缓存使用
3. **异步处理**: 所有数据库操作都是异步的

## 扩展性

模块设计支持以下扩展：

1. **添加新规则**: 在 `AcademicNormalizationService` 中添加新的规则集
2. **自定义规范**: 可以根据不同学科、出版社的要求自定义规范
3. **集成第三方API**: 可以集成专业的语言处理服务
4. **机器学习模型**: 可以集成训练的NLP模型改进准确性

## 测试

运行测试：
```bash
cd backend
pytest test_polish.py -v
```

测试覆盖：
- 单元测试：各个检查方法
- 集成测试：任务创建到导出的完整流程
- API测试：所有端点的功能和错误处理

## 故障排除

### 问题：无法检测到某些问题
- 检查规则是否正确配置
- 验证输入文本格式
- 查看日志中的调试信息

### 问题：性能下降
- 检查数据库连接池配置
- 优化大文本的处理策略
- 考虑使用缓存

### 问题：精度不够高
- 考虑调整置信度阈值
- 添加更多的规则或训练数据
- 使用专业的NLP模型

## 后续开发计划

1. **集成ML模型**: 使用BERT等模型提高准确性
2. **多语言支持**: 扩展到英文、日文等语言
3. **用户偏好学习**: 根据用户反馈自动调整规则
4. **实时协作**: 支持多用户同时编辑和反馈
5. **版本管理**: 跟踪文本的修改历史

---

**版本**: 1.0.0  
**最后更新**: 2026-01-26  
**作者**: AI Office Assistant Team
