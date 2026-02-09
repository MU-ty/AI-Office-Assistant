"use client";

import { useEffect, useMemo, useState } from "react";
import ReactMarkdown from "react-markdown";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import KnowledgeBaseSelector from "@/components/knowledge/KnowledgeBaseSelector";
import {
  getDocument,
  listDocuments,
  summarizeDocument,
  uploadDocumentFile,
  uploadDocumentText,
  uploadDocumentUrl
} from "./api";
import type { DocumentItem, DocumentSummary } from "./types";

const summaryOptions = [
  { value: "one_liner", label: "一句话" },
  { value: "paragraph", label: "段落" },
  { value: "full", label: "完整" }
] as const;

type UploadMode = "file" | "text" | "url";

export default function DocumentsModule() {
  const [mode, setMode] = useState<UploadMode>("file");
  const [title, setTitle] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [content, setContent] = useState("");
  const [url, setUrl] = useState("");
  const [summaryLevel, setSummaryLevel] = useState<"one_liner" | "paragraph" | "full">("paragraph");
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<DocumentItem | null>(null);
  const [summary, setSummary] = useState<DocumentSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [knowledgeBaseIds, setKnowledgeBaseIds] = useState<string[]>([]);

  const loadDocuments = async () => {
    try {
      const data = await listDocuments();
      setDocuments(data || []);
      if (data?.length && !selectedDoc) {
        await handleSelectDoc(data[0].id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "获取文档失败");
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  const handleSelectDoc = async (docId: number) => {
    try {
      const data = await getDocument(docId);
      setSelectedDoc(data);
      setSummary(data.latest_summary || null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "获取详情失败");
    }
  };

  const handleUpload = async () => {
    setError(null);
    setLoading(true);
    try {
      let doc: DocumentItem | null = null;
      if (mode === "file") {
        if (!file) throw new Error("请选择文件");
        doc = await uploadDocumentFile(title || file.name, file);
      }
      if (mode === "text") {
        if (!content.trim()) throw new Error("请输入文本内容");
        doc = await uploadDocumentText(title || "文本输入", content.trim());
      }
      if (mode === "url") {
        if (!url.trim()) throw new Error("请输入URL");
        doc = await uploadDocumentUrl(title || "网页导入", url.trim());
      }
      if (doc) {
        setSelectedDoc(doc);
        setSummary(null);
        await loadDocuments();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "上传失败");
    } finally {
      setLoading(false);
    }
  };

  const handleSummarize = async () => {
    if (!selectedDoc) return;
    setError(null);
    setLoading(true);
    try {
      const data = await summarizeDocument(selectedDoc.id, summaryLevel);
      setSummary(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "生成失败");
    } finally {
      setLoading(false);
    }
  };

  const summaryTitle = useMemo(() => {
    const current = summaryOptions.find((item) => item.value === summaryLevel);
    return current?.label || "段落";
  }, [summaryLevel]);

  return (
    <div className="flex h-full w-full gap-0 overflow-hidden rounded-lg border border-slate-200 bg-white shadow-lg">
      <div className="w-80 shrink-0 border-r border-slate-200 bg-slate-50">
        <div className="border-b border-slate-200 bg-white p-6">
          <h2 className="text-lg font-semibold text-slate-800">文献摘要</h2>
          <p className="mt-1 text-xs text-slate-500">上传文献并快速整理要点</p>
        </div>
        <div className="p-6 space-y-4">
          <div className="flex gap-2">
            {([
              { value: "file", label: "PDF/文档" },
              { value: "text", label: "文本" },
              { value: "url", label: "网页" }
            ] as const).map((item) => (
              <button
                key={item.value}
                type="button"
                onClick={() => setMode(item.value)}
                className={`flex-1 rounded-md border px-2 py-2 text-xs ${
                  mode === item.value
                    ? "border-blue-500 bg-blue-50 text-blue-600"
                    : "border-slate-200 bg-white text-slate-600"
                }`}
              >
                {item.label}
              </button>
            ))}
          </div>
          <div className="space-y-2">
            <label className="text-xs text-slate-500">标题</label>
            <input
              className="w-full rounded-md border border-slate-200 px-2 py-2 text-sm"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="可选，默认为文件名"
            />
          </div>
          {mode === "file" && (
            <div className="space-y-2">
              <label className="text-xs text-slate-500">选择文件</label>
              <input
                type="file"
                accept=".pdf,.docx,.txt"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="w-full rounded-md border border-slate-200 px-2 py-2 text-xs"
              />
            </div>
          )}
          {mode === "text" && (
            <div className="space-y-2">
              <label className="text-xs text-slate-500">粘贴文本</label>
              <textarea
                className="h-28 w-full rounded-md border border-slate-200 px-2 py-2 text-xs"
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="粘贴需要摘要的文本内容"
              />
            </div>
          )}
          {mode === "url" && (
            <div className="space-y-2">
              <label className="text-xs text-slate-500">网页URL</label>
              <input
                className="w-full rounded-md border border-slate-200 px-2 py-2 text-xs"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://..."
              />
            </div>
          )}
          <KnowledgeBaseSelector
            value={knowledgeBaseIds}
            onChange={setKnowledgeBaseIds}
            title="引用知识库"
          />
          <Button onClick={handleUpload} disabled={loading} className="w-full">
            {loading ? "处理中..." : "创建文档"}
          </Button>
        </div>
        <div className="px-6 pb-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-slate-700">历史文档</h3>
            <Badge variant="secondary" className="text-xs">
              {documents.length} 条
            </Badge>
          </div>
          <ScrollArea className="h-[360px]">
            <div className="space-y-3">
              {documents.map((doc) => (
                <Card
                  key={doc.id}
                  className={`cursor-pointer p-3 text-xs ${
                    selectedDoc?.id === doc.id ? "border-blue-500" : ""
                  }`}
                  onClick={() => handleSelectDoc(doc.id)}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-slate-700">{doc.title}</span>
                    <Badge variant="secondary" className="text-[10px]">
                      {doc.source_type}
                    </Badge>
                  </div>
                  <div className="mt-2 text-[11px] text-slate-400">
                    {doc.created_at ? new Date(doc.created_at).toLocaleString() : ""}
                  </div>
                </Card>
              ))}
            </div>
          </ScrollArea>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        {error && (
          <div className="mb-4 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-600">
            {error}
          </div>
        )}

        <Card className="p-4 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-slate-700">摘要生成</h3>
              <p className="text-xs text-slate-500">选择摘要级别并生成</p>
            </div>
            {selectedDoc && (
              <Badge variant="secondary" className="text-xs">
                文档 #{selectedDoc.id}
              </Badge>
            )}
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <select
              className="rounded-md border border-slate-200 px-2 py-2 text-sm"
              value={summaryLevel}
              onChange={(e) => setSummaryLevel(e.target.value as "one_liner" | "paragraph" | "full")}
            >
              {summaryOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <Button onClick={handleSummarize} disabled={!selectedDoc || loading}>
              {loading ? "处理中..." : `生成${summaryTitle}摘要`}
            </Button>
          </div>
          <div className="space-y-2">
            <label className="text-xs text-slate-500">摘要内容</label>
            <div className="min-h-[260px] w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm">
              {summary?.summary_text ? (
                <div className="prose prose-slate max-w-none text-sm">
                  <ReactMarkdown>{summary.summary_text}</ReactMarkdown>
                </div>
              ) : (
                <div className="text-slate-400">摘要内容会显示在这里</div>
              )}
            </div>
          </div>
          {summary?.quality_score !== undefined && summary?.quality_score !== null && (
            <div className="text-xs text-slate-500">质量评分：{summary.quality_score}</div>
          )}
        </Card>
      </div>
    </div>
  );
}
