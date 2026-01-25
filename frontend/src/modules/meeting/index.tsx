"use client";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { FileAudio, Loader2, Wand2 } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { useMeeting } from "./hooks/useMeeting";
import { MeetingStepper } from "./components/Stepper";

export default function MeetingModule() {
  const { steps, content, startWorkflow, isStarted, currentStep } =
    useMeeting();

  return (
    <Card className="flex-1 flex flex-col max-w-6xl mx-auto overflow-hidden shadow-xl border-none m-6">
      {/* Header */}
      <div className="p-6 border-b bg-white flex justify-between items-center">
        <div>
          <h1 className="text-xl font-bold flex items-center gap-2">
            <Wand2 className="w-5 h-5 text-blue-600" />
            AI 会议助手 Agent
          </h1>
        </div>
        <Badge variant={currentStep === 4 ? "default" : "secondary"}>
          {!isStarted && "等待开始"}
          {isStarted &&
            currentStep < 4 &&
            `步骤 ${currentStep + 1}/4 进行中...`}
          {currentStep === 4 && "生成完毕"}
        </Badge>
      </div>

      {/* Content Area - 修改为左右布局显示步骤和内容 */}
      <div className="flex-1 p-6 overflow-hidden flex gap-6">
        {/* 左侧：工作流进度 */}
        {isStarted && (
          <MeetingStepper steps={steps} currentStep={currentStep} />
        )}

        {/* 右侧：主展示区 */}
        <div
          className={`flex-1 flex flex-col ${isStarted ? "border rounded-xl bg-white p-6 shadow-inner" : ""}`}
        >
          {!isStarted ? (
            <div className="h-full border-2 border-dashed rounded-xl flex flex-col items-center justify-center">
              <FileAudio className="w-12 h-12 text-slate-400 mb-4" />
              <Button onClick={startWorkflow}>上传会议音频并开始分析</Button>
            </div>
          ) : (
            <ScrollArea className="flex-1">
              <div className="prose prose-slate max-w-none pr-4">
                {currentStep < 4 && !content ? (
                  <div className="flex items-center gap-3 text-slate-500 italic">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Agent 正在执行工作流子模块...
                  </div>
                ) : (
                  <ReactMarkdown>{content}</ReactMarkdown>
                )}
              </div>
            </ScrollArea>
          )}
        </div>
      </div>
    </Card>
  );
}
