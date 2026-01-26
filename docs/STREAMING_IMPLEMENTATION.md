## 前端流式 MD 输出实现说明

### 📋 概览

前端现已支持 **流式接收** Markdown 数据，有两种实现方式：

### 1️⃣ 优先方案：SSE 流式输出（推荐）

**后端需要实现的端点：**

```python
# FastAPI 示例
from fastapi.responses import StreamingResponse
from fastapi import APIRouter

@router.get("/api/v1/meetings/tasks/{task_id}/stream")
async def stream_task_minutes(task_id: str):
    """
    流式返回任务的 minutes 和 summary 数据
    每次数据更新时发送一个事件
    """
    async def event_generator():
        while True:
            task_data = get_task_status(task_id)  # 从数据库查询

            yield f"data: {json.dumps({
                'minutes': task_data.minutes or '',
                'summary': task_data.summary or '',
                'step': task_data.step
            })}\n\n"

            if task_data.is_completed:
                yield "event: complete\n"
                yield f"data: {json.dumps(task_data)}\n\n"
                break

            await asyncio.sleep(1)  # 每 1 秒发送一次

    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

**前端使用：**

```typescript
import { streamTaskMinutes } from "@/modules/meeting/api/streaming";

const stopStreaming = streamTaskMinutes(
  taskId,
  (minutesChunk) => {
    setMinutes(minutesChunk); // 实时更新
  },
  () => {
    console.log("流传输完成");
  },
  (error) => {
    console.error("流错误:", error);
  },
);

// 需要时停止流
stopStreaming();
```

---

### 2️⃣ 备用方案：改进的流式轮询（当前实现）

**特点：**

- ✅ 无需修改后端（兼容现有 API）
- ✅ 相比标准轮询，增量更新 MD 数据
- ✅ 1 秒轮询一次（比之前的 2 秒更快）
- ⚠️ 网络开销相对较大

**前端实现流程：**

```typescript
// 在 useMeeting Hook 中自动调用
const stopPolling = await pollTaskStatusForMinutes(
  taskId,
  (minutes) => setMinutes(minutes), // 分钟纪要更新
  (summary) => setSummary(summary), // 摘要更新
  () => setCurrentStep(4), // 完成时回调
  (error) => console.error(error), // 错误处理
  1000, // 1 秒轮询间隔
);
```

---

### 📊 对比

| 特性         | SSE 流式   | 改进轮询 |
| ------------ | ---------- | -------- |
| 实时性       | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 网络效率     | ⭐⭐⭐⭐⭐ | ⭐⭐⭐   |
| 实现复杂度   | 中等       | 简单     |
| 需要后端改动 | ✅ 是      | ❌ 否    |
| 连接稳定性   | 需要心跳   | 自动重试 |

---

### 🔄 数据流向

```
后端生成 Markdown
    ↓
每次生成一段就流式发送
    ↓
前端实时接收
    ↓
useMeeting Hook 更新状态
    ↓
messages 数组实时更新
    ↓
UI 组件实时渲染
```

---

### 💡 推荐后端实现

为了最佳体验，建议：

1. **创建流式端点** `GET /api/v1/meetings/tasks/{task_id}/stream`
   - 返回 SSE 格式数据
   - 每生成 100 字符左右发送一次
   - 完成时发送 `event: complete`

2. **保留轮询端点** `GET /api/v1/meetings/tasks/{task_id}`
   - 作为备用方案
   - 支持现有客户端

---

### 🧪 测试方法

**检查流式数据是否正确接收：**

```typescript
// 在 useMeeting Hook 中添加调试
useEffect(() => {
  console.log("📊 Minutes updated:", minutes.length, "chars");
}, [minutes]);

useEffect(() => {
  console.log("📝 Summary updated:", summary.length, "chars");
}, [summary]);
```

**在浏览器 DevTools 中查看：**

1. Network 标签 → 找到 `/stream` 请求
2. Response 标签 → 查看 SSE 数据格式
3. 或观察 console 输出

---

### ⚠️ 注意事项

1. **CORS 配置**：SSE 需要正确的 CORS 设置

   ```python
   from fastapi.middleware.cors import CORSMiddleware
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **心跳保活**：长连接需要定期发送心跳

   ```python
   yield f": heartbeat\n\n"  # 每 30 秒一次
   ```

3. **超时处理**：设置合理的连接超时
   ```python
   # 在 nginx/gunicorn 中配置
   proxy_read_timeout 3600s;
   ```

---

### 📦 当前实现状态

✅ **前端已准备好：**

- `streamTaskMinutes()` - SSE 版本（待后端）
- `pollTaskStatusForMinutes()` - 当前使用中
- `fetchMeetingMinutesWithStreaming()` - 增量式 SSE（待后端）

⏳ **后端需要：**

- 实现 `/stream` 流式端点
- 或保证 `minutes` 字段实时更新（当前轮询方案）
