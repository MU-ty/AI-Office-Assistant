import { useEffect, useMemo, useRef, useState } from "react";
import {
  createMeeting,
  uploadMeetingAudio,
  fetchTaskStatus,
  fetchMeetingMinutes,
} from "../api";
import { pollTaskStatusForMinutes } from "../api/streaming";
import {
  minutesToMessages,
  ChatMessage,
} from "@/modules/meeting/utils/minutesToMessages";

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

      // 使用流式轮询替代标准轮询
      if (stopPollingRef.current) {
        stopPollingRef.current();
      }

      stopPollingRef.current = await pollTaskStatusForMinutes(
        newTaskId,
        (minutesData) => {
          setMinutes(minutesData);
        },
        (summaryData) => {
          setSummary(summaryData);
        },
        (step) => {
          // 实时更新进度条
          setCurrentStep(step);
        },
        () => {
          // 完成回调 - 保持 isStarted=true 让用户看到最终结果
          setCurrentStep(4);
          setGeneratedAt(new Date().toISOString());
        },
        (error) => {
          console.error("流式轮询错误:", error);
          setIsStarted(false);
        },
        1000, // 1 秒轮询一次
      );
    } catch (error) {
      console.error("启动失败:", error);
      setIsStarted(false);
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
