"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle
} from "@/components/ui/dialog";
import {
  fetchDocumentHistory,
  fetchMeetingHistory,
  fetchPolishHistory,
  fetchPptHistory,
  fetchTranslationHistory,
  fetchWeeklyHistory
} from "./api";

type HistoryItem = Record<string, unknown>;

export default function HistoryModule() {
  const [meetings, setMeetings] = useState<HistoryItem[]>([]);
  const [weeklyReports, setWeeklyReports] = useState<HistoryItem[]>([]);
  const [polishTasks, setPolishTasks] = useState<HistoryItem[]>([]);
  const [documents, setDocuments] = useState<HistoryItem[]>([]);
  const [translations, setTranslations] = useState<HistoryItem[]>([]);
  const [pptProjects, setPptProjects] = useState<HistoryItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [keyword, setKeyword] = useState("");
  const [moduleFilter, setModuleFilter] = useState("all");
  const [previewTitle, setPreviewTitle] = useState("记录预览");
  const [previewItem, setPreviewItem] = useState<HistoryItem | null>(null);

  const loadHistory = async () => {
    try {
      const [meetingRes, weeklyRes, polishRes, docRes, transRes, pptRes] = await Promise.all([
        fetchMeetingHistory(),
        fetchWeeklyHistory(),
        fetchPolishHistory(),
        fetchDocumentHistory(),
        fetchTranslationHistory(),
        fetchPptHistory()
      ]);
      setMeetings(meetingRes || []);
      setWeeklyReports(weeklyRes?.items || []);
      setPolishTasks(polishRes?.items || []);
      setDocuments(docRes || []);
      setTranslations(transRes?.items || []);
      setPptProjects(pptRes?.items || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "获取历史失败");
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const normalizeText = (value: unknown) => (value ? String(value).toLowerCase() : "");
  const matchesKeyword = (item: HistoryItem) => {
    if (!keyword.trim()) return true;
    const target = keyword.trim().toLowerCase();
    const fields = [item.title, item.status, item.source_language, item.target_language, item.source_type, item.id];
    return fields.some((field) => normalizeText(field).includes(target));
  };

  const filteredMeetings = meetings.filter(matchesKeyword);
  const filteredWeekly = weeklyReports.filter(matchesKeyword);
  const filteredPolish = polishTasks.filter(matchesKeyword);
  const filteredDocs = documents.filter(matchesKeyword);
  const filteredTranslations = translations.filter(matchesKeyword);
  const filteredPpt = pptProjects.filter(matchesKeyword);

  const totalCount =
    filteredMeetings.length +
    filteredWeekly.length +
    filteredPolish.length +
    filteredDocs.length +
    filteredTranslations.length +
    filteredPpt.length;

  const percent = (count: number) => (totalCount ? Math.round((count / totalCount) * 100) : 0);

  const handleExport = (format: "json" | "csv") => {
    const data = {
      meetings: filteredMeetings,
      weekly_reports: filteredWeekly,
      polish_tasks: filteredPolish,
      documents: filteredDocs,
      translations: filteredTranslations,
      ppt_projects: filteredPpt
    };

    if (format === "json") {
      const content = JSON.stringify(data, null, 2);
      const blob = new Blob([content], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "history-export.json";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      return;
    }

    const rows: string[] = ["module,title,status,meta"]; 
    const pushRows = (module: string, items: HistoryItem[]) => {
      items.forEach((item) => {
        const title = String(item.title || item.id || "").replace(/"/g, '""');
        const status = String(item.status || "").replace(/"/g, '""');
        const meta = JSON.stringify(item).replace(/"/g, '""');
        rows.push(`"${module}","${title}","${status}","${meta}"`);
      });
    };
    pushRows("meeting", filteredMeetings);
    pushRows("weekly", filteredWeekly);
    pushRows("polish", filteredPolish);
    pushRows("document", filteredDocs);
    pushRows("translation", filteredTranslations);
    pushRows("ppt", filteredPpt);

    const blob = new Blob([rows.join("\n")], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "history-export.csv";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const openPreview = (title: string, item: HistoryItem) => {
    setPreviewTitle(title);
    setPreviewItem(item);
  };

  const closePreview = () => {
    setPreviewItem(null);
  };

  const formatPreviewValue = (value: unknown) => {
    if (value === null || value === undefined) return "-";
    if (typeof value === "string") {
      return value.length > 240 ? `${value.slice(0, 240)}...` : value;
    }
    if (typeof value === "number" || typeof value === "boolean") return String(value);
    return JSON.stringify(value, null, 2);
  };

  const previewFields = (item: HistoryItem) => {
    const keys = [
      "id",
      "title",
      "status",
      "created_at",
      "updated_at",
      "week",
      "source_language",
      "target_language",
      "source_type",
      "meeting_type",
      "description",
      "summary",
      "content"
    ];
    return keys
      .filter((key) => key in item)
      .map((key) => ({ label: key.replace(/_/g, " "), value: item[key] }));
  };

  const Section = ({
    title,
    items,
    link,
    render
  }: {
    title: string;
    items: HistoryItem[];
    link: string;
    render: (item: HistoryItem, index: number) => React.ReactNode;
  }) => (
    <Card className="p-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-700">{title}</h3>
        <div className="flex items-center gap-2">
          <Badge variant="secondary" className="text-xs">
            {items.length} 条
          </Badge>
          <Link href={link}>
            <Button variant="secondary" size="sm">进入</Button>
          </Link>
        </div>
      </div>
      <div className="mt-3 space-y-2">
        {items.length === 0 && (
          <div className="text-xs text-slate-500">暂无记录</div>
        )}
        {items.map((item, index) => (
          <div
            key={`${title}-${index}`}
            className="rounded-md border border-slate-200 bg-slate-50 px-3 py-2 text-xs"
          >
            {render(item, index)}
          </div>
        ))}
      </div>
    </Card>
  );

  return (
    <div className="mx-auto w-full max-w-6xl space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-slate-800">历史记录</h2>
          <p className="text-xs text-slate-500">汇总六个功能的最近生成记录</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="secondary" onClick={() => handleExport("json")}>导出 JSON</Button>
          <Button variant="secondary" onClick={() => handleExport("csv")}>导出 CSV</Button>
          <Button variant="secondary" onClick={loadHistory}>刷新</Button>
        </div>
      </div>

      <Card className="p-4">
        <div className="flex flex-wrap items-center gap-3">
          <input
            className="w-64 rounded-md border border-slate-200 px-3 py-2 text-sm"
            placeholder="搜索标题/状态/语言"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
          />
          <select
            className="rounded-md border border-slate-200 px-3 py-2 text-sm"
            value={moduleFilter}
            onChange={(e) => setModuleFilter(e.target.value)}
          >
            <option value="all">全部模块</option>
            <option value="meeting">会议纪要</option>
            <option value="weekly">周报生成</option>
            <option value="polish">学术润色</option>
            <option value="document">文献摘要</option>
            <option value="translation">多语言翻译</option>
            <option value="ppt">PPT生成</option>
          </select>
          <span className="text-xs text-slate-500">当前共 {totalCount} 条</span>
        </div>
      </Card>

      <Card className="p-4">
        <div className="text-sm font-semibold text-slate-700">六个功能生成占比</div>
        <div className="mt-3 grid gap-4 lg:grid-cols-[1fr_220px]">
          <div className="grid gap-2">
            {[
              { label: "会议纪要", count: filteredMeetings.length, color: "bg-blue-500" },
              { label: "周报生成", count: filteredWeekly.length, color: "bg-indigo-500" },
              { label: "学术润色", count: filteredPolish.length, color: "bg-emerald-500" },
              { label: "文献摘要", count: filteredDocs.length, color: "bg-amber-500" },
              { label: "多语言翻译", count: filteredTranslations.length, color: "bg-purple-500" },
              { label: "PPT生成", count: filteredPpt.length, color: "bg-rose-500" }
            ].map((item) => (
              <div key={item.label} className="flex items-center gap-3 text-xs">
                <span className="w-20 text-slate-600">{item.label}</span>
                <div className="h-2 w-full rounded-full bg-slate-100">
                  <div
                    className={`h-2 rounded-full ${item.color}`}
                    style={{ width: `${percent(item.count)}%` }}
                  />
                </div>
                <span className="w-12 text-right text-slate-500">{percent(item.count)}%</span>
              </div>
            ))}
          </div>
          <div className="flex items-center justify-center">
            <svg viewBox="0 0 200 200" className="h-40 w-40">
              {(() => {
                const segments = [
                  { label: "会议纪要", value: filteredMeetings.length, color: "#3b82f6" },
                  { label: "周报生成", value: filteredWeekly.length, color: "#6366f1" },
                  { label: "学术润色", value: filteredPolish.length, color: "#10b981" },
                  { label: "文献摘要", value: filteredDocs.length, color: "#f59e0b" },
                  { label: "多语言翻译", value: filteredTranslations.length, color: "#a855f7" },
                  { label: "PPT生成", value: filteredPpt.length, color: "#f43f5e" }
                ];

                const radius = 80;
                const cx = 100;
                const cy = 100;
                const full = totalCount || 1;

                let startAngle = -90;

                const toPoint = (angle: number) => {
                  const rad = (Math.PI / 180) * angle;
                  return {
                    x: cx + radius * Math.cos(rad),
                    y: cy + radius * Math.sin(rad)
                  };
                };

                const describeSlice = (start: number, end: number) => {
                  const startPt = toPoint(start);
                  const endPt = toPoint(end);
                  const largeArc = end - start > 180 ? 1 : 0;
                  return `M ${cx} ${cy} L ${startPt.x} ${startPt.y} A ${radius} ${radius} 0 ${largeArc} 1 ${endPt.x} ${endPt.y} Z`;
                };

                return segments.map((seg, idx) => {
                  if (seg.value <= 0) {
                    return null;
                  }
                  const angle = (seg.value / full) * 360;
                  const endAngle = startAngle + angle;
                  const midAngle = startAngle + angle / 2;
                  const labelPoint = (() => {
                    const rad = (Math.PI / 180) * midAngle;
                    return {
                      x: cx + (radius * 0.62) * Math.cos(rad),
                      y: cy + (radius * 0.62) * Math.sin(rad)
                    };
                  })();
                  const percentValue = Math.round((seg.value / full) * 100);
                  const isFull = angle >= 359.99;
                  const path = isFull ? (
                    <circle key={`slice-${idx}`} cx={cx} cy={cy} r={radius} fill={seg.color} />
                  ) : (
                    <path key={`slice-${idx}`} d={describeSlice(startAngle, endAngle)} fill={seg.color} />
                  );
                  const label = (
                    <text
                      key={`label-${idx}`}
                      x={labelPoint.x}
                      y={labelPoint.y}
                      textAnchor="middle"
                      dominantBaseline="middle"
                      className="fill-white text-[10px]"
                    >
                      {percentValue}%
                    </text>
                  );
                  startAngle = endAngle;
                  return [path, label];
                });
              })()}
              {totalCount === 0 && (
                <circle r="80" cx="100" cy="100" fill="#e2e8f0" />
              )}
              <text x="100" y="106" textAnchor="middle" className="fill-slate-600 text-[12px]">
                {totalCount} 条
              </text>
            </svg>
          </div>
        </div>
      </Card>

      {error && (
        <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-600">
          {error}
        </div>
      )}

      <div className="grid gap-4 lg:grid-cols-2">
        {(moduleFilter === "all" || moduleFilter === "meeting") && (
        <Section
          title="会议纪要"
          items={filteredMeetings}
          link="/meeting"
          render={(item) => (
            <div className="flex items-center justify-between gap-2">
              <div>
                <div className="text-slate-700">{(item.title as string) || "未命名会议"}</div>
                <div className="text-[11px] text-slate-400">{(item.status as string) || ""}</div>
              </div>
              <Button variant="secondary" size="sm" onClick={() => openPreview("会议纪要", item)}>
                预览
              </Button>
            </div>
          )}
        />
        )}
        {(moduleFilter === "all" || moduleFilter === "weekly") && (
        <Section
          title="周报生成"
          items={filteredWeekly}
          link="/weekly"
          render={(item) => (
            <div className="flex items-center justify-between gap-2">
              <div>
                <div className="text-slate-700">{(item.title as string) || "周报"}</div>
                <div className="text-[11px] text-slate-400">{(item.status as string) || ""}</div>
              </div>
              <Button variant="secondary" size="sm" onClick={() => openPreview("周报生成", item)}>
                预览
              </Button>
            </div>
          )}
        />
        )}
        {(moduleFilter === "all" || moduleFilter === "polish") && (
        <Section
          title="学术润色"
          items={filteredPolish}
          link="/polish"
          render={(item) => (
            <div className="flex items-center justify-between gap-2">
              <div>
                <div className="text-slate-700">任务 {(item.id as number) ?? ""}</div>
                <div className="text-[11px] text-slate-400">{(item.status as string) || ""}</div>
              </div>
              <Button variant="secondary" size="sm" onClick={() => openPreview("学术润色", item)}>
                预览
              </Button>
            </div>
          )}
        />
        )}
        {(moduleFilter === "all" || moduleFilter === "document") && (
        <Section
          title="文献摘要"
          items={filteredDocs}
          link="/documents"
          render={(item) => (
            <div className="flex items-center justify-between gap-2">
              <div>
                <div className="text-slate-700">{(item.title as string) || "文档"}</div>
                <div className="text-[11px] text-slate-400">{(item.source_type as string) || ""}</div>
              </div>
              <Button variant="secondary" size="sm" onClick={() => openPreview("文献摘要", item)}>
                预览
              </Button>
            </div>
          )}
        />
        )}
        {(moduleFilter === "all" || moduleFilter === "translation") && (
        <Section
          title="多语言翻译"
          items={filteredTranslations}
          link="/translation"
          render={(item) => (
            <div className="flex items-center justify-between gap-2">
              <div>
                <div className="text-slate-700">任务 {(item.id as number) ?? ""}</div>
                <div className="text-[11px] text-slate-400">
                  {(item.source_language as string) || ""} → {(item.target_language as string) || ""}
                </div>
              </div>
              <Button variant="secondary" size="sm" onClick={() => openPreview("多语言翻译", item)}>
                预览
              </Button>
            </div>
          )}
        />
        )}
        {(moduleFilter === "all" || moduleFilter === "ppt") && (
        <Section
          title="PPT生成"
          items={filteredPpt}
          link="/ppt"
          render={(item) => (
            <div className="flex items-center justify-between gap-2">
              <div>
                <div className="text-slate-700">{(item.title as string) || "PPT"}</div>
                <div className="text-[11px] text-slate-400">{(item.status as string) || ""}</div>
              </div>
              <Button variant="secondary" size="sm" onClick={() => openPreview("PPT生成", item)}>
                预览
              </Button>
            </div>
          )}
        />
        )}
      </div>

      <Dialog open={Boolean(previewItem)} onOpenChange={(open) => (!open ? closePreview() : null)}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>{previewTitle}</DialogTitle>
            <DialogDescription>查看当前记录的详细内容</DialogDescription>
          </DialogHeader>
          <ScrollArea className="max-h-[420px] pr-4">
            <div className="grid gap-3">
              {previewItem && previewFields(previewItem).length === 0 && (
                <div className="text-xs text-slate-500">暂无可展示字段</div>
              )}
              {previewItem &&
                previewFields(previewItem).map((field) => (
                  <div key={field.label} className="rounded-md border border-slate-200 bg-slate-50 p-3 text-xs">
                    <div className="text-[11px] text-slate-500">{field.label}</div>
                    <div className="mt-1 text-slate-700 whitespace-pre-wrap">
                      {formatPreviewValue(field.value)}
                    </div>
                  </div>
                ))}
              {previewItem && (
                <details className="rounded-md border border-slate-200 bg-white p-3 text-xs">
                  <summary className="cursor-pointer text-slate-500">原始数据</summary>
                  <pre className="mt-2 whitespace-pre-wrap text-[11px] text-slate-600">
                    {JSON.stringify(previewItem, null, 2)}
                  </pre>
                </details>
              )}
            </div>
          </ScrollArea>
        </DialogContent>
      </Dialog>
    </div>
  );
}
