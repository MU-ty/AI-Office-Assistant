"use client";

import { useEffect, useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  addTerminology,
  createTranslationTask,
  exportTranslationTask,
  getTranslationTask,
  listTerminology,
  listTranslationTasks,
  rateTranslationTask
} from "./api";
import type { TranslationTask, TranslationTerminology } from "./types";

const targetOptions = [
  { value: "zh", label: "中文" },
  { value: "en", label: "英文" },
  { value: "ja", label: "日文" },
  { value: "ko", label: "韩文" },
  { value: "fr", label: "法文" },
  { value: "de", label: "德文" }
];

const domainOptions = [
  { value: "general", label: "通用" },
  { value: "academic", label: "学术" },
  { value: "tech", label: "技术" },
  { value: "business", label: "商务" }
];

export default function TranslationModule() {
  const [inputText, setInputText] = useState("");
  const [targetLang, setTargetLang] = useState("en");
  const [domain, setDomain] = useState("general");
  const [tasks, setTasks] = useState<TranslationTask[]>([]);
  const [selectedTask, setSelectedTask] = useState<TranslationTask | null>(null);
  const [terminology, setTerminology] = useState<TranslationTerminology[]>([]);
  const [termSource, setTermSource] = useState("");
  const [termTarget, setTermTarget] = useState("");
  const [termDomain, setTermDomain] = useState("general");
  const [feedback, setFeedback] = useState("");
  const [viewMode, setViewMode] = useState<"dual" | "compare">("dual");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadTasks = async () => {
    try {
      const data = await listTranslationTasks({ skip: 0, limit: 20 });
      setTasks(data.items || []);
      if (data.items?.length && !selectedTask) {
        await handleSelectTask(data.items[0].id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "获取任务失败");
    }
  };

  const loadTerminology = async () => {
    try {
      const data = await listTerminology(domain);
      setTerminology(data || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "获取术语失败");
    }
  };

  useEffect(() => {
    loadTasks();
    loadTerminology();
  }, []);

  useEffect(() => {
    loadTerminology();
  }, [domain]);

  const handleSelectTask = async (taskId: number) => {
    try {
      const data = await getTranslationTask(taskId);
      setSelectedTask(data);
      setInputText(data.input_text || "");
      setTargetLang(data.target_language || "en");
      setDomain(data.domain || "general");
      setFeedback(data.feedback || "");
    } catch (err) {
      setError(err instanceof Error ? err.message : "获取任务失败");
    }
  };

  const handleTranslate = async () => {
    if (!inputText.trim()) {
      setError("请输入需要翻译的文本");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const task = await createTranslationTask({
        target_language: targetLang,
        input_text: inputText.trim(),
        domain
      });
      setSelectedTask(task);
      await loadTasks();
    } catch (err) {
      setError(err instanceof Error ? err.message : "翻译失败");
    } finally {
      setLoading(false);
    }
  };

  const handleRate = async (score: number) => {
    if (!selectedTask) return;
    try {
      const data = await rateTranslationTask(selectedTask.id, score, feedback.trim() || undefined);
      setSelectedTask(data);
      await loadTasks();
    } catch (err) {
      setError(err instanceof Error ? err.message : "评分失败");
    }
  };

  const handleExport = async (format: "json" | "txt" | "pdf" | "docx") => {
    if (!selectedTask) return;
    try {
      const data = await exportTranslationTask(selectedTask.id, format);
      if (typeof data === "object" && data && "path" in data) {
        const path = (data as { path: string }).path;
        const link = document.createElement("a");
        link.href = `${process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8003"}${path}`;
        link.download = `translation-${selectedTask.id}.${format}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        return;
      }

      const content = typeof data === "string" ? data : JSON.stringify(data, null, 2);
      const mime = format === "txt" ? "text/plain" : "application/json";
      const blob = new Blob([content], { type: mime });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `translation-${selectedTask.id}.${format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : "导出失败");
    }
  };

  const handleAddTerm = async () => {
    if (!termSource.trim() || !termTarget.trim()) {
      setError("请输入术语及翻译");
      return;
    }
    try {
      await addTerminology({
        original_term: termSource.trim(),
        translation: termTarget.trim(),
        domain: termDomain
      });
      setTermSource("");
      setTermTarget("");
      await loadTerminology();
    } catch (err) {
      setError(err instanceof Error ? err.message : "添加术语失败");
    }
  };

  const taskStatus = useMemo(() => selectedTask?.status || "" , [selectedTask]);

  return (
    <div className="flex h-full w-full gap-0 overflow-hidden rounded-lg border border-slate-200 bg-white shadow-lg">
      <div className="w-80 shrink-0 border-r border-slate-200 bg-slate-50">
        <div className="border-b border-slate-200 bg-white p-6">
          <h2 className="text-lg font-semibold text-slate-800">多语言翻译</h2>
          <p className="mt-1 text-xs text-slate-500">保持术语一致，输出清晰译文</p>
        </div>
        <div className="p-6 space-y-4">
          <div className="space-y-2">
            <label className="text-xs text-slate-500">目标语言</label>
            <select
              className="w-full rounded-md border border-slate-200 px-2 py-2 text-sm"
              value={targetLang}
              onChange={(e) => setTargetLang(e.target.value)}
            >
              {targetOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          <div className="space-y-2">
            <label className="text-xs text-slate-500">领域</label>
            <select
              className="w-full rounded-md border border-slate-200 px-2 py-2 text-sm"
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
            >
              {domainOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          <Button onClick={handleTranslate} disabled={loading} className="w-full">
            {loading ? "翻译中..." : "开始翻译"}
          </Button>
        </div>
        <div className="px-6 pb-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-slate-700">历史记录</h3>
            <Badge variant="secondary" className="text-xs">
              {tasks.length} 条
            </Badge>
          </div>
          <ScrollArea className="h-[280px]">
            <div className="space-y-3">
              {tasks.map((task) => (
                <Card
                  key={task.id}
                  className={`cursor-pointer p-3 text-xs ${
                    selectedTask?.id === task.id ? "border-blue-500" : ""
                  }`}
                  onClick={() => handleSelectTask(task.id)}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-slate-700">任务 {task.id}</span>
                    <Badge variant="secondary" className="text-[10px]">
                      {task.status}
                    </Badge>
                  </div>
                  <div className="mt-2 text-[11px] text-slate-400">
                    {task.created_at ? new Date(task.created_at).toLocaleString() : ""}
                  </div>
                </Card>
              ))}
            </div>
          </ScrollArea>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {error && (
          <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-600">
            {error}
          </div>
        )}

        <div className="grid gap-4 lg:grid-cols-2">
          {viewMode === "dual" && (
            <>
              <Card className="p-4 space-y-3">
                <h3 className="text-sm font-semibold text-slate-700">原文</h3>
                <textarea
                  className="min-h-[280px] w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder="粘贴需要翻译的内容"
                />
              </Card>
              <Card className="p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-slate-700">译文</h3>
                  {selectedTask && (
                    <Badge variant="secondary" className="text-xs">
                      {taskStatus}
                    </Badge>
                  )}
                </div>
                <textarea
                  className="min-h-[280px] w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                  value={selectedTask?.translated_text || ""}
                  readOnly
                />
                {selectedTask?.quality_score !== undefined && selectedTask?.quality_score !== null && (
                  <div className="text-xs text-slate-500">
                    质量评分：{selectedTask.quality_score}
                  </div>
                )}
              </Card>
            </>
          )}
          {viewMode === "compare" && (
            <Card className="p-4 lg:col-span-2">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-slate-700">双语对照</h3>
                {selectedTask && (
                  <Badge variant="secondary" className="text-xs">
                    {taskStatus}
                  </Badge>
                )}
              </div>
              <div className="mt-3 grid grid-cols-2 gap-4 text-xs text-slate-700">
                <div className="font-medium text-slate-500">原文</div>
                <div className="font-medium text-slate-500">译文</div>
                {(inputText || "")
                  .split("\n")
                  .map((line, idx) => {
                    const targetLine = (selectedTask?.translated_text || "").split("\n")[idx] || "";
                    return (
                      <div key={`pair-${idx}`} className="contents">
                        <div className="whitespace-pre-wrap rounded-md border border-slate-100 bg-slate-50 p-2">
                          {line || " "}
                        </div>
                        <div className="whitespace-pre-wrap rounded-md border border-slate-100 bg-white p-2">
                          {targetLine || " "}
                        </div>
                      </div>
                    );
                  })}
              </div>
            </Card>
          )}
        </div>

        <Card className="p-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="text-sm font-semibold text-slate-700">展示方式</div>
            <div className="flex gap-2">
              <Button
                variant={viewMode === "dual" ? "default" : "secondary"}
                onClick={() => setViewMode("dual")}
              >
                上下对照
              </Button>
              <Button
                variant={viewMode === "compare" ? "default" : "secondary"}
                onClick={() => setViewMode("compare")}
              >
                双语对照
              </Button>
            </div>
            <div className="flex gap-2">
              <Button variant="secondary" onClick={() => handleExport("json")} disabled={!selectedTask}>
                导出 JSON
              </Button>
              <Button variant="secondary" onClick={() => handleExport("txt")} disabled={!selectedTask}>
                导出 TXT
              </Button>
              <Button variant="secondary" onClick={() => handleExport("pdf")} disabled={!selectedTask}>
                导出 PDF
              </Button>
              <Button variant="secondary" onClick={() => handleExport("docx")} disabled={!selectedTask}>
                导出 DOCX
              </Button>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-700">评分与反馈</h3>
            {selectedTask?.rating && (
              <Badge variant="secondary" className="text-xs">当前评分：{selectedTask.rating}</Badge>
            )}
          </div>
          <div className="mt-3 flex flex-wrap items-center gap-2">
            {[1, 2, 3, 4, 5].map((score) => (
              <Button
                key={score}
                variant="secondary"
                onClick={() => handleRate(score)}
                disabled={!selectedTask}
              >
                {score} 分
              </Button>
            ))}
          </div>
          <textarea
            className="mt-3 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
            placeholder="填写反馈（可选）"
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
          />
        </Card>

        <Card className="p-4">
          <h3 className="text-sm font-semibold text-slate-700">术语库</h3>
          <div className="mt-3 grid gap-3 md:grid-cols-3">
            <div className="md:col-span-2">
              <ScrollArea className="h-[200px]">
                <div className="space-y-2">
                  {terminology.length === 0 && (
                    <div className="text-xs text-slate-500">暂无术语</div>
                  )}
                  {terminology.map((term) => (
                    <div
                      key={term.id}
                      className="flex items-center justify-between rounded-md border border-slate-200 bg-slate-50 px-3 py-2 text-xs"
                    >
                      <div>
                        <div className="font-medium text-slate-700">{term.original_term}</div>
                        <div className="text-slate-500">{term.translation}</div>
                      </div>
                      <Badge variant="secondary" className="text-[10px]">
                        {term.domain}
                      </Badge>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </div>
            <div className="space-y-2">
              <div className="text-xs text-slate-500">新增术语</div>
              <input
                className="w-full rounded-md border border-slate-200 px-2 py-2 text-xs"
                placeholder="术语原文"
                value={termSource}
                onChange={(e) => setTermSource(e.target.value)}
              />
              <input
                className="w-full rounded-md border border-slate-200 px-2 py-2 text-xs"
                placeholder="术语译文"
                value={termTarget}
                onChange={(e) => setTermTarget(e.target.value)}
              />
              <select
                className="w-full rounded-md border border-slate-200 px-2 py-2 text-xs"
                value={termDomain}
                onChange={(e) => setTermDomain(e.target.value)}
              >
                {domainOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              <Button variant="secondary" onClick={handleAddTerm}>
                添加术语
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
