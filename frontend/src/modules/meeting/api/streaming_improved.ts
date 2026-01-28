/**
 * 改进的 SSE 流式监听实现
 * 与后端的五步流程完全对应
 * 
 * 核心改进：
 * - 正确处理 "streaming", "processing", "completed" 三个状态
 * - 不在吐字完成时立即请求文件，而是等待 "completed" 信号
 * - 支持实时显示吐字进度
 */

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

/**
 * 流式生成会议纪要
 * 与后端五步流程同步：
 * 1. streaming: 实时吐字
 * 2. processing: 后端保存文件中
 * 3. completed: 文件保存完成，可以获取
 * 4. error/save_error: 处理错误
 * 
 * @param meetingId 会议ID
 * @param callbacks 回调函数集合
 * @returns 清理函数
 */
export function streamMeetingMinutesImproved(
  meetingId: string,
  callbacks: {
    onStreaming?: (chunk: string, fullContent: string) => void;
    onProcessing?: (message: string) => void;
    onComplete?: (data: any) => void;
    onError?: (error: Error) => void;
  }
) {
  const eventSource = new EventSource(
    `${API_BASE}/api/v1/meetings/${meetingId}/minutes/stream`
  );

  eventSource.addEventListener("message", (event) => {
    try {
      const data = JSON.parse(event.data);
      console.log("[SSE] 收到消息:", data.status, data);

      switch (data.status) {
        case "streaming":
          // ✓ 第一步：实时吐字
          if (callbacks.onStreaming) {
            callbacks.onStreaming(data.chunk || "", data.content || "");
          }
          break;

        case "processing":
          // ✓ 第二步：后端开始保存文件
          console.log("[SSE] 后端正在保存文件...");
          if (callbacks.onProcessing) {
            callbacks.onProcessing(data.message || "正在保存...");
          }
          break;

        case "completed":
          // ✓ 第三步：文件保存完成，此时可以安全获取
          console.log("[SSE] 文件保存完成，纪要生成成功！");
          eventSource.close();
          
          if (callbacks.onComplete) {
            callbacks.onComplete({
              status: "success",
              summary: data.summary,
              filePath: data.file_path,
              generatedAt: data.generated_at,
              message: data.message
            });
          }
          break;

        case "save_error":
          // × 错误：文件保存失败
          console.error("[SSE] 文件保存失败:", data.error);
          eventSource.close();
          if (callbacks.onError) {
            callbacks.onError(new Error(`保存失败: ${data.error}`));
          }
          break;

        case "error":
          // × 错误：通用错误
          console.error("[SSE] 错误:", data.error);
          eventSource.close();
          if (callbacks.onError) {
            callbacks.onError(new Error(data.error));
          }
          break;

        default:
          console.warn("[SSE] 未知状态:", data.status);
      }
    } catch (err) {
      console.error("[SSE] 解析数据失败:", err);
      if (callbacks.onError) {
        callbacks.onError(new Error(`解析失败: ${err}`));
      }
    }
  });

  eventSource.addEventListener("error", () => {
    console.error("[SSE] 连接错误");
    eventSource.close();
    if (callbacks.onError) {
      callbacks.onError(new Error("SSE 连接失败"));
    }
  });

  // 返回清理函数
  return () => {
    console.log("[SSE] 手动关闭连接");
    eventSource.close();
  };
}

/**
 * 高级：使用 React Hooks 的流式生成
 * 
 * 使用示例：
 * const { content, isStreaming, isProcessing, isComplete, error, cleanup } = 
 *   useStreamMeetingMinutes(meetingId);
 */
export function useStreamMeetingMinutes(meetingId: string) {
  const [content, setContent] = React.useState("");
  const [isStreaming, setIsStreaming] = React.useState(false);
  const [isProcessing, setIsProcessing] = React.useState(false);
  const [isComplete, setIsComplete] = React.useState(false);
  const [error, setError] = React.useState<Error | null>(null);
  const cleanupRef = React.useRef<() => void | null>(null);

  React.useEffect(() => {
    setIsStreaming(true);
    setIsProcessing(false);
    setIsComplete(false);
    setError(null);
    setContent("");

    cleanupRef.current = streamMeetingMinutesImproved(meetingId, {
      onStreaming: (chunk, fullContent) => {
        setContent(fullContent);
      },
      onProcessing: (message) => {
        setIsStreaming(false);
        setIsProcessing(true);
      },
      onComplete: (data) => {
        setIsProcessing(false);
        setIsComplete(true);
      },
      onError: (err) => {
        setIsStreaming(false);
        setIsProcessing(false);
        setError(err);
      }
    });

    return () => {
      if (cleanupRef.current) {
        cleanupRef.current();
      }
    };
  }, [meetingId]);

  return {
    content,
    isStreaming,
    isProcessing,
    isComplete,
    error,
    cleanup: cleanupRef.current || (() => {})
  };
}

/**
 * 下载生成的文件
 * 在收到 "completed" 信号后调用
 * 
 * @param meetingId 会议ID
 * @param format 格式：markdown, json, pdf, docx
 */
export async function downloadGeneratedMinutes(
  meetingId: string,
  format: "markdown" | "json" | "pdf" | "docx" = "markdown"
) {
  try {
    const filePath = `/uploads/meeting_${meetingId}_minutes.${
      format === "markdown" ? "md" : format
    }`;

    const response = await fetch(`${API_BASE}${filePath}`);
    
    if (!response.ok) {
      throw new Error(`下载失败: ${response.status} ${response.statusText}`);
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `meeting_${meetingId}_minutes.${
      format === "markdown" ? "md" : format
    }`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);

    console.log(`[下载] 文件下载成功: ${format}`);
  } catch (error) {
    console.error(`[下载] 文件下载失败: ${error}`);
    throw error;
  }
}

/**
 * 诊断工具：监控 SSE 消息流
 * 用于调试和问题排查
 */
export function diagnosticStreamMeeting(meetingId: string) {
  console.log(`[诊断] 开始监控: ${meetingId}`);
  
  const stats = {
    chunks: 0,
    totalLength: 0,
    startTime: Date.now(),
    endTime: null as number | null,
    states: [] as string[]
  };

  const cleanup = streamMeetingMinutesImproved(meetingId, {
    onStreaming: (chunk, fullContent) => {
      stats.chunks++;
      stats.totalLength = fullContent.length;
      console.log(
        `[诊断] 吐字中... [${stats.chunks}] 当前长度: ${stats.totalLength}`
      );
    },
    onProcessing: (message) => {
      stats.states.push("processing");
      console.log(`[诊断] 处理中: ${message}`);
    },
    onComplete: (data) => {
      stats.states.push("completed");
      stats.endTime = Date.now();
      const duration = (stats.endTime - stats.startTime) / 1000;
      
      console.log("[诊断] ═════════════════════════════════════");
      console.log(`[诊断] 生成完成！`);
      console.log(`[诊断] 总吐字数: ${stats.chunks}`);
      console.log(`[诊断] 总长度: ${stats.totalLength} 字符`);
      console.log(`[诊断] 耗时: ${duration.toFixed(2)} 秒`);
      console.log(`[诊断] 文件路径: ${data.filePath}`);
      console.log("[诊断] ═════════════════════════════════════");
    },
    onError: (error) => {
      stats.states.push("error");
      stats.endTime = Date.now();
      console.error("[诊断] 错误:", error.message);
    }
  });

  return cleanup;
}

/**
 * 完整流程示例（在 React 组件中使用）
 */
export function MeetingMinutesStreamExample() {
  const [meetingId, setMeetingId] = React.useState("meeting_test");
  const [generatedContent, setGeneratedContent] = React.useState("");
  const [status, setStatus] = React.useState<
    "idle" | "streaming" | "processing" | "complete" | "error"
  >("idle");
  const [error, setError] = React.useState<string | null>(null);
  const cleanupRef = React.useRef<(() => void) | null>(null);

  const handleStartStream = () => {
    setStatus("streaming");
    setGeneratedContent("");
    setError(null);

    cleanupRef.current = streamMeetingMinutesImproved(meetingId, {
      onStreaming: (chunk, fullContent) => {
        // 实时更新显示
        setGeneratedContent(fullContent);
      },
      onProcessing: (message) => {
        setStatus("processing");
      },
      onComplete: (data) => {
        setStatus("complete");
        // 此时可以安全地下载文件
      },
      onError: (err) => {
        setStatus("error");
        setError(err.message);
      }
    });
  };

  const handleStopStream = () => {
    if (cleanupRef.current) {
      cleanupRef.current();
    }
  };

  const handleDownload = async (format: "markdown" | "json" | "pdf" | "docx") => {
    try {
      await downloadGeneratedMinutes(meetingId, format);
    } catch (err) {
      setError(`下载失败: ${err}`);
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>会议纪要流式生成测试</h2>
      
      <div>
        <input
          type="text"
          value={meetingId}
          onChange={(e) => setMeetingId(e.target.value)}
          placeholder="输入 Meeting ID"
        />
        <button onClick={handleStartStream} disabled={status === "streaming" || status === "processing"}>
          开始流式生成
        </button>
        <button onClick={handleStopStream}>停止</button>
      </div>

      <div>
        <p>状态: {status}</p>
        {error && <p style={{ color: "red" }}>错误: {error}</p>}
      </div>

      <div>
        <h3>生成的内容：</h3>
        <textarea
          value={generatedContent}
          readOnly
          style={{
            width: "100%",
            height: "300px",
            fontFamily: "monospace"
          }}
        />
      </div>

      {status === "complete" && (
        <div>
          <h3>下载选项：</h3>
          <button onClick={() => handleDownload("markdown")}>
            下载 Markdown
          </button>
          <button onClick={() => handleDownload("json")}>
            下载 JSON
          </button>
          <button onClick={() => handleDownload("pdf")}>
            下载 PDF
          </button>
          <button onClick={() => handleDownload("docx")}>
            下载 Word
          </button>
        </div>
      )}
    </div>
  );
}
