# 会议纪要功能完整实现指南

## ✅ 已完成的功能

### 后端处理流程（4个完整步骤）

后端在 `backend/app/services/meeting_minutes_service.py` 中实现了完整的异步工作流：

#### 第1步：音视频转录 (2秒模拟)

```
上传成功 → 调用转录API (Whisper/Qwen-audio) → 获取转录文本
```

- 验证文件格式（mp3, wav, m4a, webm, mp4）
- 保存文件到 `uploads/` 目录
- 触发异步转录任务
- 返回 `task_id` 供前端轮询

#### 第2步：语义分析与标注 (2秒模拟)

```
分句、分段 → 提取关键词 → 实体识别 → 话题划分
```

- NLP 处理（通过 `NLPService`）
- 提取关键词、关键句
- 识别实体（日期、时间、人物等）
- 分析文本统计

#### 第3步：核心信息提取 (2秒模拟)

```
议程提取 → 决议识别 → Action Items提取 → 关键点汇总
```

- 议程清单生成
- 决议内容提取
- 任务项识别（包含负责人、截止日期）
- 汇总关键讨论点

#### 第4步：生成最终纪要 (2秒模拟)

```
数据组织 → 格式生成 (Markdown/JSON/PDF/Word) → 保存文件
```

- Markdown 格式：可编辑、版本控制友好
- JSON 格式：结构化数据
- PDF/Word：可选（需安装 reportlab/python-docx）
- 返回完整纪要内容和执行摘要

---

## 📊 前端用户界面

### 主要组件

1. **左侧工作流进度条** (`MeetingStepper.tsx`)
   - 显示 4 个处理步骤的状态
   - 彩色指示：灰色(待处理) → 蓝色(处理中) → 绿色(已完成)
   - 实时进度百分比展示

2. **文件上传区** (`Uploader.tsx`)
   - 点击上传按钮选择音视频文件
   - 上传后自动禁用（防止重复上传）
   - 完成后可重新上传

3. **实时内容展示** (`index.tsx`)
   - **处理过程日志**：显示每个步骤的进度信息
   - **执行摘要**：关键议题、核心内容预览
   - **完整纪要**：结构化的会议记录
     - 基本信息（会议日期、参与人）
     - 议程列表
     - 关键点汇总
     - 决议事项
     - Action Items（任务、负责人、截止日期）

4. **操作按钮**
   - **下载 Markdown**：导出为文本编辑格式
   - **分享纪要**：分享到邮件、企业微信、钉钉（可扩展）

---

## 🔄 数据流转过程

### 前端请求流程

```
用户上传文件
    ↓
createMeeting() - 创建会议
    ↓
uploadMeetingAudio() - 上传文件 → 获取 task_id
    ↓
setInterval - 每2秒轮询一次
    ↓
fetchTaskStatus(task_id) - 获取任务状态
    ↓
更新 UI（步骤/内容/纪要）
    ↓
当 is_completed=true 时停止轮询，展示完整结果
```

### 后端异步处理流程

```
接收文件上传请求 → 校验 → 保存文件
    ↓
_start_transcription_task()
    ├─ 初始化任务状态
    └─ asyncio.create_task(_process_full_workflow)
        ↓
_process_full_workflow() - 完整处理链
    ├─ 步骤1: 模拟转录 (await asyncio.sleep(2))
    │   └─ 生成转录文本 → 更新 step=1
    │
    ├─ 步骤2: NLP 分析 (await asyncio.sleep(2))
    │   └─ process_transcription() → 提取信息 → 更新 step=2
    │
    ├─ 步骤3: 关键信息提取 (await asyncio.sleep(2))
    │   └─ 组织数据 → 更新 step=3
    │
    ├─ 步骤4: 生成纪要 (await asyncio.sleep(2))
    │   └─ generate_meeting_minutes()
    │       └─ 生成 Markdown → 保存文件 → 更新 step=4
    │
    └─ 标记完成: is_completed=true
```

---

## 🛠️ API 端点汇总

### 核心端点

| 方法 | 端点                                    | 说明                     |
| ---- | --------------------------------------- | ------------------------ |
| POST | `/api/v1/meetings`                      | 创建会议记录             |
| POST | `/api/v1/meetings/{meeting_id}/upload`  | 上传音视频并启动转录     |
| GET  | `/api/v1/meetings/tasks/{task_id}`      | 查询任务状态（前端轮询） |
| GET  | `/api/v1/meetings/{meeting_id}/minutes` | 获取已生成的纪要         |
| POST | `/api/v1/meetings/{meeting_id}/export`  | 导出纪要文件             |

### 查询端点

| 方法 | 端点                                         | 说明              |
| ---- | -------------------------------------------- | ----------------- |
| GET  | `/api/v1/meetings/{meeting_id}/participants` | 获取参与人列表    |
| GET  | `/api/v1/meetings/{meeting_id}/agendas`      | 获取议程列表      |
| GET  | `/api/v1/meetings/{meeting_id}/decisions`    | 获取决议列表      |
| GET  | `/api/v1/meetings/{meeting_id}/action-items` | 获取 Action Items |

---

## 📝 任务状态响应示例

### 轮询响应格式

```json
{
  "task_id": "task_meeting_001_1234567890",
  "meeting_id": "meeting_001",
  "step": 2, // 当前步骤 0-4
  "is_completed": false, // 是否完成
  "content": "✓ 音视频转录完成\n✓ 语义分析完成\n→ 正在提取议程和决议...",
  "status": "processing", // 状态: transcribing/processing/completed/failed
  "summary": "## 执行摘要\n\n**关键议题**: 市场拓展、技术开发、人员招聘...",
  "minutes": "# 会议纪要\n\n## 基本信息\n..."
}
```

---

## 🎬 完整演示流程（总耗时约10秒）

1. **0s**：上传文件 → 创建会议 → 返回 task_id
2. **2s**：第1步完成 - 转录文本生成
3. **4s**：第2步完成 - NLP 分析完成
4. **6s**：第3步完成 - 议程/决议提取
5. **8s**：第4步完成 - 纪要文档生成
6. **10s**：显示完整结果，可下载/分享

---

## 🚀 启动指令

### 后端启动

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

数据库自动初始化，文件保存至 `backend/uploads/` 和 `backend/data/`

### 前端启动

```bash
cd frontend
pnpm dev
# 访问 http://localhost:3000/meeting
```

---

## 📦 文件存储位置

| 内容      | 路径                                  | 说明                      |
| --------- | ------------------------------------- | ------------------------- |
| 数据库    | `backend/data/office_assistant.db`    | SQLite 数据库（自动创建） |
| 上传文件  | `backend/uploads/`                    | 音视频原文件              |
| 转录文本  | `backend/uploads/{meeting_id}_*.md`   | Markdown 纪要             |
| JSON 纪要 | `backend/uploads/{meeting_id}_*.json` | 结构化数据                |

---

## 🔧 配置说明

### 环境变量 (`.env`)

```
NEXT_PUBLIC_API_BASE=http://localhost:8000
DB_TYPE=sqlite
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=500MB
```

### 轮询间隔

- 前端: 2秒轮询一次（可在 `useMeeting.ts` 中调整）
- 总处理时间: ~10秒（包含模拟延迟）

---

## 🎯 下一步扩展方向

### 短期

- [ ] 集成真实 ASR（Whisper API 或本地部署）
- [ ] 集成真实 NLP（Qwen、ChatGPT API）
- [ ] 支持多语言转录和翻译

### 中期

- [ ] 支持 PDF/Word 文档导出
- [ ] 邮件发送纪要功能
- [ ] 企业微信/钉钉集成分享
- [ ] 数据库持久化（当前为内存）

### 长期

- [ ] 会议知识库构建
- [ ] 实时转录（WebSocket）
- [ ] 智能摘要生成
- [ ] 多会议对比分析

---

## ⚠️ 当前限制

1. **模拟处理**：使用 `asyncio.sleep()` 模拟各步骤，实际场景需集成真实 API
2. **内存存储**：任务状态和会议数据存储在内存中，重启后清空
3. **无身份认证**：当前实现无用户认证，生产环境需添加 JWT/OAuth
4. **单文件上传**：当前仅支持单个文件上传，可扩展为批量

---

## 📞 调试技巧

### 查看后端日志

```bash
# 查看任务状态流转
tail -f backend/logs/*.log | grep "task_"
```

### 测试 API

```bash
# 创建会议
curl -X POST http://localhost:8000/api/v1/meetings \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","meeting_type":"audio","start_time":"2025-01-26T10:00:00Z"}'

# 查询任务状态
curl http://localhost:8000/api/v1/meetings/tasks/task_meeting_001_1234567890
```

---

## 总结

✅ **会议纪要功能** 已完整实现 4 个处理步骤：

1. 音视频转录
2. 语义分析
3. 议程提取
4. 纪要生成

前后端已完全对接，支持实时进度展示和完整结果查看。
