/**
 * 流式 API 调用 - 用于实时接收后端的流式数据
 */

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8003";

/**
 * 监听任务的流式输出（实时接收 MD 内容）
 * @param taskId 任务 ID
 * @param onChunk 每收到一个数据块时的回调
 * @param onComplete 完成时的回调
 * @param onError 错误时的回调
 */
export function streamTaskMinutes(
  taskId: string,
  onChunk: (chunk: string) => void,
  onComplete: () => void,
  onError: (error: Error) => void,
): () => void {
  const eventSource = new EventSource(
    `${API_BASE}/api/v1/meetings/tasks/${taskId}/stream`,
  );

  eventSource.addEventListener("message", (event) => {
    try {
      const data = JSON.parse(event.data);
      if (data.minutes) {
        onChunk(data.minutes);
      }
      if (data.summary) {
        onChunk(data.summary);
      }
    } catch (err) {
      console.error("解析流数据失败:", err);
    }
  });

  eventSource.addEventListener("complete", () => {
    eventSource.close();
    onComplete();
  });

  eventSource.addEventListener("error", (event) => {
    eventSource.close();
    onError(
      new Error(
        `流传输错误: ${event.type === "error" ? "连接失败" : event.type}`,
      ),
    );
  });

  // 返回清理函数
  return () => {
    eventSource.close();
  };
}

/**
 * 获取完整的会议纪要（包括流式接收）
 * 先通过轮询检查任务状态，当任务完成时获取完整数据
 */
export async function fetchMeetingMinutesWithStreaming(
  meetingId: string,
  onPartialMinutes: (minutes: string) => void,
  onPartialSummary: (summary: string) => void,
) {
  const eventSource = new EventSource(
    `${API_BASE}/api/v1/meetings/${meetingId}/minutes/stream`,
  );

  return new Promise((resolve, reject) => {
    eventSource.addEventListener("message", (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.minutes) {
          onPartialMinutes(data.minutes);
        }
        if (data.summary) {
          onPartialSummary(data.summary);
        }
      } catch (err) {
        console.error("解析流数据失败:", err);
      }
    });

    eventSource.addEventListener("complete", (event) => {
      try {
        const finalData = JSON.parse((event as any).data);
        eventSource.close();
        resolve(finalData);
      } catch (err) {
        eventSource.close();
        reject(err);
      }
    });

    eventSource.addEventListener("error", () => {
      eventSource.close();
      reject(new Error("流传输连接失败"));
    });
  });
}

/**
 * 备用方案：如果后端不支持 SSE，使用改进的轮询方式
 * 比标准轮询更频繁地检查状态和获取增量数据
 */
export async function pollTaskStatusForMinutes(
  taskId: string,
  onMinutesUpdate: (minutes: string) => void,
  onSummaryUpdate: (summary: string) => void,
  onStepUpdate: (step: number) => void,
  onComplete: () => void,
  onError: (error: Error) => void,
  interval: number = 1000, // 改为 1 秒轮询一次
): Promise<() => void> {
  let lastMinutesLength = 0;
  let lastSummaryLength = 0;
  let isPolling = true;

  const poll = async () => {
    try {
      const response = await fetch(
        `${API_BASE}/api/v1/meetings/tasks/${taskId}`,
      );

      if (!response.ok) {
        throw new Error(`获取任务状态失败: ${response.status}`);
      }

      const data = await response.json();

      // 调试日志
      console.log("📊 轮询结果:", {
        step: data.step,
        minutes: data.minutes ? `${data.minutes.length} chars` : "empty",
        summary: data.summary ? `${data.summary.length} chars` : "empty",
        is_completed: data.is_completed,
        rawData: data,
      });

      // 更新步骤（每次都更新，确保进度条实时反馈）
      if (typeof data.step === "number") {
        onStepUpdate(Math.min(data.step, 4));
      }

      // 仅当数据更新时才触发回调（增量更新）
      if (data.minutes && data.minutes.length > lastMinutesLength) {
        console.log(
          "✅ Minutes 更新:",
          data.minutes.length,
          "->",
          lastMinutesLength,
        );
        onMinutesUpdate(data.minutes);
        lastMinutesLength = data.minutes.length;
      }

      if (data.summary && data.summary.length > lastSummaryLength) {
        console.log(
          "✅ Summary 更新:",
          data.summary.length,
          "->",
          lastSummaryLength,
        );
        onSummaryUpdate(data.summary);
        lastSummaryLength = data.summary.length;
      }

      // 任务完成
      if (data.is_completed) {
        console.log("✅ 任务完成");
        isPolling = false;
        onComplete();
        return;
      }

      // 继续轮询
      if (isPolling) {
        setTimeout(poll, interval);
      }
    } catch (err) {
      console.error("❌ 轮询错误:", err);
      isPolling = false;
      onError(err instanceof Error ? err : new Error(String(err)));
    }
  };

  // 立即开始轮询
  poll();

  // 返回停止轮询的函数
  return () => {
    isPolling = false;
  };
}
