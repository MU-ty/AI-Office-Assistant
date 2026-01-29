"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { FileAudio, Loader2, Wand2, Send, FileText, FileCode, FileType } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { useSearchParams } from "next/navigation";
import { useMeeting } from "./hooks/useMeeting";
import { MeetingStepper } from "./components/Stepper";
import { UploadButton } from "./components/Uploader";
import { MarkdownViewer } from "./components/MarkdownViewer";
// 导入我们刚才在 api.ts 中定义的接口
import { exportMeetingMinutes } from "./api";

export default function MeetingModule() {
  const searchParams = useSearchParams();
  const meetingIdFromUrl = searchParams.get("meetingId") || undefined;
  
  // 用于下载按钮的 Loading 状态
  const [downloadingFormat, setDownloadingFormat] = useState<string | null>(null);

  const {
    steps,
    content,
    startWorkflow,
    isStarted,
    currentStep,
    minutes,
    summary,
    messages,
    meetingId,
    meetingTitle,
    generatedAt,
  } = useMeeting(meetingIdFromUrl);

  /**
   * 核心下载逻辑
   * 处理 Markdown 内容生成与 PDF/Word 文件链接跳转
   */
  const handleDownload = async (format: 'markdown' | 'pdf' | 'docx') => {
    if (!meetingId) {
      alert("错误：未获取到有效的会议 ID");
      return;
    }

    setDownloadingFormat(format);
    try {
      const data = await exportMeetingMinutes(meetingId, format);
      const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
      
      let downloadUrl = "";
      
      if (format === 'markdown') {
        // 后端返回的是 { content: "..." }
        const blob = new Blob([data.content], { type: 'text/markdown' });
        downloadUrl = URL.createObjectURL(blob);
      } else {
        // 后端返回的是 { file_path: "/uploads/..." }
        // 必须拼接 API 基地址才能访问静态资源
        downloadUrl = data.file_path.startsWith('http') 
          ? data.file_path 
          : `${API_BASE}${data.file_path}`;
      }

      // 创建虚拟链接并触发下载
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.download = data.filename || `meeting_minutes_${meetingId}.${format}`;
      document.body.appendChild(link);
      link.click();
      
      // 清理
      document.body.removeChild(link);
      if (format === 'markdown') URL.revokeObjectURL(downloadUrl);
      
    } catch (error) {
      console.error("下载执行失败:", error);
      alert("下载失败，请检查后端服务是否正常运行，或依赖包是否安装。");
    } finally {
      setDownloadingFormat(null);
    }
  };

  return (
    <div className="flex-1 flex gap-0 overflow-hidden w-full h-full border border-slate-200 rounded-lg shadow-lg">
      {/* 左侧边栏 - 工作流区域 */}
      <div className="w-80 bg-slate-50 border-r border-slate-200 flex flex-col shrink-0">
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

          {isStarted && currentStep === 4 && (
            <div className="mt-4">
              <UploadButton
                onFileSelect={(file) => startWorkflow(file)}
                isStarted={false}
              />
            </div>
          )}
        </div>

        <div className="flex-1 p-6 overflow-y-auto">
          <div className="mb-4">
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">
              执行步骤
            </h3>
            <MeetingStepper steps={steps} currentStep={currentStep} />
          </div>

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
        <div className="h-16 border-b border-slate-200 flex items-center justify-between px-6">
          <div>
            <h1 className="font-semibold text-slate-800">会议纪要生成</h1>
            <p className="text-xs text-slate-500">
              上传音频文件，AI 自动生成会议纪要
            </p>
          </div>
          <div className="flex gap-2">
            {currentStep === 4 && minutes && (
              <MarkdownViewer
                content={minutes}
                title={meetingTitle || "会议纪要"}
                meetingId={meetingId}
                generatedAt={generatedAt}
              />
            )}
          </div>
        </div>

        <ScrollArea className="flex-1 p-6">
          <div className="max-w-6xl mx-auto space-y-4">
            {!isStarted && !minutes && !summary && !content ? (
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
              <>
                <div className="flex justify-end">
                  <div className="max-w-[85%] bg-blue-600 text-white rounded-2xl rounded-tr-sm px-4 py-3">
                    <p className="text-sm">上传了会议音频文件并开始分析</p>
                  </div>
                </div>

                <div className="space-y-3">
                  {content && (
                    <div className="flex justify-start">
                      <div className="max-w-[95%]">
                        <div className="flex items-center gap-2 mb-2">
                          <div className="w-7 h-7 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center">
                            <Wand2 className="w-4 h-4 text-white" />
                          </div>
                          <span className="text-xs font-medium text-slate-600">
                            AI 助手
                          </span>
                        </div>
                        <div className="bg-slate-100 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
                          <div className="text-[11px] font-semibold text-slate-500 mb-1">
                            处理进度
                          </div>
                          <div className="prose prose-slate max-w-none text-sm text-slate-700">
                            {content}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {summary && (
                    <div className="flex justify-start">
                      <div className="max-w-[95%]">
                        <div className="bg-slate-100 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
                          <div className="text-[11px] font-semibold text-slate-500 mb-1">
                            执行摘要
                          </div>
                          <div className="prose prose-slate max-w-none text-sm">
                            <ReactMarkdown>{summary}</ReactMarkdown>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {minutes && (
                    <div className="flex justify-start">
                      <div className="max-w-[95%]">
                        <div className="bg-blue-50 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm border border-blue-200">
                          <div className="text-[11px] font-semibold text-blue-600 mb-2 flex items-center gap-1">
                            📝 实时纪要
                            {isStarted && currentStep < 4 && (
                              <span className="inline-flex">
                                <span className="animate-pulse text-xs">•</span>
                                <span className="animate-pulse text-xs" style={{ animationDelay: "0.2s" }}>•</span>
                                <span className="animate-pulse text-xs" style={{ animationDelay: "0.4s" }}>•</span>
                              </span>
                            )}
                          </div>
                          <div className="prose prose-slate max-w-none text-sm max-h-64 overflow-y-auto">
                            <ReactMarkdown>{minutes}</ReactMarkdown>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {!content && !summary && !minutes && (
                    <div className="flex justify-start">
                      <div className="max-w-[95%] bg-slate-100 rounded-2xl rounded-tl-sm px-4 py-3 flex items-center gap-2 text-slate-600">
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span className="text-sm">正在分析会议内容...</span>
                      </div>
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        </ScrollArea>

        {/* 底部功能区 - 接入后端下载功能 */}
        {currentStep === 4 && minutes && (
          <div className="h-auto border-t border-slate-200 bg-slate-50 p-4 flex items-center gap-3">
            <span className="text-xs font-semibold text-slate-400 uppercase ml-2">导出纪要:</span>
            
            <Button
              variant="outline"
              size="sm"
              disabled={!!downloadingFormat}
              onClick={() => handleDownload('markdown')}
              className="gap-2"
            >
              <FileCode className="w-4 h-4" />
              Markdown
            </Button>

            <Button
              variant="outline"
              size="sm"
              disabled={!!downloadingFormat}
              onClick={() => handleDownload('pdf')}
              className="gap-2 border-red-200 text-red-600 hover:bg-red-50 hover:text-red-700"
            >
              {downloadingFormat === 'pdf' ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileText className="w-4 h-4" />}
              PDF 格式
            </Button>

            <Button
              variant="outline"
              size="sm"
              disabled={!!downloadingFormat}
              onClick={() => handleDownload('docx')}
              className="gap-2 border-blue-200 text-blue-600 hover:bg-blue-50 hover:text-blue-700"
            >
              {downloadingFormat === 'docx' ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileType className="w-4 h-4" />}
              Word 格式
            </Button>

            <Button variant="ghost" size="sm" className="ml-auto text-slate-400">
              分享纪要
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}