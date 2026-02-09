"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import KnowledgeBaseSelector from "@/components/knowledge/KnowledgeBaseSelector";
import {
  createWeeklyReport,
  createWorkLog,
  deleteWorkLog,
  deleteWeeklyReport,
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
  getPlaceholderCount,
  getSummaryPreview,
  normalizeSummary,
  parseWeeklySections,
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
  const [filterWeek, setFilterWeek] = useState("all");
  const [loadingLogs, setLoadingLogs] = useState(false);
  const [loadingReports, setLoadingReports] = useState(false);
  const [savingReport, setSavingReport] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [knowledgeBaseIds, setKnowledgeBaseIds] = useState<string[]>([]);

  const [logForm, setLogForm] = useState({
    work_type: "",
    task_description: "",
    hours_spent: "",
    log_date: weekRange.start
  });
  const [selectedLogIds, setSelectedLogIds] = useState<number[]>([]);
  const [useAiPolish, setUseAiPolish] = useState(false);

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
        limit: 1000
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
      const data = await listWeeklyReports({ limit: 100, skip: 0 });
      setReports(data.items || []);
    } catch (err: unknown) {
      setError(getErrorMessage(err, "获取周报列表失败"));
    } finally {
      setLoadingReports(false);
    }
  }, [getErrorMessage]);

  const weekOptions = useMemo(() => {
    const weeks = new Set(reports.map((report) => report.week));
    return ["all", ...Array.from(weeks)];
  }, [reports]);

  const visibleReports = useMemo(() => {
    if (filterWeek === "all") return reports;
    return reports.filter((report) => report.week === filterWeek);
  }, [filterWeek, reports]);

  const groupedReports = useMemo(() => {
    const grouped = new Map<string, WeeklyReport[]>();
    visibleReports.forEach((report) => {
      const list = grouped.get(report.week) || [];
      list.push(report);
      grouped.set(report.week, list);
    });
    return Array.from(grouped.entries()).map(([week, items]) => ({
      week,
      items
    }));
  }, [visibleReports]);

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

  const toggleLogSelection = (id: number) => {
    setSelectedLogIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const ensureSection = (text: string, header: string) => {
    if (text.includes(header)) return text;
    return text ? `${text}\n\n${header}\n- ` : `${header}\n- `;
  };

  const insertLinesIntoSection = (text: string, header: string, lines: string[]) => {
    if (!lines.length) return text;
    const normalized = ensureSection(text, header);
    const parts = normalized.split(/\r?\n/);
    const headerIndex = parts.findIndex((line) => line.replace(/[:：]\s*$/, "") === header.replace(/[:：]\s*$/, ""));
    if (headerIndex === -1) return normalized + "\n" + lines.map((line) => `- ${line}`).join("\n");

    let insertIndex = headerIndex + 1;
    while (insertIndex < parts.length && !/^[^\s].*[:：]$/.test(parts[insertIndex])) {
      insertIndex += 1;
    }

    const existing = new Set(
      parts
        .slice(headerIndex + 1, insertIndex)
        .map((line) => line.replace(/^[-*\d\.\)]+\s*/, "").trim())
        .filter(Boolean)
    );

    const toInsert = lines.filter((line) => !existing.has(line));
    const insertLines = toInsert.map((line) => `- ${line}`);
    parts.splice(insertIndex, 0, ...insertLines);
    return parts.join("\n");
  };

  const handleAddSelectedLogs = () => {
    if (!selectedReport) {
      setError("请先选择一份周报再添加记录");
      return;
    }
    if (!selectedLogIds.length) {
      setError("请选择需要添加的工作记录");
      return;
    }

    const selectedLogs = logs.filter((log) => selectedLogIds.includes(log.id));
    const lines = selectedLogs.map(
      (log) => `${log.work_type}：${log.task_description}（${log.hours_spent}h）`
    );

    setReportDraft((prev) => {
      const summaryWithHeader = ensureSection(prev.summary || "", "本周完成：");
      const contentWithHeader = ensureSection(prev.content || "", "本周完成：");
      return {
        ...prev,
        summary: insertLinesIntoSection(summaryWithHeader, "本周完成：", lines),
        content: insertLinesIntoSection(contentWithHeader, "本周完成：", lines)
      };
    });

    setSelectedLogIds([]);
  };

  const handleCreateReport = async () => {
    setError(null);
    try {
      const report = await createWeeklyReport({
        title: reportDraft.title || undefined,
        week_start_date: toIsoDateTime(weekStart),
        week_end_date: toIsoDateTime(weekEnd, true),
        ai_polish: useAiPolish
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
      setSelectedLogIds([]);
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

  const summarySections = useMemo(() => parseWeeklySections(reportDraft.summary), [reportDraft.summary]);
  const contentSections = useMemo(() => parseWeeklySections(reportDraft.content), [reportDraft.content]);
  const summaryPlaceholderCount = useMemo(
    () => getPlaceholderCount(reportDraft.summary),
    [reportDraft.summary]
  );
  const contentPlaceholderCount = useMemo(
    () => getPlaceholderCount(reportDraft.content),
    [reportDraft.content]
  );

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

  const handleDeleteReport = async () => {
    if (!selectedReport) return;
    setError(null);
    try {
      await deleteWeeklyReport(selectedReport.id);
      setSelectedReport(null);
      setReportDraft({ title: "", summary: "", content: "" });
      refreshReports();
    } catch (err: unknown) {
      setError(getErrorMessage(err, "删除周报失败"));
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
      <div className="w-[30rem] bg-slate-50 border-r border-slate-200 flex flex-col shrink-0 min-h-0">
        <div className="p-6 border-b border-slate-200 bg-white">
          <h2 className="text-lg font-semibold text-slate-800">周报整理</h2>
          <p className="text-xs text-slate-500 mt-1">基于工作记录自动汇总，可自行润色</p>
        </div>

        <div className="flex-1 min-h-0 flex flex-col">
          <div className="p-4 space-y-3">
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

            <KnowledgeBaseSelector
              value={knowledgeBaseIds}
              onChange={setKnowledgeBaseIds}
              title="引用知识库"
            />

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
        </div>
      </div>

      <div className="flex-1 flex flex-col bg-white min-h-0">
        <div className="h-16 border-b border-slate-200 flex items-center justify-between px-6">
          <div>
            <h1 className="font-semibold text-slate-800">周报生成</h1>
            <p className="text-xs text-slate-500">根据记录自动汇总，支持手动润色与导出</p>
          </div>
          <div className="flex gap-2">
            <Button variant="secondary" onClick={refreshReports}>
              刷新列表
            </Button>
            <label className="flex items-center gap-2 text-xs text-slate-500">
              <input
                type="checkbox"
                checked={useAiPolish}
                onChange={(e) => setUseAiPolish(e.target.checked)}
              />
              AI 扩写润色
            </label>
            <Button onClick={handleCreateReport}>生成周报</Button>
          </div>
        </div>

        <div className="flex-1 min-h-0 grid grid-cols-[320px_1fr] overflow-hidden">
          <div className="border-r border-slate-200 p-6 flex flex-col min-h-0">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold text-slate-700">历史周报</h3>
              <Badge variant="secondary" className="text-xs">
                {loadingReports ? "加载中" : `${reports.length} 份`}
              </Badge>
            </div>
            <div className="mb-4">
              <label className="block text-[11px] text-slate-500 mb-1">按周筛选</label>
              <select
                className="w-full rounded-md border border-slate-200 px-2 py-1 text-xs"
                value={filterWeek}
                onChange={(e) => setFilterWeek(e.target.value)}
              >
                {weekOptions.map((week) => (
                  <option key={week} value={week}>
                    {week === "all" ? "全部周次" : week}
                  </option>
                ))}
              </select>
            </div>
            <ScrollArea className="h-[320px]">
              <div className="space-y-4">
                {visibleReports.length === 0 && !loadingReports && (
                  <div className="text-xs text-slate-500">暂无周报</div>
                )}
                {groupedReports.map(({ week, items }) => (
                  <div key={week} className="space-y-2">
                    <div className="text-[11px] font-semibold text-slate-500">
                      {week}
                    </div>
                    {items.map((report) => (
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
                        <div className="text-[11px] text-slate-500">
                          摘要：{getSummaryPreview(report.summary)}
                        </div>
                      </Card>
                    ))}
                  </div>
                ))}
              </div>
            </ScrollArea>

            <div className="mt-6 border-t border-slate-200 pt-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-semibold text-slate-700">本周记录</h3>
                <Badge variant="secondary" className="text-xs">
                  {loadingLogs ? "加载中" : `${logs.length} 条`}
                </Badge>
              </div>
              <div className="mb-3 flex items-center justify-between">
                <span className="text-[11px] text-slate-500">
                  已选择 {selectedLogIds.length} 条
                </span>
                <Button
                  variant="secondary"
                  className="text-xs"
                  onClick={handleAddSelectedLogs}
                  disabled={!selectedLogIds.length}
                >
                  添加进周报
                </Button>
              </div>
              <ScrollArea className="h-[260px]">
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
                      <div className="flex items-center justify-between">
                        <label className="text-[11px] text-slate-500 flex items-center gap-2">
                          <input
                            type="checkbox"
                            checked={selectedLogIds.includes(log.id)}
                            onChange={() => toggleLogSelection(log.id)}
                          />
                          选入周报
                        </label>
                        <Button
                          variant="secondary"
                          className="text-xs"
                          onClick={() => {
                            setSelectedLogIds([log.id]);
                            handleAddSelectedLogs();
                          }}
                        >
                          立刻添加
                        </Button>
                      </div>
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
                  <div className="grid gap-3 rounded-md border border-slate-100 bg-slate-50 p-3">
                    <div>
                      <div className="text-[11px] font-semibold text-slate-600">结构化摘要预览</div>
                      <div className="mt-2 grid grid-cols-1 gap-2 text-xs text-slate-600">
                        <div>
                          <span className="font-medium text-slate-700">本周完成：</span>
                          {summarySections.completed.length
                            ? summarySections.completed.join("；")
                            : "暂无"}
                        </div>
                        <div>
                          <span className="font-medium text-slate-700">问题与风险：</span>
                          {summarySections.risks.length
                            ? summarySections.risks.join("；")
                            : "暂无"}
                        </div>
                        <div>
                          <span className="font-medium text-slate-700">下周计划：</span>
                          {summarySections.plans.length
                            ? summarySections.plans.join("；")
                            : "暂无"}
                        </div>
                      </div>
                    </div>
                    <div>
                      <div className="text-[11px] font-semibold text-slate-600">详细内容预览</div>
                      <div className="mt-2 grid grid-cols-1 gap-2 text-xs text-slate-600">
                        <div>
                          <span className="font-medium text-slate-700">本周完成：</span>
                          {contentSections.completed.length
                            ? contentSections.completed.join("；")
                            : "暂无"}
                        </div>
                        <div>
                          <span className="font-medium text-slate-700">问题与风险：</span>
                          {contentSections.risks.length
                            ? contentSections.risks.join("；")
                            : "暂无"}
                        </div>
                        <div>
                          <span className="font-medium text-slate-700">下周计划：</span>
                          {contentSections.plans.length
                            ? contentSections.plans.join("；")
                            : "暂无"}
                        </div>
                      </div>
                    </div>
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
                    {summaryPlaceholderCount > 0 && (
                      <p className="text-[11px] text-amber-600">
                        还有 {summaryPlaceholderCount} 处占位未填写。
                      </p>
                    )}
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
                    {contentPlaceholderCount > 0 && (
                      <p className="text-[11px] text-amber-600">
                        还有 {contentPlaceholderCount} 处占位未填写。
                      </p>
                    )}
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
                      className="text-red-600 border-red-200"
                      onClick={handleDeleteReport}
                      disabled={selectedReport.status !== "draft"}
                    >
                      删除周报
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
