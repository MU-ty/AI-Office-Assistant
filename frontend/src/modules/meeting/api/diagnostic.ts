/**
 * 诊断和备用轮询策略
 * 当主轮询方案没有获取到 minutes/summary 时的备选方案
 */

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export interface TaskStatusResponse {
  task_id: string;
  meeting_id: string;
  step: number;
  is_completed: boolean;
  content?: string;
  status?: string;
  summary?: string;
  minutes?: string;
}

/**
 * 诊断轮询 - 获取完整的任务状态
 * 用于在主轮询方案失败时作为备选方案
 */
export async function diagnosticPoll(
  taskId: string,
  onStatusUpdate: (status: TaskStatusResponse) => void,
  onComplete: () => void,
  onError: (error: Error) => void,
  interval: number = 1000,
): Promise<() => void> {
  let isPolling = true;
  let pollCount = 0;

  const poll = async () => {
    try {
      const response = await fetch(
        `${API_BASE}/api/v1/meetings/tasks/${taskId}`,
      );

      if (!response.ok) {
        throw new Error(`获取任务状态失败: ${response.status}`);
      }

      const data: TaskStatusResponse = await response.json();
      pollCount++;

      // 诊断输出
      console.log(
        `\n🔍 第 ${pollCount} 次轮询 (${new Date().toLocaleTimeString()}):`,
      );
      console.log("  step:", data.step);
      console.log("  is_completed:", data.is_completed);
      console.log(
        "  content:",
        data.content ? `有 (${data.content.length} chars)` : "无",
      );
      console.log(
        "  summary:",
        data.summary ? `有 (${data.summary.length} chars)` : "无",
      );
      console.log(
        "  minutes:",
        data.minutes ? `有 (${data.minutes.length} chars)` : "无",
      );
      console.log("  status:", data.status);
      console.log("  完整数据:", JSON.stringify(data, null, 2));

      // 调用回调函数
      onStatusUpdate(data);

      // 任务完成
      if (data.is_completed) {
        console.log("\n✅ 任务标记为完成");
        isPolling = false;
        onComplete();
        return;
      }

      // 继续轮询
      if (isPolling) {
        setTimeout(poll, interval);
      }
    } catch (err) {
      console.error("❌ 诊断轮询错误:", err);
      isPolling = false;
      onError(err instanceof Error ? err : new Error(String(err)));
    }
  };

  // 立即开始轮询
  poll();

  // 返回停止轮询的函数
  return () => {
    isPolling = false;
    console.log("🛑 停止轮询");
  };
}
