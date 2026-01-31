import { useEffect, useMemo, useRef, useState } from "react";
import {
  createMeeting,
  uploadMeetingAudio,
  fetchTaskStatus,
  fetchMeetingMinutes,
} from "../api";
import { pollTaskStatusForMinutes } from "../api/streaming";
import { diagnosticPoll } from "../api/diagnostic";
import { streamMeetingMinutesImproved } from "../api/streaming_improved";
import {
  minutesToMessages,
  ChatMessage,
} from "@/modules/meeting/utils/minutesToMessages";
import {
  convertMinutesJSONToMarkdown,
  generateSummary,
  MeetingMinutesJSON,
} from "@/modules/meeting/utils/minutesConverter";

export interface TaskStatus {
  task_id: string;
  meeting_id: string;
  step: number;
  is_completed: boolean;
  content: string;
  status: string;
  summary?: string;
  minutes?: string;
}

export interface MeetingMinutesRecord {
  meeting_id: string;
  title?: string;
  summary?: string;
  minutes?: string;
  content?: string;
  generated_at?: string;
  formats?: Record<string, unknown>;
}

export interface MeetingData {
  id: string;
  title: string;
  meeting_type?: string;
  start_time?: string;
  location?: string;
  created_at?: string;
}

type UiMessage = ChatMessage & { label?: string };

export function useMeeting(initialMeetingId?: string) {
  const [currentStep, setCurrentStep] = useState(0);
  const [content, setContent] = useState("");
  const [minutes, setMinutes] = useState(""); // 完整纪要
  const [summary, setSummary] = useState(""); // 执行摘要
  const [isStarted, setIsStarted] = useState(false);
  const [meetingId, setMeetingId] = useState(initialMeetingId || "");
  const [meetingTitle, setMeetingTitle] = useState(""); // 新增：会议标题
  const [generatedAt, setGeneratedAt] = useState<string>(""); // 新增：生成时间
  const [taskId, setTaskId] = useState<string>("");
  const hasLoadedInitialRef = useRef(false);
  const pollTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const stopPollingRef = useRef<(() => void) | null>(null);
  const stopSseRef = useRef<(() => void) | null>(null);
  const sseStartedRef = useRef(false);

  // 1. 先声明状态获取函数
  function getStatus(index: number) {
    if (currentStep > index) return "completed" as const;
    if (currentStep === index && isStarted) return "loading" as const;
    return "waiting" as const;
  }

  // 2. 再声明依赖该函数的 steps 数组
  // 这样每次组件重新渲染时，steps 都会根据最新的 currentStep 重新生成
  const steps = [
    { id: "1", label: "音视频切片转录 ", status: getStatus(0) },
    { id: "2", label: "语义角色标注", status: getStatus(1) },
    { id: "3", label: "核心议程提取", status: getStatus(2) },
    { id: "4", label: "生成纪要文档", status: getStatus(3) },
  ];

  const startWorkflow = async (file: File) => {
    setIsStarted(true);
    setCurrentStep(0);
    setContent("");
    setMinutes("");
    setSummary("");
    setMeetingId("");
    setMeetingTitle(""); // 重置标题
    setGeneratedAt(""); // 重置生成时间

    try {
      const meetingPayload = {
        title: file.name,
        meeting_type: "audio",
        start_time: new Date().toISOString(),
      };

      const meeting = await createMeeting(meetingPayload);
      const meetingId = meeting.id || meeting.meeting_id;
      if (!meetingId) {
        throw new Error("未获取到会议ID");
      }

      setMeetingId(meetingId);
      setMeetingTitle(meeting.title || file.name); // 保存会议标题

      const uploadResp = await uploadMeetingAudio(meetingId, file);
      const newTaskId = uploadResp.task_id || uploadResp.transcription_task_id;
      if (!newTaskId) {
        throw new Error("未获取到任务ID");
      }

      setTaskId(newTaskId);

      console.log("🚀 开始轮询任务:", newTaskId);

      // 使用诊断轮询（临时）
      if (stopPollingRef.current) {
        stopPollingRef.current();
      }

      if (stopSseRef.current) {
        stopSseRef.current();
        stopSseRef.current = null;
      }
      sseStartedRef.current = false;

      stopPollingRef.current = await diagnosticPoll(
        newTaskId,
        (status) => {
          // 更新所有字段
          if (status.step !== undefined) {
            setCurrentStep(Math.min(status.step, 4));
          }
          if (status.content) {
            setContent(status.content);
          }
          if (status.summary) {
            setSummary(status.summary);
          }
          if (status.minutes) {
            setMinutes(status.minutes);
          }

          // 当进入“生成纪要文档”(step=3)阶段时，启动 SSE 逐字输出
          if (
            status.step === 3 &&
            !sseStartedRef.current &&
            meetingId
          ) {
            sseStartedRef.current = true;
            console.log("🟦 启动 SSE 逐字输出...", meetingId);

            stopSseRef.current = streamMeetingMinutesImproved(meetingId, {
              onStreaming: (_chunk, fullContent) => {
                // 后端会同时带 chunk 与累积 content，这里用累积内容直接渲染
                setMinutes(fullContent);
              },
              onProcessing: (message) => {
                setContent(message);
              },
              onComplete: () => {
                console.log("✅ SSE 输出完成");
                if (stopSseRef.current) {
                  stopSseRef.current();
                  stopSseRef.current = null;
                }
              },
              onError: (err) => {
                console.error("❌ SSE 输出失败:", err);
                if (stopSseRef.current) {
                  stopSseRef.current();
                  stopSseRef.current = null;
                }
              },
            });
          }
        },
        async () => {
          // 任务完成后，调用纪要接口获取完整数据
          console.log("✅ 诊断轮询完成，开始获取完整纪要");
          setCurrentStep(4);

          if (stopSseRef.current) {
            stopSseRef.current();
            stopSseRef.current = null;
          }

          try {
            const minutesData = await fetchMeetingMinutes(meetingId);
            console.log("📄 收到完整纪要数据:", minutesData);

            // 检查数据格式并转换
            if (minutesData.paragraphs || minutesData.sentences) {
              // JSON 格式，需要转换为 Markdown
              console.log("🔄 检测到 JSON 格式，转换为 Markdown");
              const markdown = convertMinutesJSONToMarkdown(
                minutesData as MeetingMinutesJSON,
              );
              const summary = generateSummary(
                minutesData as MeetingMinutesJSON,
              );

              setMinutes(markdown);
              setSummary(summary);
            } else if (minutesData.minutes) {
              // 已经是 Markdown 格式
              console.log("📝 检测到 Markdown 格式");
              setMinutes(minutesData.minutes);
              if (minutesData.summary) {
                setSummary(minutesData.summary);
              }
            }

            if (minutesData.content) {
              setContent(minutesData.content);
            }
            if (minutesData.generated_at) {
              setGeneratedAt(minutesData.generated_at);
            } else {
              setGeneratedAt(new Date().toISOString());
            }
          } catch (error) {
            console.error("❌ 获取完整纪要失败:", error);
          }
        },
        (error) => {
          console.error("❌ 诊断轮询错误:", error);
          setIsStarted(false);

          if (stopSseRef.current) {
            stopSseRef.current();
            stopSseRef.current = null;
          }
        },
        1000, // 1 秒轮询一次
      );
    } catch (error) {
      console.error("启动失败:", error);
      setIsStarted(false);

      if (stopSseRef.current) {
        stopSseRef.current();
        stopSseRef.current = null;
      }
    }
  };

  const loadExistingMinutes = async (targetMeetingId: string) => {
    if (!targetMeetingId) return;
    try {
      setIsStarted(true);
      setContent("正在加载会议纪要...");
      const data: MeetingMinutesRecord =
        await fetchMeetingMinutes(targetMeetingId);

      setMeetingId(targetMeetingId);
      if (data.title) setMeetingTitle(data.title);
      if (data.content) setContent(data.content);
      if (data.summary) setSummary(data.summary);
      if (data.minutes) setMinutes(data.minutes);
      if (data.generated_at) setGeneratedAt(data.generated_at);
      setCurrentStep(4);
    } catch (error) {
      console.error("加载会议纪要失败:", error);
    } finally {
      setIsStarted(false);
    }
  };

  // 汇总为聊天消息列表
  const messages = useMemo<UiMessage[]>(() => {
    const list: UiMessage[] = [];

    if (content) {
      list.push({ id: "progress", role: "assistant", content, label: "进度" });
    }

    if (summary) {
      list.push({
        id: "summary",
        role: "assistant",
        content: summary,
        label: "执行摘要",
      });
    }

    if (minutes) {
      list.push(...minutesToMessages(minutes));
    }

    return list;
  }, [content, summary, minutes]);

  useEffect(() => {
    if (initialMeetingId && !hasLoadedInitialRef.current) {
      hasLoadedInitialRef.current = true;
      loadExistingMinutes(initialMeetingId);
    }

    return () => {
      if (pollTimerRef.current) {
        clearInterval(pollTimerRef.current);
      }
      if (stopPollingRef.current) {
        stopPollingRef.current();
      }
    };
  }, []);

  return {
    steps,
    content,
    startWorkflow,
    isStarted,
    currentStep,
    minutes,
    summary,
    taskId,
    meetingId,
    meetingTitle,
    generatedAt,
    loadExistingMinutes,
    messages,
  };
}
