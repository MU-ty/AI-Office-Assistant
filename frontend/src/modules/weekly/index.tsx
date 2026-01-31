"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  createWeeklyReport,
  createWorkLog,
  deleteWorkLog,
  exportWeeklyReport,
  getWeeklyReport,
  listWeeklyReports,
  listWorkLogs,
  updateWeeklyReport
} from "./api";
import type { WeeklyReport, WorkLog } from "./types";
import {
  formatDate,
  getCurrentWeekRange,
  getDetailTemplate,
  getSummaryTemplate,
  normalizeSummary,
  toIsoDateTime
} from "./utils";

export default function WeeklyReportModule() {
  const weekRange = useMemo(() => getCurrentWeekRange(), []);
  const [weekStart, setWeekStart] = useState(weekRange.start);
  const [weekEnd, setWeekEnd] = useState(weekRange.end);
  const [isAuthed, setIsAuthed] = useState(true);

  const [logs, setLogs] = useState<WorkLog[]>([]);
  const [reports, setReports] = useState<WeeklyReport[]>([]);
  const [selectedReport, setSelectedReport] = useState<WeeklyReport | null>(null);
  const [loadingLogs, setLoadingLogs] = useState(false);
  const [loadingReports, setLoadingReports] = useState(false);
  const [savingReport, setSavingReport] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [logForm, setLogForm] = useState({
    work_type: "",
    task_description: "",
    hours_spent: "",
    log_date: weekRange.start
  });

  const [reportDraft, setReportDraft] = useState({
    title: "",
    summary: "",
    content: ""
  });

  const getErrorMessage = useCallback((err: unknown, fallback: string) => {
    if (err instanceof Error) return err.message;
    if (typeof err === "string") return err;
    return fallback;
  }, []);

  const refreshLogs = useCallback(async () => {
    setLoadingLogs(true);
    setError(null);
    try {
      const data = await listWorkLogs({
        date_from: weekStart,
        date_to: weekEnd,
        skip: 0,
        limit: 200
      });
      setLogs(data.items || []);
    } catch (err: unknown) {
      setError(getErrorMessage(err, "获取工作记录失败"));
    } finally {
      setLoadingLogs(false);
    }
  }, [getErrorMessage, weekEnd, weekStart]);

  const refreshReports = useCallback(async () => {
    setLoadingReports(true);
    setError(null);
    try {
      const data = await listWeeklyReports({ limit: 20, skip: 0 });
      setReports(data.items || []);
    } catch (err: unknown) {
      setError(getErrorMessage(err, "获取周报列表失败"));
    } finally {
      setLoadingReports(false);
    }
  }, [getErrorMessage]);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("access_token");
      setIsAuthed(Boolean(token));
    }
  }, []);

  useEffect(() => {
    refreshLogs();
  }, [refreshLogs]);

  useEffect(() => {
    refreshReports();
  }, [refreshReports]);

  if (!isAuthed) {
    return (
      <div className="flex h-full w-full items-center justify-center">
        <Card className="max-w-md p-6 text-center">
          <h2 className="text-lg font-semibold text-slate-800">请先登录</h2>
          <p className="mt-2 text-sm text-slate-500">
            登录后才能创建和管理你的周报记录。
          </p>
          <Link
            href="/auth/login"
            className="mt-4 inline-flex items-center justify-center rounded-md bg-blue-600 px-4 py-2 text-sm text-white"
          >
            前往登录
          </Link>
        </Card>
      </div>
    );
  }

  const handleCreateLog = async () => {
    setError(null);
    if (!logForm.work_type || !logForm.task_description || !logForm.hours_spent) {
      setError("请完整填写工作类型、任务描述与耗时");
      return;
    }

    try {
      await createWorkLog({
        work_type: logForm.work_type,
        task_description: logForm.task_description,
        hours_spent: Number(logForm.hours_spent),
        log_date: logForm.log_date ? toIsoDateTime(logForm.log_date) : undefined
      });
      setLogForm((prev) => ({
        ...prev,
        task_description: "",
        hours_spent: ""
      }));
      refreshLogs();
    } catch (err: unknown) {
      setError(getErrorMessage(err, "新增记录失败"));
    }
  };

  const handleDeleteLog = async (id: number) => {
    setError(null);
    try {
      await deleteWorkLog(id);
      refreshLogs();
    } catch (err: unknown) {
      setError(getErrorMessage(err, "删除记录失败"));
    }
  };

  const handleCreateReport = async () => {
    setError(null);
    try {
      const report = await createWeeklyReport({
        title: reportDraft.title || undefined,
        week_start_date: toIsoDateTime(weekStart),
        week_end_date: toIsoDateTime(weekEnd, true)
      });
      setSelectedReport(report);
      const summary = normalizeSummary(report.summary);
      setReportDraft({
        title: report.title || "",
        summary: summary || getSummaryTemplate(),
        content: report.content || getDetailTemplate()
      });
      refreshReports();
    } catch (err: unknown) {
      setError(getErrorMessage(err, "生成周报失败"));
    }
  };

  const handleSelectReport = async (reportId: number) => {
    setError(null);
    try {
      const report = await getWeeklyReport(reportId);
      setSelectedReport(report);
      const summary = normalizeSummary(report.summary);
      setReportDraft({
        title: report.title || "",
        summary: summary || getSummaryTemplate(),
        content: report.content || getDetailTemplate()
      });
    } catch (err: unknown) {
      setError(getErrorMessage(err, "获取周报详情失败"));
    }
  };

  const handleApplyTemplate = () => {
    setReportDraft((prev) => ({
      ...prev,
      summary: prev.summary?.trim() ? prev.summary : getSummaryTemplate(),
      content: prev.content?.trim() ? prev.content : getDetailTemplate()
    }));
  };

  const handleSaveReport = async () => {
    if (!selectedReport) return;
    setSavingReport(true);
    setError(null);
    try {
      const updated = await updateWeeklyReport(selectedReport.id, {
        title: reportDraft.title,
        summary: reportDraft.summary,
        content: reportDraft.content
      });
      setSelectedReport(updated);
      refreshReports();
    } catch (err: unknown) {
      setError(getErrorMessage(err, "保存周报失败"));
    } finally {
      setSavingReport(false);
    }
  };


  const handleExportReport = async (format: "markdown" | "html" | "pdf" | "docx") => {
    if (!selectedReport) return;
    setError(null);
    try {
      const data = await exportWeeklyReport(selectedReport.id, format);
      if (format === "pdf" || format === "docx") {
        const path = data.path as string | undefined;
        if (!path) {
          throw new Error("导出失败：未返回文件路径");
        }
        const downloadUrl = path.startsWith("http")
          ? path
          : `${process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8003"}${path.replace(/\\/g, "/")}`;
        const fileResponse = await fetch(downloadUrl);
        if (!fileResponse.ok) {
          throw new Error("下载文件失败");
        }
        const fileBlob = await fileResponse.blob();
        const fileUrl = URL.createObjectURL(fileBlob);
        const link = document.createElement("a");
        link.href = fileUrl;
        link.download = `${selectedReport.title || "weekly-report"}.${format}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(fileUrl);
        return;
      }

      const blob = new Blob([data.content || ""], {
        type: format === "html" ? "text/html" : "text/markdown"
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${selectedReport.title || "weekly-report"}.${
        format === "html" ? "html" : "md"
      }`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (err: unknown) {
      setError(getErrorMessage(err, "导出周报失败"));
    }
  };

  return (
    <div className="flex-1 flex gap-0 overflow-hidden w-full h-full border border-slate-200 rounded-lg shadow-lg">
      <div className="w-80 bg-slate-50 border-r border-slate-200 flex flex-col shrink-0">
        <div className="p-6 border-b border-slate-200 bg-white">
          <h2 className="text-lg font-semibold text-slate-800">周报整理</h2>
          <p className="text-xs text-slate-500 mt-1">基于工作记录自动汇总，可自行润色</p>
        </div>

        <div className="p-6 space-y-4">
          <div>
            <label className="block text-xs text-slate-500 mb-1">周起止日期</label>
            <div className="flex gap-2">
              <input
                type="date"
                className="w-full rounded-md border border-slate-200 px-2 py-1 text-sm"
                value={weekStart}
                onChange={(e) => setWeekStart(e.target.value)}
              />
              <input
                type="date"
                className="w-full rounded-md border border-slate-200 px-2 py-1 text-sm"
                value={weekEnd}
                onChange={(e) => setWeekEnd(e.target.value)}
              />
            </div>
          </div>

          <div className="rounded-lg border border-slate-200 bg-white p-4 space-y-3">
            <h3 className="text-sm font-medium text-slate-700">新增工作记录</h3>
            <input
              className="w-full rounded-md border border-slate-200 px-2 py-1 text-sm"
              placeholder="工作类型（例：需求分析 / 开发 / 会议）"
              value={logForm.work_type}
              onChange={(e) =>
                setLogForm((prev) => ({ ...prev, work_type: e.target.value }))
              }
            />
            <textarea
              className="w-full rounded-md border border-slate-200 px-2 py-1 text-sm min-h-[80px]"
              placeholder="任务描述（尽量写成业务视角，比如：完成某功能的联调/上线准备）"
              value={logForm.task_description}
              onChange={(e) =>
                setLogForm((prev) => ({ ...prev, task_description: e.target.value }))
              }
            />
            <div className="flex gap-2">
              <input
                type="number"
                step="0.5"
                className="w-full rounded-md border border-slate-200 px-2 py-1 text-sm"
                placeholder="耗时（小时）"
                value={logForm.hours_spent}
                onChange={(e) =>
                  setLogForm((prev) => ({ ...prev, hours_spent: e.target.value }))
                }
              />
              <input
                type="date"
                className="w-full rounded-md border border-slate-200 px-2 py-1 text-sm"
                value={logForm.log_date}
                onChange={(e) =>
                  setLogForm((prev) => ({ ...prev, log_date: e.target.value }))
                }
              />
            </div>
            <Button onClick={handleCreateLog} className="w-full">
              保存记录
            </Button>
          </div>
        </div>

        <div className="flex-1 p-6 pt-0 overflow-hidden">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-slate-700">本周记录</h3>
            <Badge variant="secondary" className="text-xs">
              {loadingLogs ? "加载中" : `${logs.length} 条`}
            </Badge>
          </div>
          <ScrollArea className="h-[320px]">
            <div className="space-y-3">
              {logs.length === 0 && !loadingLogs && (
                <div className="text-xs text-slate-500">暂无记录</div>
              )}
              {logs.map((log) => (
                <Card key={log.id} className="p-3 space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="text-xs font-medium text-slate-700">
                      {log.work_type}
                    </div>
                    <span className="text-[11px] text-slate-400">
                      {formatDate(log.log_date)} · {log.hours_spent}h
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    {log.task_description}
                  </p>
                  <Button
                    variant="secondary"
                    className="w-full text-xs"
                    onClick={() => handleDeleteLog(log.id)}
                  >
                    删除
                  </Button>
                </Card>
              ))}
            </div>
          </ScrollArea>
        </div>
      </div>

      <div className="flex-1 flex flex-col bg-white">
        <div className="h-16 border-b border-slate-200 flex items-center justify-between px-6">
          <div>
            <h1 className="font-semibold text-slate-800">周报生成</h1>
            <p className="text-xs text-slate-500">根据记录自动汇总，支持手动润色与导出</p>
          </div>
          <div className="flex gap-2">
            <Button variant="secondary" onClick={refreshReports}>
              刷新列表
            </Button>
            <Button onClick={handleCreateReport}>生成周报</Button>
          </div>
        </div>

        <div className="flex-1 grid grid-cols-[320px_1fr] overflow-hidden">
          <div className="border-r border-slate-200 p-6">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold text-slate-700">历史周报</h3>
              <Badge variant="secondary" className="text-xs">
                {loadingReports ? "加载中" : `${reports.length} 份`}
              </Badge>
            </div>
            <ScrollArea className="h-[520px]">
              <div className="space-y-3">
                {reports.length === 0 && !loadingReports && (
                  <div className="text-xs text-slate-500">暂无周报</div>
                )}
                {reports.map((report) => (
                  <Card
                    key={report.id}
                    className={`p-3 space-y-2 cursor-pointer transition hover:shadow ${
                      selectedReport?.id === report.id ? "border-blue-500" : ""
                    }`}
                    onClick={() => handleSelectReport(report.id)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="text-xs font-medium text-slate-700">
                        {report.title || report.week}
                      </div>
                      <Badge
                        variant={report.status === "draft" ? "secondary" : "default"}
                        className="text-[10px]"
                      >
                        {report.status}
                      </Badge>
                    </div>
                    <div className="text-[11px] text-slate-400">
                      {formatDate(report.week_start_date)} - {formatDate(report.week_end_date)}
                    </div>
                    <div className="text-[11px] text-slate-500">
                      总工时：{report.total_hours}h
                    </div>
                  </Card>
                ))}
              </div>
            </ScrollArea>
          </div>

          <div className="p-6 space-y-4 overflow-y-auto">
            {error && (
              <div className="rounded-md bg-red-50 border border-red-200 px-3 py-2 text-xs text-red-600">
                {error}
              </div>
            )}

            {!selectedReport ? (
              <div className="text-sm text-slate-500">
                请选择左侧周报或点击“生成周报”开始整理。
              </div>
            ) : (
              <>
                <Card className="p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-semibold text-slate-700">周报内容</h3>
                    <Badge className="text-[10px]" variant="secondary">
                      {selectedReport.status}
                    </Badge>
                  </div>
                  <div className="grid gap-2">
                    <label className="text-xs text-slate-500">标题</label>
                    <input
                      className="w-full rounded-md border border-slate-200 px-2 py-1 text-sm"
                      value={reportDraft.title}
                      onChange={(e) =>
                        setReportDraft((prev) => ({ ...prev, title: e.target.value }))
                      }
                    />
                  </div>
                  <div className="grid gap-2">
                    <label className="text-xs text-slate-500">摘要</label>
                    <textarea
                      className="w-full rounded-md border border-slate-200 px-2 py-1 text-sm min-h-[120px]"
                      value={reportDraft.summary}
                      onChange={(e) =>
                        setReportDraft((prev) => ({ ...prev, summary: e.target.value }))
                      }
                    />
                    <p className="text-[11px] text-slate-400">
                      建议写法：用业务成果+结果描述，比如“完成 XX 功能联调，关键流程可用”。
                    </p>
                  </div>
                  <div className="grid gap-2">
                    <label className="text-xs text-slate-500">详细内容（可选）</label>
                    <textarea
                      className="w-full rounded-md border border-slate-200 px-2 py-1 text-sm min-h-[160px]"
                      value={reportDraft.content}
                      onChange={(e) =>
                        setReportDraft((prev) => ({ ...prev, content: e.target.value }))
                      }
                    />
                    <p className="text-[11px] text-slate-400">
                      可以补充：问题/风险、协作事项、下周计划等。
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <Button variant="secondary" onClick={handleApplyTemplate}>
                      填充结构模板
                    </Button>
                    <Button onClick={handleSaveReport} disabled={savingReport}>
                      保存
                    </Button>
                    <Button
                      variant="secondary"
                      onClick={() => handleExportReport("markdown")}
                    >
                      导出 Markdown
                    </Button>
                    <Button
                      variant="secondary"
                      onClick={() => handleExportReport("html")}
                    >
                      导出 HTML
                    </Button>
                    <Button
                      variant="secondary"
                      onClick={() => handleExportReport("pdf")}
                    >
                      导出 PDF
                    </Button>
                    <Button
                      variant="secondary"
                      onClick={() => handleExportReport("docx")}
                    >
                      导出 Word
                    </Button>
                  </div>
                </Card>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
