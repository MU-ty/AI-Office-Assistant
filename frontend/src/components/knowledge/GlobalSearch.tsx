
import React, { useState, useEffect } from 'react';
import { Search, Loader2, FileText, Calendar } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { searchDocuments } from '@/modules/knowledge/api';
import { SearchResult } from '@/modules/knowledge/types';
import { cn } from '@/lib/utils';

interface GlobalSearchProps {
    kbId?: number;
    onSelectDocument?: (docId: string) => void;
}

export const GlobalSearch = ({ kbId, onSelectDocument }: GlobalSearchProps) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  
  // Simple debounce logic if hook not exists
  useEffect(() => {
    const timer = setTimeout(() => {
        if (query.trim()) {
            handleSearch();
        } else {
            setResults([]);
            setOpen(false);
        }
    }, 500);
    return () => clearTimeout(timer);
  }, [query, kbId]); // Add kbId dependency

    // Helper to style highlights
    const formatHighlight = (html: string) => {
        if (!html) return "";
        return html
            .replace(/<em>/g, '<span class="bg-yellow-200 text-orange-900 rounded-sm px-0.5 font-medium box-decoration-clone">')
            .replace(/<\/em>/g, '</span>');
    };

    const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setOpen(true);
    try {
      const filters = kbId ? { knowledge_base_id: kbId } : undefined;
      const res = await searchDocuments(query, filters);
      setResults(res.items);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative w-full max-w-xl">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="搜索全文内容..."
          className="pl-9 bg-slate-50 border-slate-200 focus:bg-white transition-colors"
        />
        {loading && (
          <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 animate-spin text-slate-400" />
        )}
      </div>

      {open && query && (
        <div className="absolute top-full mt-2 w-full bg-white rounded-lg border border-slate-200 shadow-xl z-50 overflow-hidden">
          <ScrollArea className="h-[400px]">
            {results.length > 0 ? (
              <div className="p-2 space-y-1">
                {results.map((item) => (
                  <div
                    key={item.id}
                    className="p-3 rounded-md hover:bg-slate-50 cursor-pointer group transition-colors"
                    onClick={() => {
                        if (onSelectDocument) {
                            onSelectDocument(String(item.id));
                            setOpen(false);
                            setQuery(""); // Optional: clear query after selection
                        }
                    }}
                  >
                    <div className="flex items-start justify-between gap-2">
                        <div className="flex-1 min-w-0">
                            <h4 
                                className="text-sm font-medium text-slate-800 mb-1 truncate"
                                dangerouslySetInnerHTML={{ __html: formatHighlight(item.title_highlight || item.title) }} 
                            />
                            {item.content_highlight && item.content_highlight.length > 0 ? (
                                <p 
                                    className="text-xs text-slate-500 line-clamp-3 leading-relaxed"
                                    dangerouslySetInnerHTML={{ __html: formatHighlight(item.content_highlight.join(' ... ')) }}
                                />
                            ) : (
                                <p className="text-xs text-slate-500 line-clamp-2">
                                    {item.content.substring(0, 150)}...
                                </p>
                            )}
                        </div>
                        <Badge variant="secondary" className="text-[10px] shrink-0">
                            {Math.round(item.score * 10) / 10}
                        </Badge>
                    </div>
                    <div className="mt-2 flex items-center gap-3 text-[10px] text-slate-400">
                        <span className="flex items-center gap-1">
                            <FileText className="w-3 h-3" />
                            {item.document_type || 'Document'}
                        </span>
                        {item.created_at && (
                            <span className="flex items-center gap-1">
                                <Calendar className="w-3 h-3" />
                                {new Date(item.created_at).toLocaleDateString()}
                            </span>
                        )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-8 text-center text-sm text-slate-400">
                {!loading && "未找到相关内容"}
              </div>
            )}
          </ScrollArea>
          <div className="p-2 bg-slate-50 border-t border-slate-100 text-[10px] text-slate-400 text-center">
            按 Enter 查看更多结果
          </div>
        </div>
      )}
      
      {/* Click outside handler would be good here */}
      {open && <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />}
    </div>
  );
};
