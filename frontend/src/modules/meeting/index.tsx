"use client";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { FileAudio, Loader2, Wand2, Send } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { useSearchParams } from "next/navigation";
import { useMeeting } from "./hooks/useMeeting";
import { MeetingStepper } from "./components/Stepper";
import { UploadButton } from "./components/Uploader";

export default function MeetingModule() {
  const searchParams = useSearchParams();
  const meetingIdFromUrl = searchParams.get("meetingId") || undefined;
  const {
    steps,
    content,
    startWorkflow,
    isStarted,
    currentStep,
    minutes,
    summary,
    messages,
  } = useMeeting(meetingIdFromUrl);

  return (
    <div className="flex-1 flex gap-0 overflow-hidden w-full h-full border border-slate-200 rounded-lg shadow-lg">
      {/* 左侧边栏 - 工作流区域 */}
      <div className="w-80 bg-slate-50 border-r border-slate-200 flex flex-col shrink-0">
        {/* 侧边栏头部 */}
        <div className="p-6 border-b border-slate-200 bg-white">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-blue-600 rounded-lg">
              <Wand2 className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="font-bold text-slate-800">AI 会议助手</h2>
              <p className="text-xs text-slate-500">工作流执行面板</p>
            </div>
          </div>

          {/* 条件渲染：只在处理完成后显示上传按钮 */}
          {isStarted && currentStep === 4 && (
            <div className="mt-4">
              <UploadButton
                onFileSelect={(file) => startWorkflow(file)}
                isStarted={false} // 完成状态下按钮不禁用
              />
            </div>
          )}
        </div>

        {/* 工作流步骤 */}
        <div className="flex-1 p-6 overflow-y-auto">
          <div className="mb-4">
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">
              执行步骤
            </h3>
            <MeetingStepper steps={steps} currentStep={currentStep} />
          </div>

          {/* 状态信息 */}
          <div className="mt-6 p-4 bg-white rounded-lg border border-slate-200">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-slate-700">状态</span>
              <Badge
                variant={currentStep === 4 ? "default" : "secondary"}
                className="text-xs"
              >
                {!isStarted && "等待开始"}
                {isStarted && currentStep < 4 && "处理中"}
                {currentStep === 4 && "已完成"}
              </Badge>
            </div>
            {isStarted && (
              <div className="mt-3 pt-3 border-t border-slate-100">
                <div className="text-xs text-slate-600">
                  <div className="flex justify-between mb-1">
                    <span>进度</span>
                    <span className="font-medium">{currentStep}/4</span>
                  </div>
                  <div className="w-full bg-slate-200 rounded-full h-1.5 mt-2">
                    <div
                      className="bg-blue-600 h-1.5 rounded-full transition-all duration-500"
                      style={{ width: `${(currentStep / 4) * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 右侧聊天区域 */}
      <div className="flex-1 flex flex-col bg-white">
        {/* 聊天区头部 */}
        <div className="h-16 border-b border-slate-200 flex items-center justify-between px-6">
          <div>
            <h1 className="font-semibold text-slate-800">会议纪要生成</h1>
            <p className="text-xs text-slate-500">
              上传音频文件，AI 自动生成会议纪要
            </p>
          </div>
          {isStarted && currentStep === 4 && (
            <Button variant="outline" size="sm">
              导出纪要
            </Button>
          )}
        </div>

        {/* 聊天消息区域 */}
        <ScrollArea className="flex-1 p-6">
          <div className="max-w-6xl mx-auto space-y-4">
            {!isStarted ? (
              /* 初始状态 - 上传提示 */
              <div className="flex flex-col items-center justify-center py-20">
                <div className="w-full max-w-md">
                  <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
                      <FileAudio className="w-8 h-8 text-blue-600" />
                    </div>
                    <h3 className="text-lg font-semibold text-slate-800 mb-2">
                      开始你的会议分析
                    </h3>
                    <p className="text-sm text-slate-500">
                      上传会议音频，AI 将自动进行转录、分析并生成结构化纪要
                    </p>
                  </div>
                  <UploadButton
                    onFileSelect={(file) => startWorkflow(file)}
                    isStarted={isStarted}
                  />
                </div>
              </div>
            ) : (
              /* 消息流 */
              <>
                {/* 用户消息 */}
                <div className="flex justify-end">
                  <div className="max-w-[85%] bg-blue-600 text-white rounded-2xl rounded-tr-sm px-4 py-3">
                    <p className="text-sm">上传了会议音频文件并开始分析</p>
                  </div>
                </div>

                {/* AI 响应（聊天气泡呈现） */}
                {currentStep < 4 && messages.length === 0 ? (
                  <div className="flex justify-start">
                    <div className="max-w-[95%] bg-slate-100 rounded-2xl rounded-tl-sm px-4 py-3 flex items-center gap-2 text-slate-600">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span className="text-sm">正在分析会议内容...</span>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {messages.map((msg, idx) => {
                      const label = msg.section || msg.label || "会议纪要";
                      return (
                        <div className="flex justify-start" key={msg.id}>
                          <div className="max-w-[95%]">
                            {idx === 0 && (
                              <div className="flex items-center gap-2 mb-2">
                                <div className="w-7 h-7 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center">
                                  <Wand2 className="w-4 h-4 text-white" />
                                </div>
                                <span className="text-xs font-medium text-slate-600">
                                  AI 助手
                                </span>
                              </div>
                            )}

                            <div className="bg-slate-100 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
                              <div className="text-[11px] font-semibold text-slate-500 mb-1">
                                {label}
                              </div>
                              <div className="prose prose-slate max-w-none text-sm">
                                <ReactMarkdown>{msg.content}</ReactMarkdown>
                              </div>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </>
            )}
          </div>
        </ScrollArea>

        {/* 底部输入区 */}
        {currentStep === 4 && minutes && (
          <div className="h-auto border-t border-slate-200 bg-slate-50 p-4 flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                const element = document.createElement("a");
                element.setAttribute(
                  "href",
                  "data:text/markdown;charset=utf-8," +
                    encodeURIComponent(minutes),
                );
                element.setAttribute("download", "meeting_minutes.md");
                element.style.display = "none";
                document.body.appendChild(element);
                element.click();
                document.body.removeChild(element);
              }}
            >
              ↓ 下载 Markdown
            </Button>
            <Button variant="outline" size="sm">
              分享纪要
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
