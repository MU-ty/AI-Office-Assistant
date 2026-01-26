## 问题解决：会议纪要正确显示

### 🎯 问题根源

后端的 **任务状态** 和 **纪要内容** 是通过两个不同的接口返回的：

1. **任务状态接口** `GET /api/v1/meetings/tasks/{task_id}`
   - 返回：`step`, `content`, `status`, `is_completed`
   - ❌ **不包含** `minutes` 和 `summary`

2. **纪要获取接口** `GET /api/v1/meetings/{meeting_id}/minutes`
   - 返回：完整的会议纪要 JSON 数据
   - 包含：`paragraphs`, `decisions`, `action_items`, `key_points` 等

### ✅ 解决方案

**两阶段流程：**

```
阶段1: 轮询任务状态
  ↓
监控 step 和 is_completed
  ↓
阶段2: 任务完成后
  ↓
调用纪要接口获取完整数据
  ↓
转换 JSON → Markdown
  ↓
显示在前端
```

### 📝 实现细节

#### 1. 任务完成回调增强

```typescript
async () => {
  // 任务完成后，调用纪要接口
  const minutesData = await fetchMeetingMinutes(meetingId);

  // JSON → Markdown 转换
  const markdown = convertMinutesJSONToMarkdown(minutesData);
  const summary = generateSummary(minutesData);

  setMinutes(markdown);
  setSummary(summary);
};
```

#### 2. JSON 转 Markdown 转换器

创建了 `minutesConverter.ts` 来处理：

- ✅ 标题和元信息
- ✅ 参与者列表
- ✅ 会议内容（段落）
- ✅ 关键要点
- ✅ 决议事项
- ✅ Action Items（表格格式）
- ✅ 统计信息

生成的 Markdown 示例：

```markdown
# 会议纪要 - meeting_1769430499

**日期：** 2026-01-26 20:28:27

## 参与者

- 参与者1
- 参与者2
- 参与者3

## 会议内容

各位好，今天的会议主要讨论Q1季度的工作计划和重点项目。

首先，我们来看市场部的工作进展。上个月完成了三个大客户的合作谈判...

## 关键要点

- 关键点: 各位好，今天的会议主要讨论Q1季度的工作计划和重点项目
- 关键点: 首先，我们来看市场部的工作进展
  ...

## 关键决议

- 决议: 批准新产品项目的开发预算500万元
  ...

## 行动事项

| 任务                         | 负责人 | 截止日期 |
| ---------------------------- | ------ | -------- |
| 市场部制定详细的客户拓展方案 | 张三   | 3月15日  |
| 技术部完成API接口设计文档    | 李四   | 3月10日  |

...
```

### 🔄 完整流程

```
用户上传文件
  ↓
创建会议记录
  ↓
上传音频
  ↓
开始轮询任务状态 (每 1 秒)
  ├─ step: 0 → "正在分析..."
  ├─ step: 1 → "音视频转录完成"
  ├─ step: 2 → "语义分析完成"
  ├─ step: 3 → "议程提取完成"
  └─ step: 4, is_completed: true
       ↓
    调用纪要接口
       ↓
    获取 JSON 数据
       ↓
    转换为 Markdown
       ↓
    显示在聊天气泡中
```

### 📊 修改的文件

| 文件                        | 改动说明                 |
| --------------------------- | ------------------------ |
| `hooks/useMeeting.ts`       | 任务完成后调用纪要接口   |
| `utils/minutesConverter.ts` | JSON → Markdown 转换器   |
| `api/diagnostic.ts`         | 诊断轮询工具（用于调试） |

### 🎉 现在的效果

1. ✅ **进度条正确更新** - 从 1/4 到 4/4 逐步递进
2. ✅ **处理进度实时显示** - "转录完成" → "分析完成" 等
3. ✅ **完整纪要正确展示** - Markdown 格式，包含所有内容
4. ✅ **执行摘要生成** - 自动提取关键决议和 Action Items
5. ✅ **完成后界面保持** - 用户可以查看、下载

### 🧪 测试验证

上传文件后，Console 会显示：

```
🚀 开始轮询任务: task_meeting_xxx

🔍 第 1 次轮询:
  step: 0

🔍 第 9 次轮询:
  step: 4
  is_completed: true

✅ 诊断轮询完成，开始获取完整纪要
📄 收到完整纪要数据: {...}
🔄 检测到 JSON 格式，转换为 Markdown
```

然后前端会显示：

- 📝 实时纪要（蓝色背景）
- 📋 执行摘要
- ✅ "查看完整纪要"按钮
