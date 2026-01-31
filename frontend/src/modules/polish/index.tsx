"use client";

import { useEffect, useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  acceptPolishIssue,
  createPolishTask,
  exportPolishResult,
  getPolishTask,
  listPolishTasks,
  rejectPolishIssue
} from "./api";
import type { PolishIssue, PolishTask } from "./types";

const levelOptions = [
  { value: "standard", label: "标准" },
  { value: "academic", label: "学术" },
  { value: "formal", label: "正式" }
];

export default function PolishModule() {
  const [text, setText] = useState("");
  const [level, setLevel] = useState("standard");
  const [autoFix, setAutoFix] = useState(true);
  const [tasks, setTasks] = useState<PolishTask[]>([]);
  const [selectedTask, setSelectedTask] = useState<PolishTask | null>(null);
  const [issues, setIssues] = useState<PolishIssue[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const totalIssues = useMemo(() => issues.length, [issues]);

  const loadTasks = async () => {
    try {
      const data = await listPolishTasks({ skip: 0, limit: 20 });
      setTasks(data.items || []);
      if (data.items?.length && !selectedTask) {
        await handleSelectTask(data.items[0].id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "获取任务失败");
    }
  };

  useEffect(() => {
    loadTasks();
  }, []);

  const handleCreate = async () => {
    if (!text.trim()) {
      setError("请输入需要润色的文本");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const task = await createPolishTask({
        original_text: text.trim(),
        polish_level: level,
        auto_fix_enabled: autoFix
      });
      setSelectedTask(task);
      setIssues((task as { issues?: PolishIssue[] }).issues || []);
      await loadTasks();
    } catch (err) {
      setError(err instanceof Error ? err.message : "创建任务失败");
    } finally {
      setLoading(false);
    }
  };

  const handleSelectTask = async (taskId: number) => {
    setError(null);
    try {
      const data = await getPolishTask(taskId);
      setSelectedTask(data);
      setIssues(data.issues || []);
      setText(data.original_text || "");
      setLevel(data.polish_level || "standard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "获取任务失败");
    }
  };

  const handleAccept = async (issueId: number) => {
    if (!selectedTask) return;
    try {
      await acceptPolishIssue(selectedTask.id, issueId);
      await handleSelectTask(selectedTask.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "更新建议失败");
    }
  };

  const handleReject = async (issueId: number) => {
    if (!selectedTask) return;
    try {
      await rejectPolishIssue(selectedTask.id, issueId);
      await handleSelectTask(selectedTask.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "更新建议失败");
    }
  };

  const handleExport = async (format: "json" | "txt") => {
    if (!selectedTask) return;
    try {
      const data = await exportPolishResult(selectedTask.id, format);
      const content = typeof data === "string" ? data : JSON.stringify(data, null, 2);
      const blob = new Blob([content], { type: format === "txt" ? "text/plain" : "application/json" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `polish-${selectedTask.id}.${format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : "导出失败");
    }
  };

  return (
    <div className="flex h-full w-full gap-0 overflow-hidden rounded-lg border border-slate-200 bg-white shadow-lg">
      <div className="w-80 shrink-0 border-r border-slate-200 bg-slate-50">
        <div className="border-b border-slate-200 bg-white p-6">
          <h2 className="text-lg font-semibold text-slate-800">学术润色</h2>
          <p className="mt-1 text-xs text-slate-500">检查术语、时态、风格与论文规范</p>
        </div>
        <div className="p-6 space-y-4">
          <div className="space-y-2">
            <label className="text-xs text-slate-500">润色级别</label>
            <select
              className="w-full rounded-md border border-slate-200 px-2 py-2 text-sm"
              value={level}
              onChange={(e) => setLevel(e.target.value)}
            >
              {levelOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          <label className="flex items-center gap-2 text-sm text-slate-600">
            <input
              type="checkbox"
              checked={autoFix}
              onChange={(e) => setAutoFix(e.target.checked)}
            />
            自动套用建议
          </label>
          <Button onClick={handleCreate} disabled={loading} className="w-full">
            {loading ? "处理中..." : "开始润色"}
          </Button>
        </div>
        <div className="px-6 pb-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-slate-700">历史记录</h3>
            <Badge variant="secondary" className="text-xs">
              {tasks.length} 条
            </Badge>
          </div>
          <ScrollArea className="h-[360px]">
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
                    问题数：{task.total_issues}
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

        <div className="grid gap-4 lg:grid-cols-2">
          <Card className="p-4 space-y-3">
            <h3 className="text-sm font-semibold text-slate-700">原文</h3>
            <textarea
              className="min-h-[280px] w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="粘贴需要润色的学术内容"
            />
          </Card>
          <Card className="p-4 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-slate-700">润色结果</h3>
              {selectedTask && (
                <Badge variant="secondary" className="text-xs">
                  {selectedTask.status}
                </Badge>
              )}
            </div>
            <textarea
              className="min-h-[280px] w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
              value={selectedTask?.polished_text || ""}
              readOnly
            />
            <div className="flex flex-wrap gap-2">
              <Button variant="secondary" onClick={() => handleExport("json")}>
                导出 JSON
              </Button>
              <Button variant="secondary" onClick={() => handleExport("txt")}>
                导出 TXT
              </Button>
            </div>
          </Card>
        </div>

        <Card className="mt-4 p-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-700">问题清单</h3>
            <span className="text-xs text-slate-500">共 {totalIssues} 条</span>
          </div>
          <div className="mt-3 space-y-3">
            {issues.length === 0 && (
              <div className="text-xs text-slate-500">当前没有检测到问题</div>
            )}
            {issues.map((issue) => (
              <div
                key={issue.id}
                className="rounded-md border border-slate-200 bg-slate-50 p-3 text-xs"
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium text-slate-700">{issue.issue_type}</span>
                  <Badge variant="secondary" className="text-[10px]">
                    {issue.status}
                  </Badge>
                </div>
                <p className="mt-2 text-slate-600">原文：{issue.original_content}</p>
                <p className="mt-1 text-slate-600">建议：{issue.suggested_content}</p>
                {issue.reason && (
                  <p className="mt-1 text-slate-500">原因：{issue.reason}</p>
                )}
                <div className="mt-2 flex gap-2">
                  <Button
                    variant="secondary"
                    className="h-7 px-2 text-[11px]"
                    onClick={() => handleAccept(issue.id)}
                    disabled={issue.status === "accepted"}
                  >
                    采纳
                  </Button>
                  <Button
                    variant="secondary"
                    className="h-7 px-2 text-[11px]"
                    onClick={() => handleReject(issue.id)}
                    disabled={issue.status === "rejected"}
                  >
                    忽略
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
