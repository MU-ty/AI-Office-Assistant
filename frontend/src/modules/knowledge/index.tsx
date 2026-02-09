"use client";

import { useEffect, useState, useMemo, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Plus, FolderPlus, Upload, FileText, Settings, Database, Trash2, Edit, Save, X, Undo, Redo, Loader2, MessageSquare, PanelRightOpen, PanelRightClose } from "lucide-react";
import {
  listKnowledgeBases,
  getDirectoryTree,
  createDirectory,
  createKnowledgeBase,
  uploadDocument,
  listKnowledge, // Legacy
  deleteKnowledge,
  deleteKnowledgeBase,
  deleteDirectory,
  getDocument,
  updateDocument
} from "./api";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import ReactMarkdown from "react-markdown";
import type { KnowledgeBase, Directory, KnowledgeItem, Document } from "@/modules/knowledge/types";
import { KnowledgeTree } from "@/components/knowledge/KnowledgeTree";
import { GlobalSearch } from "@/components/knowledge/GlobalSearch";
import { KnowledgeChat } from "@/components/knowledge/KnowledgeChat";
import { cn } from "@/lib/utils";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
    DialogFooter,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function KnowledgeModule() {
  // State
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [selectedKb, setSelectedKb] = useState<KnowledgeBase | null>(null);
  const [directories, setDirectories] = useState<Directory[]>([]);
  const [selectedDirId, setSelectedDirId] = useState<number | null>(null);
  
  const [documents, setDocuments] = useState<KnowledgeItem[]>([]);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Dialog states
  const [isCreateKbOpen, setIsCreateKbOpen] = useState(false);
  const [newKbName, setNewKbName] = useState("");
  
  const [isCreateDirOpen, setIsCreateDirOpen] = useState(false);
  const [newDirName, setNewDirName] = useState("");
  const [newDirParentId, setNewDirParentId] = useState<number | null>(null);

  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadTitle, setUploadTitle] = useState("");

  const [viewDoc, setViewDoc] = useState<Document | null>(null);
  const [isViewOpen, setIsViewOpen] = useState(false);
  
  // Chat state
  const [isChatOpen, setIsChatOpen] = useState(false);

  // Editing state
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState("");
  const [history, setHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [isSaving, setIsSaving] = useState(false);
  
  // Sync scroll state
  const [syncScroll, setSyncScroll] = useState(true);
  const editRef = useRef<HTMLTextAreaElement>(null);
  const previewRef = useRef<HTMLDivElement>(null);

  // Initial Load
  useEffect(() => {
    loadKnowledgeBases();
  }, []);

  // Load Directories when KB selected
  useEffect(() => {
    if (selectedKb) {
      loadDirectories(parseInt(selectedKb.id));
      // Reset selected dir when KB changes
      if (selectedDirId !== null) {
          setSelectedDirId(null);
      } else {
          loadDocuments(selectedKb.id, null);
      }
    } else {
      setDirectories([]);
      setDocuments([]);
    }
  }, [selectedKb]);

  // Reload documents when directory changes
  useEffect(() => {
      if (selectedKb) {
          loadDocuments(selectedKb.id, selectedDirId);
      }
  }, [selectedDirId]);

  const loadKnowledgeBases = async () => {
    try {
      const data = await listKnowledgeBases();
      setKnowledgeBases(data || []);
      if (data?.length && !selectedKb) {
        setSelectedKb(data[0]);
      }
    } catch (err) {
      setError("获取知识库列表失败");
    }
  };

  const loadDirectories = async (kbId: number) => {
    try {
      const tree = await getDirectoryTree(kbId);
      setDirectories(tree);
    } catch (err) {
      console.error("加载目录失败", err);
    }
  };

  const loadDocuments = async (kbId: string, dirId: number | null) => {
    setLoading(true);
    try {
      const items = await listKnowledge(kbId, 1, 20, undefined, dirId); 
      setDocuments(items || []);
    } catch (err) {
      setError("获取文档列表失败");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateKb = async () => {
      if (!newKbName.trim()) return;
      try {
          const kb = await createKnowledgeBase({ name: newKbName, description: "Created via Web UI" });
          setKnowledgeBases([...knowledgeBases, kb]);
          setSelectedKb(kb);
          setIsCreateKbOpen(false);
          setNewKbName("");
      } catch (err) {
          setError("创建知识库失败");
      }
  };

  const handleCreateDir = async () => {
      if (!newDirName.trim() || !selectedKb) return;
      try {
          await createDirectory(newDirName, parseInt(selectedKb.id), newDirParentId || undefined);
          await loadDirectories(parseInt(selectedKb.id));
          setIsCreateDirOpen(false);
          setNewDirName("");
      } catch (err) {
          setError("创建目录失败");
      }
  };

  const handleUpload = async () => {
      if (!uploadFile || !selectedKb) return;
      setLoading(true);
      try {
        await uploadDocument(
            uploadFile, 
            uploadTitle || uploadFile.name, 
            parseInt(selectedKb.id), 
            selectedDirId || undefined
        );
        setIsUploadOpen(false);
        setUploadFile(null);
        setUploadTitle("");
        await loadDocuments(selectedKb.id, selectedDirId || null); // Refresh list
      } catch (err) {
          setError("上传失败: " + err);
      } finally {
          setLoading(false);
      }
  };

  const handleDeleteKb = async (e: React.MouseEvent, kbId: string) => {
      e.stopPropagation();
      if (!window.confirm("确定要删除这个知识库吗？所有目录和文档都将被删除！")) return;
      try {
          await deleteKnowledgeBase(parseInt(kbId));
          // Refresh list
          const newList = knowledgeBases.filter(kb => kb.id !== kbId);
          setKnowledgeBases(newList);
          if (selectedKb?.id === kbId) {
              setSelectedKb(newList[0] || null);
          }
      } catch (err) {
          setError("删除知识库失败: " + err);
      }
  };

  const handleDeleteDir = async (dirId: number) => {
      if (!window.confirm("确定要删除这个目录吗？目录下的所有文档都将被删除！")) return;
      try {
          await deleteDirectory(dirId);
          if (selectedKb) {
              await loadDirectories(parseInt(selectedKb.id));
              if (selectedDirId === dirId) {
                  setSelectedDirId(null);
              }
          }
      } catch (err) {
          setError("删除目录失败: " + err);
      }
  };

  const handleDeleteDoc = async (e: React.MouseEvent, docId: string) => {
      e.stopPropagation();
      if (!window.confirm("确定要删除这个文档吗？")) return;
      try {
          await deleteKnowledge(docId);
          // Refresh list
          if (selectedKb) {
             await loadDocuments(selectedKb.id, selectedDirId || null);
          }
      } catch (err) {
          setError("删除文档失败: " + err);
      }
  };

  const handleViewDoc = async (docId: string) => {
      try {
          const doc = await getDocument(docId);
          setViewDoc(doc);
          setIsViewOpen(true);
          // Reset edit state
          setIsEditing(false);
          setEditContent(doc.content || "");
          setHistory([doc.content || ""]);
          setHistoryIndex(0);
      } catch (err) {
          setError("获取文档内容失败: " + err);
      }
  };

  const handleEnterEditMode = () => {
      setIsEditing(true);
      const content = viewDoc?.content || "";
      setEditContent(content);
      setHistory([content]);
      setHistoryIndex(0);
  };

  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      const newContent = e.target.value;
      setEditContent(newContent);
      
      // Simple history management: add to history if length changed significantly or paused?
      // For simplicity in this demo: we push to history on every change but we need to be careful.
      // Better approach for manual undo/redo buttons:
      // We'll use a debounce effect or just let user type. 
      // But to make "Undo" button active, we need history.
      // Let's implement a simple "commit" to history on pause (debounce).
  };
  
  // Use effect for debounced history update
  useEffect(() => {
      if (!isEditing) return;
      const timer = setTimeout(() => {
          if (editContent !== history[historyIndex]) {
              const newHistory = history.slice(0, historyIndex + 1);
              newHistory.push(editContent);
              setHistory(newHistory);
              setHistoryIndex(newHistory.length - 1);
          }
      }, 800); // 800ms debounce
      return () => clearTimeout(timer);
  }, [editContent, isEditing]); // Note: excluding history/historyIndex to avoid loops, but need to be careful

  const handleUndo = () => {
      if (historyIndex > 0) {
          const newIndex = historyIndex - 1;
          setHistoryIndex(newIndex);
          setEditContent(history[newIndex]);
      }
  };

  const handleRedo = () => {
      if (historyIndex < history.length - 1) {
          const newIndex = historyIndex + 1;
          setHistoryIndex(newIndex);
          setEditContent(history[newIndex]);
      }
  };

  const handleSave = async () => {
      if (!viewDoc) return;
      setIsSaving(true);
      try {
          await updateDocument(viewDoc.id, { content: editContent });
          // Update local view
          setViewDoc({ ...viewDoc, content: editContent });
          setIsEditing(false);
          // Refresh list to update updated_at etc if needed
          if (selectedKb) {
             loadDocuments(selectedKb.id, selectedDirId || null);
          }
      } catch (err) {
          setError("保存失败: " + err);
      } finally {
          setIsSaving(false);
      }
  };

  const handleCancelEdit = () => {
      setIsEditing(false);
      setEditContent(viewDoc?.content || "");
  };

  // Handle sync scrolling
  const handleScroll = (e: React.UIEvent<HTMLElement>, source: 'edit' | 'preview') => {
      if (!syncScroll) return;

      const target = e.currentTarget;
      const percentage = target.scrollTop / (target.scrollHeight - target.clientHeight);

      if (source === 'edit' && previewRef.current) {
          previewRef.current.scrollTop = percentage * (previewRef.current.scrollHeight - previewRef.current.clientHeight);
      } else if (source === 'preview' && editRef.current) {
          editRef.current.scrollTop = percentage * (editRef.current.scrollHeight - editRef.current.clientHeight);
      }
  };

  // Markdown components configuration
  const markdownComponents = {
      h1: ({...props}: any) => <h1 className="text-3xl font-bold mb-6 text-slate-900" {...props} />,
      h2: ({...props}: any) => <h2 className="text-2xl font-bold mb-4 mt-8 text-slate-800 border-b pb-2 border-slate-100" {...props} />,
      h3: ({...props}: any) => <h3 className="text-xl font-semibold mb-3 mt-6 text-slate-800" {...props} />,
      h4: ({...props}: any) => <h4 className="text-lg font-semibold mb-2 mt-4 text-slate-800" {...props} />,
      p: ({...props}: any) => <p className="mb-4 leading-7 text-slate-600" {...props} />,
      ul: ({...props}: any) => <ul className="list-disc list-inside mb-4 space-y-1 text-slate-600" {...props} />,
      ol: ({...props}: any) => <ol className="list-decimal list-inside mb-4 space-y-1 text-slate-600" {...props} />,
      li: ({...props}: any) => <li className="ml-2" {...props} />,
      blockquote: ({...props}: any) => <blockquote className="border-l-4 border-blue-200 pl-4 py-1 italic my-4 text-slate-500 bg-blue-50/50 rounded-r" {...props} />,
      code: ({className, children, ...props}: any) => {
          const match = /language-(\w+)/.exec(className || '');
          const isInline = !match && !String(children).includes('\n');
          return isInline ? (
              <code className="bg-slate-100 text-pink-500 rounded px-1.5 py-0.5 text-sm font-mono" {...props}>{children}</code>
          ) : (
              <code className="block bg-slate-900 text-slate-50 p-4 rounded-lg text-sm font-mono overflow-x-auto my-4" {...props}>{children}</code>
          );
      },
      pre: ({...props}: any) => <pre className="not-prose" {...props} />,
      a: ({...props}: any) => <a className="text-blue-600 hover:underline cursor-pointer" target="_blank" rel="noopener noreferrer" {...props} />,
      table: ({...props}: any) => <div className="overflow-x-auto my-6"><table className="min-w-full border-collapse border border-slate-200" {...props} /></div>,
      th: ({...props}: any) => <th className="border border-slate-200 bg-slate-50 px-4 py-2 text-left font-semibold text-slate-700" {...props} />,
      td: ({...props}: any) => <td className="border border-slate-200 px-4 py-2 text-slate-600" {...props} />,
      hr: ({...props}: any) => <hr className="my-8 border-slate-200" {...props} />,
      img: ({...props}: any) => <img className="rounded-lg border border-slate-200 shadow-sm max-w-full my-4" {...props} alt={props.alt || ''} />,
  };

  return (
    <div className="flex h-full w-full gap-0 overflow-hidden bg-slate-50/50">
      {/* Sidebar */}
      <div className="w-64 shrink-0 flex flex-col border-r border-slate-200 bg-white">
        {/* KB Selector */}
        <div className="p-4 border-b border-slate-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-slate-800 flex items-center gap-2">
              <Database className="w-4 h-4 text-blue-600" />
              知识库
            </h2>
            <Dialog open={isCreateKbOpen} onOpenChange={setIsCreateKbOpen}>
                <DialogTrigger asChild>
                    <Button variant="ghost" size="icon" className="h-6 w-6">
                        <Plus className="w-4 h-4" />
                    </Button>
                </DialogTrigger>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>新建知识库</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-4 py-4">
                        <div className="space-y-2">
                            <Label>名称</Label>
                            <Input value={newKbName} onChange={e => setNewKbName(e.target.value)} placeholder="例如：产品文档" />
                        </div>
                    </div>
                    <DialogFooter>
                        <Button onClick={handleCreateKb}>创建</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
          </div>
          
          <div className="space-y-1">
            {knowledgeBases.map(kb => (
              <div
                key={kb.id}
                onClick={() => setSelectedKb(kb)}
                className={cn(
                  "px-3 py-2 rounded-md text-sm cursor-pointer transition-colors flex items-center justify-between group",
                  selectedKb?.id === kb.id ? "bg-blue-50 text-blue-700 font-medium" : "text-slate-600 hover:bg-slate-100"
                )}
              >
                <span className="truncate">{kb.name}</span>
                <div className="flex items-center gap-2">
                    {selectedKb?.id === kb.id && <div className="w-1.5 h-1.5 rounded-full bg-blue-500" />}
                    <div 
                        className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-100 hover:text-red-600 rounded transition-all"
                        onClick={(e) => handleDeleteKb(e, kb.id)}
                        title="删除知识库"
                    >
                        <Trash2 className="w-3 h-3" />
                    </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Directory Tree */}
        <div className="flex-1 overflow-hidden flex flex-col">
            <div className="p-3 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
                <span className="text-xs font-medium text-slate-500">目录结构</span>
                <Button 
                    variant="ghost" 
                    size="icon" 
                    className="h-5 w-5"
                    onClick={() => {
                        setNewDirParentId(selectedDirId);
                        setIsCreateDirOpen(true);
                    }}
                    disabled={!selectedKb}
                >
                    <FolderPlus className="w-3 h-3" />
                </Button>
            </div>
            <ScrollArea className="flex-1 p-2">
                {selectedKb ? (
                    <KnowledgeTree 
                        directories={directories}
                        selectedDirId={selectedDirId}
                        onSelectDirectory={setSelectedDirId}
                        onCreateDirectory={(parentId) => {
                             setNewDirParentId(parentId);
                             setIsCreateDirOpen(true);
                        }}
                        onDeleteDirectory={handleDeleteDir}
                    />
                ) : (
                    <div className="p-4 text-center text-xs text-slate-400">请先选择知识库</div>
                )}
            </ScrollArea>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden bg-white">
        {/* Header */}
        <div className="h-16 border-b border-slate-200 px-6 flex items-center justify-between gap-4">
            <GlobalSearch 
                kbId={selectedKb ? parseInt(selectedKb.id) : undefined} 
                onSelectDocument={handleViewDoc}
            />
            
            <div className="flex items-center gap-2">
                <Button 
                    variant={isChatOpen ? "secondary" : "outline"}
                    className={cn("gap-2", isChatOpen && "bg-blue-50 text-blue-600 border-blue-200")}
                    onClick={() => setIsChatOpen(!isChatOpen)}
                    title={isChatOpen ? "关闭 AI 助手" : "打开 AI 助手"}
                >
                    <MessageSquare className="w-4 h-4" />
                    <span className="hidden sm:inline">AI 问答</span>
                    {isChatOpen ? <PanelRightClose className="w-4 h-4 ml-1 opacity-50" /> : <PanelRightOpen className="w-4 h-4 ml-1 opacity-50" />}
                </Button>
                
                <div className="w-px h-6 bg-slate-200 mx-1" />

                <Dialog open={isUploadOpen} onOpenChange={setIsUploadOpen}>
                    <DialogTrigger asChild>
                        <Button className="gap-2 bg-blue-600 hover:bg-blue-700">
                            <Upload className="w-4 h-4" />
                            上传文档
                        </Button>
                    </DialogTrigger>
                    <DialogContent>
                        <DialogHeader>
                            <DialogTitle>上传文档</DialogTitle>
                        </DialogHeader>
                        <div className="space-y-4 py-4">
                            <div className="space-y-2">
                                <Label>标题 (可选)</Label>
                                <Input value={uploadTitle} onChange={e => setUploadTitle(e.target.value)} placeholder="如果不填则使用文件名" />
                            </div>
                            <div className="space-y-2">
                                <Label>选择文件</Label>
                                <Input type="file" onChange={e => setUploadFile(e.target.files?.[0] || null)} />
                            </div>
                            <div className="space-y-2">
                                <Label className="text-xs text-slate-500">
                                    上传位置: {selectedKb?.name} / {selectedDirId ? "当前选中目录" : "根目录"}
                                </Label>
                            </div>
                        </div>
                        <DialogFooter>
                            <Button onClick={handleUpload} disabled={loading || !uploadFile}>
                                {loading ? "上传中..." : "开始上传"}
                            </Button>
                        </DialogFooter>
                    </DialogContent>
                </Dialog>
            </div>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-auto p-6">
            <div className="mb-4 flex items-center justify-between">
                <h3 className="text-lg font-medium text-slate-800">
                    {selectedDirId ? "目录文档" : "所有文档"}
                </h3>
                <Badge variant="outline" className="text-slate-500">
                    {documents.length} 个文件
                </Badge>
            </div>

            {error && (
                <div className="mb-4 p-3 bg-red-50 text-red-600 text-sm rounded-md border border-red-100">
                    {error}
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {documents.map((doc) => (
                    <Card 
                        key={doc.id} 
                        className="p-4 hover:shadow-md transition-shadow cursor-pointer group relative"
                        onClick={() => handleViewDoc(doc.id)}
                    >
                        <div className="flex items-start justify-between mb-2">
                            <div className="p-2 bg-blue-50 rounded-lg text-blue-600">
                                <FileText className="w-5 h-5" />
                            </div>
                            <Badge variant="secondary" className="text-[10px]">
                                {doc.file_type || "DOC"}
                            </Badge>
                        </div>
                        <h4 className="font-medium text-slate-800 text-sm line-clamp-1 mb-1" title={doc.title}>
                            {doc.title || doc.source || "未命名文档"}
                        </h4>
                        <p className="text-xs text-slate-500 mb-3">
                            {doc.created_at ? new Date(doc.created_at).toLocaleDateString() : "-"}
                        </p>
                        
                        <div className="flex items-center justify-between text-xs text-slate-400">
                             <span>{doc.parse_status || "Ready"}</span>
                             <div 
                                className="p-1 hover:bg-red-50 hover:text-red-500 rounded cursor-pointer transition-colors opacity-0 group-hover:opacity-100"
                                onClick={(e) => handleDeleteDoc(e, doc.id)}
                                title="删除文档"
                             >
                                <Trash2 className="w-3 h-3" />
                             </div>
                        </div>
                    </Card>
                ))}
                
                {documents.length === 0 && !loading && (
                    <div className="col-span-full py-12 text-center border-2 border-dashed border-slate-100 rounded-xl">
                        <div className="mx-auto w-12 h-12 bg-slate-50 rounded-full flex items-center justify-center mb-3">
                            <FileText className="w-6 h-6 text-slate-300" />
                        </div>
                        <h3 className="text-slate-900 font-medium mb-1">暂无文档</h3>
                        <p className="text-slate-500 text-sm">点击右上角上传按钮添加新文档</p>
                    </div>
                )}
            </div>
        </div>
      </div>

      {/* Chat Panel */}
      {isChatOpen && (
        <KnowledgeChat 
            kbId={selectedKb ? parseInt(selectedKb.id) : undefined}
            kbName={selectedKb?.name}
            onClose={() => setIsChatOpen(false)}
            onViewDocument={handleViewDoc}
        />
      )}

      {/* Create Directory Dialog */}
      <Dialog open={isCreateDirOpen} onOpenChange={setIsCreateDirOpen}>
        <DialogContent>
            <DialogHeader>
                <DialogTitle>新建目录</DialogTitle>
            </DialogHeader>
            <div className="py-4">
                <Label>目录名称</Label>
                <Input value={newDirName} onChange={e => setNewDirName(e.target.value)} className="mt-2" />
            </div>
            <DialogFooter>
                <Button onClick={handleCreateDir}>创建</Button>
            </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* View Document Dialog */}
      <Dialog open={isViewOpen} onOpenChange={(open) => {
          if (!open && isEditing) {
              if (!window.confirm("正在编辑中，确定要关闭吗？未保存的内容将丢失。")) return;
          }
          setIsViewOpen(open);
      }}>
        <DialogContent className="max-w-[95vw] w-[95vw] h-[95vh] flex flex-col p-0 gap-0">
            <DialogHeader className="flex flex-row items-center justify-between space-y-0 p-4 border-b border-slate-200">
                <DialogTitle className="text-xl font-semibold truncate max-w-[600px] flex items-center gap-2" title={viewDoc?.title}>
                    <FileText className="w-5 h-5 text-blue-600" />
                    {viewDoc?.title}
                </DialogTitle>
                <div className="flex items-center gap-2 pr-8">
                    {isEditing ? (
                        <>
                            <div className="flex items-center bg-slate-100 rounded-lg p-1 mr-2">
                                <Button variant="ghost" size="icon" onClick={handleUndo} disabled={historyIndex <= 0} title="撤销" className="h-7 w-7">
                                    <Undo className="w-4 h-4" />
                                </Button>
                                <Button variant="ghost" size="icon" onClick={handleRedo} disabled={historyIndex >= history.length - 1} title="重做" className="h-7 w-7">
                                    <Redo className="w-4 h-4" />
                                </Button>
                            </div>
                            <Button variant="default" size="sm" onClick={handleSave} disabled={isSaving} className="gap-1 bg-blue-600 hover:bg-blue-700">
                                {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                                保存
                            </Button>
                            <Button variant="ghost" size="sm" onClick={handleCancelEdit} disabled={isSaving} className="gap-1 text-slate-500">
                                <X className="w-4 h-4" />
                                取消
                            </Button>
                        </>
                    ) : (
                        <Button variant="outline" size="sm" onClick={handleEnterEditMode} className="gap-1">
                            <Edit className="w-4 h-4" />
                            编辑
                        </Button>
                    )}
                </div>
            </DialogHeader>
            <div className="flex-1 overflow-hidden bg-slate-50 relative">
                 {isEditing ? (
                     <div className="flex h-full w-full">
                         {/* Edit Pane */}
                         <div className="flex-1 h-full border-r border-slate-200 bg-white flex flex-col">
                             <div className="px-4 py-2 bg-slate-50 border-b border-slate-100 text-xs font-medium text-slate-500 flex justify-between items-center h-10">
                                 <span>Markdown 编辑</span>
                                 <div className="flex items-center gap-2">
                                    <div className="flex items-center gap-1.5">
                                        <Switch 
                                            id="sync-scroll" 
                                            checked={syncScroll} 
                                            onCheckedChange={setSyncScroll}
                                            className="scale-75" 
                                        />
                                        <Label htmlFor="sync-scroll" className="cursor-pointer">同步滚动</Label>
                                    </div>
                                    <span className="w-px h-3 bg-slate-300 mx-1"></span>
                                    <span>{editContent.length} 字符</span>
                                 </div>
                             </div>
                             <Textarea 
                                ref={editRef}
                                value={editContent} 
                                onChange={handleContentChange}
                                onScroll={(e) => handleScroll(e, 'edit')}
                                className="flex-1 w-full resize-none p-4 font-mono text-sm border-0 focus-visible:ring-0 bg-white leading-relaxed"
                                placeholder="在此输入 Markdown 内容..."
                             />
                         </div>
                         {/* Preview Pane */}
                         <div className="flex-1 h-full bg-slate-50 flex flex-col overflow-hidden">
                             <div className="px-4 py-2 bg-slate-100 border-b border-slate-200 text-xs font-medium text-slate-500 h-10 flex items-center">
                                 <span>实时预览</span>
                             </div>
                             <div 
                                className="flex-1 overflow-auto p-8"
                                ref={previewRef}
                                onScroll={(e) => handleScroll(e, 'preview')}
                             >
                                <div className="prose prose-slate max-w-none dark:prose-invert">
                                    <ReactMarkdown components={markdownComponents}>{editContent}</ReactMarkdown>
                                </div>
                             </div>
                         </div>
                     </div>
                 ) : (
                     <div className="h-full w-full max-w-5xl mx-auto bg-white shadow-sm my-0 border-x border-slate-100 flex flex-col">
                         <div className="flex-1 overflow-auto p-12">
                            {viewDoc?.content ? (
                                <div className="prose prose-slate max-w-none dark:prose-invert">
                                    <ReactMarkdown components={markdownComponents}>{viewDoc.content}</ReactMarkdown>
                                </div>
                            ) : (
                                <div className="flex items-center justify-center h-full text-slate-400 flex-col gap-4">
                                    <FileText className="w-12 h-12 opacity-20" />
                                    <p>暂无内容</p>
                                </div>
                            )}
                         </div>
                     </div>
                 )}
            </div>
            {isEditing && (
                <div className="h-8 border-t border-slate-200 bg-white flex items-center justify-between px-4 text-xs text-slate-400">
                    <div className="flex gap-4">
                        <span>状态: {isSaving ? "保存中..." : "已修改"}</span>
                        <span>版本: {historyIndex + 1} / {history.length}</span>
                    </div>
                    <div>
                        Markdown 语法支持
                    </div>
                </div>
            )}
        </DialogContent>
      </Dialog>

    </div>
  );
}
