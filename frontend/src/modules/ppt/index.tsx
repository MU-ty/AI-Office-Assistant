"use client";

import { useEffect, useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { createPPTProject, exportPPT, generatePPTSlides, getPPTProject, importPPTProject, listPPTProjects } from "./api";
import type { PPTProject, PPTSlide } from "./types";

const toneOptions = [
  { value: "professional", label: "专业" },
  { value: "brief", label: "简洁" },
  { value: "formal", label: "正式" }
];
const themeOptions = [
  { value: "classic", label: "经典" },
  { value: "dark", label: "暗色" },
  { value: "ocean", label: "海蓝" },
  { value: "forest", label: "森林" },
  { value: "custom", label: "自定义" }
];

export default function PPTModule() {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [content, setContent] = useState("");
  const [tone, setTone] = useState("professional");
  const [theme, setTheme] = useState("classic");
  const [themePalette, setThemePalette] = useState<{ bg: string; text: string }>({
    bg: "#ffffff",
    text: "#1e293b"
  });
  const [importFile, setImportFile] = useState<File | null>(null);
  const [projects, setProjects] = useState<PPTProject[]>([]);
  const [selectedProject, setSelectedProject] = useState<PPTProject | null>(null);
  const [slides, setSlides] = useState<PPTSlide[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadProjects = async () => {
    try {
      const data = await listPPTProjects({ skip: 0, limit: 20 });
      setProjects(data.items || []);
      if (data.items?.length && !selectedProject) {
        await handleSelectProject(data.items[0].id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "获取项目失败");
    }
  };

  useEffect(() => {
    loadProjects();
  }, []);

  const handleSelectProject = async (projectId: number) => {
    try {
      const data = await getPPTProject(projectId);
      setSelectedProject(data);
      setSlides(data.slides || []);
      setTitle(data.title || "");
      setDescription(data.description || "");
      setTheme(data.theme || "classic");
      if (data.theme_palette?.bg || data.theme_palette?.text) {
        setThemePalette({
          bg: data.theme_palette?.bg || "#ffffff",
          text: data.theme_palette?.text || "#1e293b"
        });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "获取项目失败");
    }
  };

  const handleCreate = async () => {
    if (!title.trim() || !content.trim()) {
      setError("请输入标题与内容");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const project = await createPPTProject({
        title: title.trim(),
        description: description.trim() || undefined,
        source_content: content.trim(),
        theme,
        theme_palette: theme === "custom" ? themePalette : null
      });
      setSelectedProject(project);
      await loadProjects();
    } catch (err) {
      setError(err instanceof Error ? err.message : "创建失败");
    } finally {
      setLoading(false);
    }
  };

  const handleImport = async () => {
    if (!title.trim()) {
      setError("请输入标题");
      return;
    }
    if (!importFile) {
      setError("请选择要导入的文件");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const project = await importPPTProject({
        title: title.trim(),
        description: description.trim() || undefined,
        theme,
        theme_palette: theme === "custom" ? themePalette : null,
        file: importFile
      });
      setSelectedProject(project);
      await loadProjects();
    } catch (err) {
      setError(err instanceof Error ? err.message : "导入失败");
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    if (!selectedProject) return;
    setLoading(true);
    setError(null);
    try {
      const project = await generatePPTSlides(
        selectedProject.id,
        tone,
        theme,
        theme === "custom" ? themePalette : null
      );
      setSelectedProject(project);
      setSlides(project.slides || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "生成失败");
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    if (!selectedProject) return;
    try {
      const data = await exportPPT(selectedProject.id);
      const path = (data as { path: string }).path;
      const link = document.createElement("a");
      link.href = `${process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8003"}${path}`;
      link.download = `ppt-${selectedProject.id}.pptx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      setError(err instanceof Error ? err.message : "导出失败");
    }
  };

  const slideCount = useMemo(() => slides.length, [slides]);

  return (
    <div className="flex h-full w-full gap-0 overflow-hidden rounded-lg border border-slate-200 bg-white shadow-lg">
      <div className="w-80 shrink-0 border-r border-slate-200 bg-slate-50">
        <div className="border-b border-slate-200 bg-white p-6">
          <h2 className="text-lg font-semibold text-slate-800">PPT生成</h2>
          <p className="mt-1 text-xs text-slate-500">快速整理内容并生成演示提纲</p>
        </div>
        <div className="p-6 space-y-4">
          <div className="space-y-2">
            <label className="text-xs text-slate-500">标题</label>
            <input
              className="w-full rounded-md border border-slate-200 px-2 py-2 text-sm"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="输入项目标题"
            />
          </div>
          <div className="space-y-2">
            <label className="text-xs text-slate-500">描述</label>
            <input
              className="w-full rounded-md border border-slate-200 px-2 py-2 text-sm"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="可选"
            />
          </div>
          <div className="space-y-2">
            <label className="text-xs text-slate-500">导入文件</label>
            <input
              type="file"
              accept=".md,.markdown,.docx,.pdf"
              onChange={(e) => setImportFile(e.target.files?.[0] || null)}
              className="w-full rounded-md border border-slate-200 px-2 py-2 text-xs"
            />
            <p className="text-[11px] text-slate-400">支持 Markdown / Word / PDF</p>
          </div>
          <div className="space-y-2">
            <label className="text-xs text-slate-500">风格</label>
            <select
              className="w-full rounded-md border border-slate-200 px-2 py-2 text-sm"
              value={tone}
              onChange={(e) => setTone(e.target.value)}
            >
              {toneOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          <div className="space-y-2">
            <label className="text-xs text-slate-500">模板主题</label>
            <div className="grid grid-cols-2 gap-2">
              {themeOptions.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => setTheme(option.value)}
                  className={`rounded-md border px-3 py-2 text-xs ${
                    theme === option.value
                      ? "border-blue-500 bg-blue-50 text-blue-600"
                      : "border-slate-200 bg-white text-slate-600"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span>{option.label}</span>
                    <span className="flex gap-1">
                      <span
                        className="h-3 w-3 rounded-full border"
                        style={{
                          background:
                            option.value === "dark"
                              ? "#0f172a"
                              : option.value === "ocean"
                              ? "#e2f0ff"
                              : option.value === "forest"
                              ? "#e8f5e9"
                              : option.value === "custom"
                              ? themePalette.bg
                              : "#ffffff"
                        }}
                      />
                      <span
                        className="h-3 w-3 rounded-full border"
                        style={{
                          background:
                            option.value === "dark"
                              ? "#f8fafc"
                              : option.value === "ocean"
                              ? "#0f172a"
                              : option.value === "forest"
                              ? "#1b5e20"
                              : option.value === "custom"
                              ? themePalette.text
                              : "#1e293b"
                        }}
                      />
                    </span>
                  </div>
                </button>
              ))}
            </div>
            {theme === "custom" && (
              <div className="grid grid-cols-2 gap-2">
                <label className="flex items-center justify-between rounded-md border border-slate-200 bg-white px-2 py-2 text-xs">
                  背景色
                  <input
                    type="color"
                    value={themePalette.bg}
                    onChange={(e) =>
                      setThemePalette((prev) => ({ ...prev, bg: e.target.value }))
                    }
                  />
                </label>
                <label className="flex items-center justify-between rounded-md border border-slate-200 bg-white px-2 py-2 text-xs">
                  文字色
                  <input
                    type="color"
                    value={themePalette.text}
                    onChange={(e) =>
                      setThemePalette((prev) => ({ ...prev, text: e.target.value }))
                    }
                  />
                </label>
              </div>
            )}
          </div>
          <Button onClick={handleCreate} disabled={loading} className="w-full">
            {loading ? "处理中..." : "创建项目"}
          </Button>
          <Button onClick={handleImport} disabled={loading} className="w-full" variant="secondary">
            {loading ? "处理中..." : "导入内容"}
          </Button>
          <Button
            variant="secondary"
            onClick={handleGenerate}
            disabled={!selectedProject || loading}
            className="w-full"
          >
            生成大纲
          </Button>
          <Button
            variant="secondary"
            onClick={handleExport}
            disabled={!selectedProject || slideCount === 0}
            className="w-full"
          >
            导出 PPTX
          </Button>
        </div>
        <div className="px-6 pb-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-slate-700">历史项目</h3>
            <Badge variant="secondary" className="text-xs">
              {projects.length} 条
            </Badge>
          </div>
          <ScrollArea className="h-[300px]">
            <div className="space-y-3">
              {projects.map((project) => (
                <Card
                  key={project.id}
                  className={`cursor-pointer p-3 text-xs ${
                    selectedProject?.id === project.id ? "border-blue-500" : ""
                  }`}
                  onClick={() => handleSelectProject(project.id)}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-slate-700">{project.title}</span>
                    <Badge variant="secondary" className="text-[10px]">
                      {project.status}
                    </Badge>
                  </div>
                  <div className="mt-2 text-[11px] text-slate-400">
                    {project.created_at ? new Date(project.created_at).toLocaleString() : ""}
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

        <Card className="p-4 space-y-3">
          <h3 className="text-sm font-semibold text-slate-700">内容输入</h3>
          <textarea
            className="min-h-[240px] w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="粘贴或输入演示内容"
          />
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-700">幻灯片大纲</h3>
            <span className="text-xs text-slate-500">共 {slideCount} 页</span>
          </div>
          <div className="mt-4 space-y-3">
            {slides.length === 0 && (
              <div className="text-xs text-slate-500">尚未生成大纲</div>
            )}
            {slides.map((slide, index) => (
              <div key={`${slide.title}-${index}`} className="rounded-md border border-slate-200 bg-slate-50 p-3 text-xs">
                <div className="font-medium text-slate-700">
                  {index + 1}. {slide.title}
                </div>
                <ul className="mt-2 list-disc space-y-1 pl-4 text-slate-600">
                  {slide.bullets.map((bullet, idx) => (
                    <li key={`${index}-${idx}`}>{bullet}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
