"use client";

import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { listKnowledgeBases } from "@/modules/knowledge/api";
import type { KnowledgeBase } from "@/modules/knowledge/types";

export default function KnowledgeBaseSelector({
  value,
  onChange,
  title = "引用知识库"
}: {
  value: string[];
  onChange: (ids: string[]) => void;
  title?: string;
}) {
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await listKnowledgeBases();
        setKnowledgeBases(data || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : "获取知识库失败");
      }
    };
    load();
  }, []);

  const toggle = (id: string) => {
    if (value.includes(id)) {
      onChange(value.filter((item) => item !== id));
    } else {
      onChange([...value, id]);
    }
  };

  return (
    <Card className="p-4 space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-700">{title}</h3>
        <Badge variant="secondary" className="text-xs">
          {value.length} 已选
        </Badge>
      </div>
      {error && (
        <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-600">
          {error}
        </div>
      )}
      <ScrollArea className="h-40">
        <div className="space-y-2">
          {knowledgeBases.map((kb) => (
            <label
              key={kb.id}
              className="flex items-center gap-2 rounded-md border border-slate-200 bg-white px-2 py-2 text-xs"
            >
              <input
                type="checkbox"
                checked={value.includes(kb.id)}
                onChange={() => toggle(kb.id)}
              />
              <div className="flex-1">
                <p className="font-medium text-slate-700">{kb.name}</p>
                <p className="text-[11px] text-slate-400 line-clamp-1">
                  {kb.description || "暂无描述"}
                </p>
              </div>
            </label>
          ))}
          {!knowledgeBases.length && (
            <div className="rounded-md border border-dashed border-slate-200 p-3 text-center text-xs text-slate-400">
              暂无知识库
            </div>
          )}
        </div>
      </ScrollArea>
    </Card>
  );
}
