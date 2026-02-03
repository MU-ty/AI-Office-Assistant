"use client";

import { useEffect, useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  createKnowledgeBase,
  createKnowledgeUrl,
  deleteKnowledge,
  knowledgeSearch,
  listKnowledge,
  listKnowledgeBases,
  uploadKnowledgeFile
} from "./api";
import type { KnowledgeBase, KnowledgeItem, KnowledgeSearchChunk } from "./types";

export default function KnowledgeModule() {
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [selectedKb, setSelectedKb] = useState<KnowledgeBase | null>(null);
  const [knowledgeItems, setKnowledgeItems] = useState<KnowledgeItem[]>([]);
  const [searchResults, setSearchResults] = useState<KnowledgeSearchChunk[]>([]);
  const [kbName, setKbName] = useState("");
  const [kbDesc, setKbDesc] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [metadata, setMetadata] = useState("");
  const [enableMultimodel, setEnableMultimodel] = useState(false);
  const [url, setUrl] = useState("");
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadKnowledgeBases = async () => {
    try {
      const data = await listKnowledgeBases();
      setKnowledgeBases(data || []);
      if (data?.length && !selectedKb) {
        await handleSelectKb(data[0]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "获取知识库失败");
    }
  };

  const loadKnowledgeItems = async (kbId: string) => {
    try {
      const items = await listKnowledge(kbId);
      setKnowledgeItems(items || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "获取知识失败");
    }
  };

  useEffect(() => {
    loadKnowledgeBases();
  }, []);

  const handleSelectKb = async (kb: KnowledgeBase) => {
    setSelectedKb(kb);
    setSearchResults([]);
    await loadKnowledgeItems(kb.id);
  };

  const handleCreateKb = async () => {
    if (!kbName.trim()) {
      setError("请输入知识库名称");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const kb = await createKnowledgeBase({
        name: kbName.trim(),
        description: kbDesc.trim()
      });
      setKbName("");
      setKbDesc("");
      await loadKnowledgeBases();
      if (kb?.id) {
        await handleSelectKb(kb);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "创建失败");
    } finally {
      setLoading(false);
    }
  };

  const handleUploadFile = async () => {
    if (!selectedKb) {
      setError("请选择知识库");
      return;
    }
    if (!file) {
      setError("请选择文件");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await uploadKnowledgeFile(selectedKb.id, file, metadata || undefined, enableMultimodel);
      setFile(null);
      setMetadata("");
      await loadKnowledgeItems(selectedKb.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "上传失败");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUrl = async () => {
    if (!selectedKb) {
      setError("请选择知识库");
      return;
    }
    if (!url.trim()) {
      setError("请输入URL");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await createKnowledgeUrl(selectedKb.id, url.trim(), enableMultimodel);
      setUrl("");
      await loadKnowledgeItems(selectedKb.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "创建失败");
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!selectedKb) {
      setError("请选择知识库");
      return;
    }
    if (!query.trim()) {
      setError("请输入搜索内容");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const results = await knowledgeSearch(query.trim(), [selectedKb.id]);
      setSearchResults(results || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "搜索失败");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteKnowledge = async (knowledgeId: string) => {
    if (!selectedKb) return;
    setLoading(true);
    setError(null);
    try {
      await deleteKnowledge(knowledgeId);
      await loadKnowledgeItems(selectedKb.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "删除失败");
    } finally {
      setLoading(false);
    }
  };

  const selectedKbLabel = useMemo(() => {
    if (!selectedKb) return "未选择知识库";
    return `${selectedKb.name}${selectedKb.description ? ` · ${selectedKb.description}` : ""}`;
  }, [selectedKb]);

  return (
    <div className="flex h-full w-full gap-0 overflow-hidden rounded-lg border border-slate-200 bg-white shadow-lg">
      <div className="w-80 shrink-0 border-r border-slate-200 bg-slate-50">
        <div className="border-b border-slate-200 bg-white p-6">
          <h2 className="text-lg font-semibold text-slate-800">知识库管理</h2>
          <p className="mt-1 text-xs text-slate-500">连接 WeKnora 知识库与检索</p>
        </div>
        <div className="p-6 space-y-4">
          <div className="space-y-2">
            <label className="text-xs text-slate-500">知识库名称</label>
            <input
              className="w-full rounded-md border border-slate-200 px-2 py-2 text-sm"
              value={kbName}
              onChange={(e) => setKbName(e.target.value)}
              placeholder="例如：产品手册"
            />
          </div>
          <div className="space-y-2">
            <label className="text-xs text-slate-500">描述</label>
            <textarea
              className="h-20 w-full rounded-md border border-slate-200 px-2 py-2 text-xs"
              value={kbDesc}
              onChange={(e) => setKbDesc(e.target.value)}
              placeholder="用于区分用途，可选"
            />
          </div>
          <Button onClick={handleCreateKb} disabled={loading} className="w-full">
            {loading ? "处理中..." : "创建知识库"}
          </Button>
        </div>
        <div className="px-6 pb-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-slate-700">我的知识库</h3>
            <Badge variant="secondary" className="text-xs">
              {knowledgeBases.length} 条
            </Badge>
          </div>
          <ScrollArea className="h-[360px]">
            <div className="space-y-3">
              {knowledgeBases.map((kb) => (
                <Card
                  key={kb.id}
                  className={`cursor-pointer p-3 text-xs ${
                    selectedKb?.id === kb.id ? "border-blue-500" : "border-slate-200"
                  }`}
                  onClick={() => handleSelectKb(kb)}
                >
                  <div className="flex items-center justify-between">
                    <p className="font-semibold text-slate-700">{kb.name}</p>
                    <Badge variant="secondary">KB</Badge>
                  </div>
                  <p className="mt-1 text-[11px] text-slate-500 line-clamp-2">
                    {kb.description || "暂无描述"}
                  </p>
                </Card>
              ))}
              {!knowledgeBases.length && (
                <div className="rounded-md border border-dashed border-slate-200 p-4 text-center text-xs text-slate-400">
                  暂无知识库，请先创建
                </div>
              )}
            </div>
          </ScrollArea>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        <div className="border-b border-slate-200 bg-white p-6">
          <h2 className="text-lg font-semibold text-slate-800">知识库详情</h2>
          <p className="mt-1 text-xs text-slate-500">{selectedKbLabel}</p>
        </div>

        <div className="p-6 space-y-6">
          {error && (
            <div className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-xs text-red-600">
              {error}
            </div>
          )}

          {!selectedKb && (
            <div className="rounded-md border border-dashed border-slate-200 p-8 text-center text-sm text-slate-400">
              请选择左侧知识库后进行操作
            </div>
          )}

          {selectedKb && (
            <>
              <Card className="p-4 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-slate-700">导入知识</h3>
                  <Badge variant="secondary" className="text-xs">文件 / URL</Badge>
                </div>
                <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <label className="text-xs text-slate-500">上传文件</label>
                    <input
                      type="file"
                      accept=".pdf,.docx,.txt,.md"
                      onChange={(e) => setFile(e.target.files?.[0] || null)}
                      className="w-full rounded-md border border-slate-200 px-2 py-2 text-xs"
                    />
                    <textarea
                      className="h-16 w-full rounded-md border border-slate-200 px-2 py-2 text-xs"
                      value={metadata}
                      onChange={(e) => setMetadata(e.target.value)}
                      placeholder="metadata（JSON，可选）"
                    />
                    <label className="flex items-center gap-2 text-xs text-slate-600">
                      <input
                        type="checkbox"
                        checked={enableMultimodel}
                        onChange={(e) => setEnableMultimodel(e.target.checked)}
                      />
                      启用多模态解析
                    </label>
                    <Button onClick={handleUploadFile} disabled={loading} className="w-full">
                      {loading ? "处理中..." : "上传文件"}
                    </Button>
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs text-slate-500">URL 导入</label>
                    <input
                      className="w-full rounded-md border border-slate-200 px-2 py-2 text-sm"
                      value={url}
                      onChange={(e) => setUrl(e.target.value)}
                      placeholder="https://..."
                    />
                    <div className="h-16" />
                    <Button onClick={handleCreateUrl} disabled={loading} className="w-full">
                      {loading ? "处理中..." : "导入 URL"}
                    </Button>
                  </div>
                </div>
              </Card>

              <Card className="p-4 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-slate-700">知识检索</h3>
                  <Badge variant="secondary" className="text-xs">语义搜索</Badge>
                </div>
                <div className="flex flex-col gap-3 md:flex-row">
                  <input
                    className="flex-1 rounded-md border border-slate-200 px-3 py-2 text-sm"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="输入问题或关键字"
                  />
                  <Button onClick={handleSearch} disabled={loading} className="md:w-32">
                    {loading ? "查询中..." : "搜索"}
                  </Button>
                </div>
                {searchResults.length > 0 && (
                  <div className="space-y-3">
                    {searchResults.map((item) => (
                      <Card key={item.id} className="p-3 text-xs">
                        <div className="flex items-center justify-between">
                          <p className="font-semibold text-slate-700">
                            {item.knowledge_title || item.knowledge_filename || "搜索结果"}
                          </p>
                          <Badge variant="secondary">{item.score?.toFixed(2) ?? "-"}</Badge>
                        </div>
                        <p className="mt-2 text-slate-600 line-clamp-3">{item.content || "-"}</p>
                        <p className="mt-2 text-[11px] text-slate-400">
                          {item.chunk_type || "text"} · {item.knowledge_source || "未知来源"}
                        </p>
                      </Card>
                    ))}
                  </div>
                )}
                {searchResults.length === 0 && query && (
                  <p className="text-xs text-slate-400">暂无检索结果</p>
                )}
              </Card>

              <Card className="p-4 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-slate-700">知识列表</h3>
                  <Badge variant="secondary" className="text-xs">
                    {knowledgeItems.length} 条
                  </Badge>
                </div>
                <div className="space-y-3">
                  {knowledgeItems.map((item) => (
                    <Card key={item.id} className="p-3 text-xs">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-semibold text-slate-700">{item.title || item.source || "未命名"}</p>
                          <p className="text-[11px] text-slate-400">
                            {item.file_type || "-"} · {item.parse_status || "未知状态"}
                          </p>
                        </div>
                        <Button
                          variant="secondary"
                          size="sm"
                          disabled={loading}
                          onClick={() => handleDeleteKnowledge(item.id)}
                        >
                          删除
                        </Button>
                      </div>
                    </Card>
                  ))}
                  {!knowledgeItems.length && (
                    <div className="rounded-md border border-dashed border-slate-200 p-4 text-center text-xs text-slate-400">
                      当前知识库暂无内容
                    </div>
                  )}
                </div>
              </Card>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
