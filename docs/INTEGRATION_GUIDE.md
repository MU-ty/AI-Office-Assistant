## 会议纪要功能集成完成指南

### 功能流程

```
用户上传录音/文档
  ↓
后端分析生成 MD
  ↓
前端轮询任务状态
  ↓
任务完成后显示消息
  ↓
用户可查看/下载完整纪要
```

### 已实现的功能

#### 1. **核心 Hook: `useMeeting`**
   - 管理会议状态、上传工作流、轮询机制
   - 导出：`steps`, `messages`, `minutes`, `summary`, `meetingTitle`, `generatedAt`
   - 支持加载已有纪要

#### 2. **消息聚合系统**
   - `content`: 处理进度（转录、标注、提取等）
   - `summary`: 执行摘要
   - `minutes`: 完整纪要（通过 `minutesToMessages` 分段显示）

#### 3. **MarkdownViewer 组件**
   - 完整 MD 内容预览（模态框）
   - 复制到剪贴板
   - 下载文件功能
   - 显示生成时间和会议 ID

#### 4. **主页面集成**
   - 左侧：工作流步骤进度
   - 右侧：聊天气泡形式的消息流
   - 消息实时更新（2 秒轮询一次）
   - 完成后显示"查看完整纪要"按钮

### 消息显示逻辑

```javascript
// 在 startWorkflow 或 loadExistingMinutes 时触发
1. content → 显示为 "进度" 标签的消息
2. summary → 显示为 "执行摘要" 标签的消息
3. minutes → 按段落分割显示为多条消息

// 显示条件
- isStarted 且 messages.length > 0 → 显示消息列表
- isStarted 且 messages.length === 0 → 显示 Loading 态
- !isStarted → 显示初始上传界面
```

### 关键代码集成点

**1. Hook 返回值** ([useMeeting.ts](useMeeting.ts#L195-L210))
```typescript
return {
  steps,
  messages,           // ✅ 聊天消息列表
  minutes,            // ✅ 完整纪要（用于下载/预览）
  summary,            // ✅ 摘要
  meetingTitle,       // ✅ 会议标题
  generatedAt,        // ✅ 生成时间
  ...
};
```

**2. 主页面消息显示** ([index.tsx](index.tsx#L155-L180))
```tsx
{isStarted && messages.length === 0 ? (
  <Loading />
) : messages.length > 0 ? (
  <MessageList messages={messages} />
) : null}
```

**3. MarkdownViewer 集成** ([index.tsx](index.tsx#L108-L115))
```tsx
{currentStep === 4 && minutes && (
  <MarkdownViewer
    content={minutes}
    title={meetingTitle || "会议纪要"}
    meetingId={meetingId}
    generatedAt={generatedAt}
  />
)}
```

### 文件结构

```
frontend/src/modules/meeting/
├── api.ts                          # API 请求函数
├── hooks/
│   └── useMeeting.ts              # 核心逻辑 Hook
├── components/
│   ├── MarkdownViewer.tsx         # 完整纪要查看器
│   ├── Stepper.tsx               # 步骤显示组件
│   └── Uploader.tsx              # 文件上传组件
├── utils/
│   └── minutesToMessages.ts       # MD 转聊天消息
├── services/
│   └── meetingService.ts          # 可选，备用 API 层
└── index.tsx                      # 主页面
```

### 调试技巧

**查看消息是否正确生成：**
```typescript
// 在 useMeeting.ts 中添加
useEffect(() => {
  console.log("Current messages:", messages);
}, [messages]);
```

**检查 API 响应格式：**
```javascript
// 在浏览器控制台查看 Network 标签
// GET /api/v1/meetings/tasks/{taskId}
// 应该返回：{ task_id, step, is_completed, minutes, summary, ... }

// GET /api/v1/meetings/{meetingId}/minutes
// 应该返回：{ minutes, summary, title, ... }
```

### 可能的问题排查

| 问题 | 原因 | 解决方案 |
|------|------|--------|
| 消息不显示 | messages 数组为空 | 检查 `minutes` 或 `summary` 是否为空 |
| 轮询停止 | 后端未返回 `is_completed: true` | 检查后端任务状态接口 |
| MarkdownViewer 按钮不显示 | `currentStep !== 4` 或 `minutes` 为空 | 检查轮询时 step 更新 |
| 样式错乱 | Dialog 组件缺失 | 已在 `components/ui/dialog.tsx` 中定义 |

### 后续优化方向

- [ ] 支持 WebSocket 实时推送（替代轮询）
- [ ] 添加撤销/恢复功能
- [ ] 支持编辑和注解
- [ ] 导出为 PDF/Word 格式
- [ ] 会议纪要历史管理
