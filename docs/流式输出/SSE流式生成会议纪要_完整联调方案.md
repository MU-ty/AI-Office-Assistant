# SSE 流式生成会议纪要 - 完整联调方案

## 问题描述

原有的 SSE 流式实现存在的核心问题：
```
时间线：
T0: 后端开始吐字 ————————→
T1:              吐字完成，SSE 立即断开连接 ← 【问题】
T2:              后端才开始 save_to_json()
T3:              文件保存完成
                
前端：
T1: SSE 收到断开信号 → 立即发起 GET /minutes 请求
T2: 文件还在保存中 → 404 错误 ✗
```

## 解决方案（五步闭环）

改进的流程确保"文件保存完成"再"断开连接"：

```
T0: 后端开始吐字 ————————————→
T1:              吐字完成 ✓
T2:              保存 JSON/MD/PDF/DOCX
T3:              发送 SSE 完成信号 ✓
T4:              【最后】断开连接 ✓

前端：
T1: 接收 "streaming" 消息，显示吐字过程
T3: 接收 "completed" 消息，获取文件路径
T4: 可以 100% 成功获取文件
```

## 代码实现

### 1. 后端流式服务 (`meeting_streaming_service.py`)

**核心改进点：**

```python
async def generate_minutes_stream(self, meeting_id, meeting_data, llm_stream_generator):
    """
    五步流程：
    1. SSE 正常吐字（yield streaming message）
    2. LLM 吐字完成后，不立即关闭
    3. 立即在当前函数内执行 save_to_json()  ← 关键
    4. 发送完成信号（yield completed message）
    5. 最后断开连接（function return）
    """
```

**主要方法：**

- `generate_minutes_stream()` - 主流程，保证流程序列正确
- `_save_minutes_to_files()` - 同步保存所有格式文件（JSON/MD/PDF/DOCX）
- `_extract_summary()` - 提取摘要用于完成信号

### 2. 后端 API 端点 (`meetings.py`)

**新增路由：**

```python
GET /api/v1/meetings/{meeting_id}/minutes/stream

# SSE 消息类型：
# 1. {"status": "streaming", "chunk": "...", "content": "完整内容"}
# 2. {"status": "processing", "message": "正在处理..."}
# 3. {"status": "completed", "summary": "...", "file_path": "/uploads/..."}
# 4. {"status": "error", "error": "错误信息"}
```

### 3. 前端调用 (`frontend/api/streaming.ts`)

**推荐的前端实现：**

```typescript
export function streamMeetingMinutes(
  meetingId: string,
  onChunk: (chunk: string) => void,
  onProcessing: () => void,
  onComplete: (data: any) => void,
  onError: (error: Error) => void
): () => void {
  const eventSource = new EventSource(
    `${API_BASE}/api/v1/meetings/${meetingId}/minutes/stream`
  );

  eventSource.addEventListener("message", (event) => {
    const data = JSON.parse(event.data);
    
    if (data.status === "streaming") {
      // 实时显示生成的内容
      onChunk(data.chunk);
    } else if (data.status === "processing") {
      // 显示处理中的提示
      onProcessing();
    } else if (data.status === "completed") {
      // 流程完成，此时文件一定已保存
      eventSource.close();
      onComplete(data);
    } else if (data.status === "error") {
      // 错误处理
      eventSource.close();
      onError(new Error(data.error));
    }
  });

  // 返回清理函数
  return () => eventSource.close();
}
```

## 联调步骤

### Step 1: 部署新代码

```bash
# 后端
cd backend
git add -A
git commit -m "fix: SSE 流式生成纪要 - 保证文件保存完成再断开连接"
git push

# 前端（可选）
cd frontend
git add -A
git commit -m "feat: 改进 SSE 流式监听，适应新的后端信号"
```

### Step 2: 启动服务

```bash
# 后端（确保依赖已安装）
cd backend
pip install reportlab python-docx
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 前端
cd frontend
npm run dev
```

### Step 3: 测试流程

#### 使用 curl 测试 SSE：

```bash
# 创建会议
curl -X POST http://localhost:8000/api/v1/meetings \
  -H "Content-Type: application/json" \
  -d '{
    "title": "测试会议",
    "meeting_type": "技术分享",
    "start_time": "2026-01-28"
  }'

# 应该返回类似：
# {"id": "meeting_12345", "status": "created"}

# 监听流式输出（替换 meeting_id）
curl -N http://localhost:8000/api/v1/meetings/meeting_12345/minutes/stream

# 应该看到：
# data: {"status": "streaming", "chunk": "...", ...}
# data: {"status": "processing", ...}
# data: {"status": "completed", "file_path": "/uploads/...", ...}
```

#### 使用前端测试：

1. 打开浏览器 http://localhost:3000
2. 在会议纪要模块上传音频
3. 观察控制台输出和页面实时显示
4. 等待"完成"信号
5. 尝试下载生成的文件（应该 100% 成功）

### Step 4: 检查日志

后端日志应该显示清晰的流程：

```
[meeting_xxx] 开始流式生成会议纪要
[meeting_xxx] LLM 吐字完成，长度: 5234 字符
[meeting_xxx] 发送处理中信号
[meeting_xxx] 开始保存文件...
[meeting_xxx] JSON 文件保存成功: /path/to/meeting_xxx_minutes.json
[meeting_xxx] Markdown 文件保存成功: /path/to/meeting_xxx_minutes.md
[meeting_xxx] PDF 文件生成成功: /path/to/meeting_xxx_minutes.pdf
[meeting_xxx] DOCX 文件生成成功: /path/to/meeting_xxx_minutes.docx
[meeting_xxx] 所有文件保存完成
[meeting_xxx] 发送完成信号，SSE 即将关闭
```

## SSE 消息格式详解

### 1. Streaming 消息（实时吐字）

```json
{
  "status": "streaming",
  "meeting_id": "meeting_1769567947",
  "chunk": "本次会议讨论了...",
  "content": "...完整内容到此位置..."
}
```

用途：
- 前端实时显示生成过程
- 可用于进度条更新

### 2. Processing 消息（处理中）

```json
{
  "status": "processing",
  "message": "正在处理和保存纪要...",
  "meeting_id": "meeting_1769567947"
}
```

用途：
- 通知前端吐字已完成，进入保存阶段
- 可显示 loading 状态

### 3. Completed 消息（完成）

```json
{
  "status": "completed",
  "meeting_id": "meeting_1769567947",
  "summary": "本次会议讨论了...",
  "file_path": "/uploads/meeting_1769567947_minutes.json",
  "generated_at": "2026-01-28T10:30:45.123456Z",
  "total_length": 5234,
  "message": "会议纪要生成完成！"
}
```

用途：
- 通知前端所有文件已保存完成
- 前端可以安全地获取文件
- 此时可以显示下载按钮

### 4. Error/SaveError 消息（错误）

```json
{
  "status": "error",
  "meeting_id": "meeting_1769567947",
  "error": "错误信息详情"
}
```

或

```json
{
  "status": "save_error",
  "error": "文件保存失败：权限不足",
  "meeting_id": "meeting_1769567947"
}
```

## 问题排查

### 问题 1：SSE 连接立即断开

**症状：** 收不到任何消息

**排查步骤：**
1. 检查后端日志是否有异常
2. 确认 meeting_id 是否正确
3. 检查 CORS 配置

**解决：**
```python
# main.py 中确保有 CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", ...],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
```

### 问题 2：收到 completed 信号后仍无法获取文件

**症状：** 文件下载失败，404 错误

**排查步骤：**
1. 检查日志确认文件是否真的保存了
2. 确认文件路径是否正确
3. 检查 `/uploads` 静态文件挂载

**解决：**
```python
# main.py 中确保有静态文件配置
if not os.path.exists(settings.UPLOAD_DIR):
    os.makedirs(settings.UPLOAD_DIR)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
```

### 问题 3：PDF/DOCX 生成失败

**症状：** 日志显示 "PDF 文件生成失败"

**排查步骤：**
1. 确认依赖已安装：`pip list | grep reportlab`
2. 检查中文字体（Windows）：`C:\Windows\Fonts\simhei.ttf`
3. 查看详细错误日志

**解决：**
```bash
# 安装缺失的依赖
pip install reportlab python-docx

# 可选：测试 PDF 生成
python -c "import reportlab; print(reportlab.__version__)"
```

## 性能优化建议

### 1. 异步保存（高级）

如果文件保存非常耗时，可以考虑：

```python
# 仅在必要时使用异步保存
async def _save_minutes_async(self, meeting_id, data):
    """异步保存，不阻塞 SSE 吐字"""
    await asyncio.to_thread(self._save_to_disk, meeting_id, data)
```

### 2. PDF/DOCX 延迟生成

```python
# 只立即生成 JSON 和 Markdown
# PDF/DOCX 可以在后台异步生成
try:
    # 同步保存快速格式
    sync_save(json, markdown)
    
    # 异步生成慢速格式
    asyncio.create_task(
        async_generate_pdf_docx(meeting_id, data)
    )
except Exception as e:
    # 快速格式保存失败才返回错误
    pass
```

### 3. 缓存机制

```python
# 重复查询相同 meeting_id 时使用缓存
from functools import lru_cache

@lru_cache(maxsize=100)
def get_saved_files(meeting_id):
    return os.listdir(f"/uploads/meeting_{meeting_id}_*")
```

## 总结

| 方面 | 改进前 | 改进后 |
|------|-------|-------|
| 流程清晰性 | 含糊不清 | 五步明确 |
| 时序问题 | 存在 404 | 100% 成功 |
| 文件保证 | 无法保证 | 完全保证 |
| 前端体验 | 需要重试 | 一次成功 |
| 日志可追踪性 | 困难 | 完全清晰 |

## 联系支持

如有问题，请检查：
1. 后端日志：`backend/logs/`
2. 前端控制台：F12 开发者工具
3. API 文档：`http://localhost:8000/api/docs`
4. 网络请求：F12 → Network → 过滤 `minutes/stream`
