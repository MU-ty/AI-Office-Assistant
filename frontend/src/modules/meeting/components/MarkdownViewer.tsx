"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Download, FileText, Copy, Check } from "lucide-react";
import ReactMarkdown from "react-markdown";

interface MarkdownViewerProps {
  /** Markdown 内容 */
  content: string;
  /** 会议标题 */
  title?: string;
  /** 会议 ID（用于文件名） */
  meetingId?: string;
  /** 生成时间 */
  generatedAt?: string;
}

export function MarkdownViewer({
  content,
  title = "会议纪要",
  meetingId,
  generatedAt,
}: MarkdownViewerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  // 下载 Markdown 文件
  const handleDownload = () => {
    const fileName = meetingId
      ? `meeting_${meetingId}_minutes.md`
      : "meeting_minutes.md";

    const element = document.createElement("a");
    element.setAttribute(
      "href",
      "data:text/markdown;charset=utf-8," + encodeURIComponent(content),
    );
    element.setAttribute("download", fileName);
    element.style.display = "none";
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  // 复制到剪贴板
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("复制失败:", err);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm" className="gap-2">
          <FileText className="w-4 h-4" />
          查看完整纪要
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-4xl max-h-[90vh] flex flex-col p-0">
        {/* 头部 */}
        <DialogHeader className="px-6 pt-6 pb-4 border-b">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <DialogTitle className="text-xl font-bold">{title}</DialogTitle>
              <DialogDescription className="flex items-center gap-2 mt-2">
                {generatedAt && (
                  <span className="text-xs text-slate-500">
                    生成时间: {new Date(generatedAt).toLocaleString("zh-CN")}
                  </span>
                )}
                {meetingId && (
                  <Badge variant="secondary" className="text-xs">
                    ID: {meetingId}
                  </Badge>
                )}
              </DialogDescription>
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleCopy}
                className="gap-2"
              >
                {copied ? (
                  <>
                    <Check className="w-4 h-4" />
                    已复制
                  </>
                ) : (
                  <>
                    <Copy className="w-4 h-4" />
                    复制
                  </>
                )}
              </Button>
              <Button
                variant="default"
                size="sm"
                onClick={handleDownload}
                className="gap-2"
              >
                <Download className="w-4 h-4" />
                下载
              </Button>
            </div>
          </div>
        </DialogHeader>

        {/* Markdown 内容区域 */}
        <ScrollArea className="flex-1 px-6 py-4">
          <article className="prose prose-slate prose-sm max-w-none">
            <ReactMarkdown
              components={{
                // 自定义样式
                h1: ({ node, ...props }) => (
                  <h1 className="text-2xl font-bold mt-6 mb-4" {...props} />
                ),
                h2: ({ node, ...props }) => (
                  <h2 className="text-xl font-semibold mt-5 mb-3" {...props} />
                ),
                h3: ({ node, ...props }) => (
                  <h3 className="text-lg font-semibold mt-4 mb-2" {...props} />
                ),
                p: ({ node, ...props }) => (
                  <p className="my-3 leading-7" {...props} />
                ),
                ul: ({ node, ...props }) => (
                  <ul className="my-3 ml-6 list-disc" {...props} />
                ),
                ol: ({ node, ...props }) => (
                  <ol className="my-3 ml-6 list-decimal" {...props} />
                ),
                li: ({ node, ...props }) => <li className="my-1" {...props} />,
                blockquote: ({ node, ...props }) => (
                  <blockquote
                    className="border-l-4 border-blue-500 pl-4 italic my-4 text-slate-600"
                    {...props}
                  />
                ),
                code: ({ node, className, children, ...props }) => {
                  const match = /language-(\w+)/.exec(className || "");
                  return match ? (
                    <code
                      className={`block bg-slate-900 text-slate-100 p-4 rounded-lg overflow-x-auto ${className}`}
                      {...props}
                    >
                      {children}
                    </code>
                  ) : (
                    <code
                      className="bg-slate-100 text-slate-800 px-1.5 py-0.5 rounded text-sm"
                      {...props}
                    >
                      {children}
                    </code>
                  );
                },
                table: ({ node, ...props }) => (
                  <div className="overflow-x-auto my-4">
                    <table
                      className="min-w-full border-collapse border border-slate-300"
                      {...props}
                    />
                  </div>
                ),
                th: ({ node, ...props }) => (
                  <th
                    className="border border-slate-300 bg-slate-100 px-4 py-2 text-left font-semibold"
                    {...props}
                  />
                ),
                td: ({ node, ...props }) => (
                  <td
                    className="border border-slate-300 px-4 py-2"
                    {...props}
                  />
                ),
              }}
            >
              {content}
            </ReactMarkdown>
          </article>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
}
