
import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, FileText, Loader2, X, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { chatWithKnowledge, ChatMessage, ChatSource } from '@/modules/knowledge/api';
import ReactMarkdown from 'react-markdown';
import { cn } from '@/lib/utils';

interface KnowledgeChatProps {
    kbId?: number;
    kbName?: string;
    onClose?: () => void;
    onViewDocument?: (docId: string) => void;
}

interface MessageItem extends ChatMessage {
    id: string;
    sources?: ChatSource[];
    isStreaming?: boolean;
    error?: string;
}

export const KnowledgeChat = ({ kbId, kbName, onClose, onViewDocument }: KnowledgeChatProps) => {
    const [input, setInput] = useState('');
    const [messages, setMessages] = useState<MessageItem[]>([
        {
            id: 'welcome',
            role: 'assistant',
            content: `你好！我是你的智能知识助手。${kbName ? `我已经准备好回答关于 **${kbName}** 的问题了。` : '请选择一个知识库开始提问，或者直接问我问题。'}`
        }
    ]);
    const [isLoading, setIsLoading] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    // Auto scroll to bottom
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim() || isLoading) return;

        const userMsg: MessageItem = {
            id: Date.now().toString(),
            role: 'user',
            content: input.trim()
        };

        const aiMsgId = (Date.now() + 1).toString();
        const aiMsg: MessageItem = {
            id: aiMsgId,
            role: 'assistant',
            content: '',
            isStreaming: true
        };

        setMessages(prev => [...prev, userMsg, aiMsg]);
        setInput('');
        setIsLoading(true);

        // Prepare history for API
        const history = messages
            .filter(m => m.role !== 'system' && !m.error)
            .map(m => ({ role: m.role, content: m.content }));

        await chatWithKnowledge(
            userMsg.content,
            history,
            kbId ? [kbId] : [],
            (token) => {
                setMessages(prev => prev.map(m => {
                    if (m.id === aiMsgId) {
                        // 如果之前是 ... 占位符，现在替换为真实内容
                        const currentContent = m.isStreaming && !m.content ? "" : m.content;
                        return { ...m, content: currentContent + token };
                    }
                    return m;
                }));
            },
            (sources) => {
                setMessages(prev => prev.map(m => {
                    if (m.id === aiMsgId) {
                        return { ...m, sources };
                    }
                    return m;
                }));
            },
            (error) => {
                setMessages(prev => prev.map(m => {
                    if (m.id === aiMsgId) {
                        return { ...m, error, isStreaming: false };
                    }
                    return m;
                }));
            },
            () => {
                setMessages(prev => prev.map(m => {
                    if (m.id === aiMsgId) {
                        return { ...m, isStreaming: false };
                    }
                    return m;
                }));
                setIsLoading(false);
            }
        );
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="flex flex-col h-full bg-white border-l border-slate-200 w-[400px] shadow-xl">
            {/* Header */}
            <div className="h-16 border-b border-slate-200 px-4 flex items-center justify-between bg-slate-50/50">
                <div className="flex items-center gap-2">
                    <div className="p-1.5 bg-blue-100 rounded-lg text-blue-600">
                        <Bot className="w-5 h-5" />
                    </div>
                    <div>
                        <h3 className="font-semibold text-slate-800">AI 助手</h3>
                        {kbName && <p className="text-xs text-slate-500 truncate max-w-[200px]">当前知识库: {kbName}</p>}
                    </div>
                </div>
                <Button variant="ghost" size="icon" onClick={onClose} className="text-slate-400 hover:text-slate-600">
                    <X className="w-5 h-5" />
                </Button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-auto p-4 space-y-6" ref={scrollRef}>
                {messages.map((msg) => (
                    <div key={msg.id} className={cn("flex gap-3", msg.role === 'user' ? "flex-row-reverse" : "")}>
                        <div className={cn(
                            "w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-1",
                            msg.role === 'user' ? "bg-slate-800 text-white" : "bg-blue-100 text-blue-600"
                        )}>
                            {msg.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                        </div>
                        
                        <div className={cn(
                            "flex flex-col gap-2 max-w-[85%]",
                            msg.role === 'user' ? "items-end" : "items-start"
                        )}>
                            <div className={cn(
                                "p-3 rounded-2xl text-sm leading-relaxed shadow-sm",
                                msg.role === 'user' 
                                    ? "bg-slate-800 text-slate-50 rounded-tr-none" 
                                    : "bg-white border border-slate-100 text-slate-700 rounded-tl-none"
                            )}>
                                {msg.error ? (
                                    <div className="flex items-center gap-2 text-red-500">
                                        <AlertCircle className="w-4 h-4" />
                                        <span>{msg.error}</span>
                                    </div>
                                ) : (
                                    <div className="prose prose-sm max-w-none dark:prose-invert">
                                        <ReactMarkdown>{msg.content || (msg.isStreaming ? '...' : '')}</ReactMarkdown>
                                    </div>
                                )}
                            </div>

                            {/* Sources */}
                            {msg.sources && msg.sources.length > 0 && (
                                <div className="w-full space-y-2">
                                    <p className="text-xs font-medium text-slate-500 ml-1">参考文档:</p>
                                    {msg.sources.map((source, idx) => (
                                        <Card 
                                            key={idx} 
                                            className="p-2.5 bg-slate-50 hover:bg-white hover:shadow-md transition-all cursor-pointer border-slate-200 group"
                                            onClick={() => onViewDocument?.(String(source.id))}
                                        >
                                            <div className="flex items-start gap-2">
                                                <div className="mt-0.5 p-1 bg-white rounded border border-slate-100 text-blue-500">
                                                    <FileText className="w-3 h-3" />
                                                </div>
                                                <div className="flex-1 min-w-0">
                                                    <h4 className="text-xs font-medium text-slate-700 truncate mb-0.5 group-hover:text-blue-600 transition-colors">
                                                        {source.title}
                                                    </h4>
                                                    <p className="text-[10px] text-slate-400 line-clamp-2 leading-relaxed">
                                                        {source.content_preview}
                                                    </p>
                                                </div>
                                                <Badge variant="secondary" className="text-[9px] h-4 px-1">
                                                    {Math.round(source.score * 100)}%
                                                </Badge>
                                            </div>
                                        </Card>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                ))}
            </div>

            {/* Input */}
            <div className="p-4 border-t border-slate-200 bg-white">
                <div className="relative">
                    <Input
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder={kbId ? "输入问题，按回车发送..." : "请先选择一个知识库"}
                        disabled={isLoading || !kbId}
                        className="pr-10 py-6 resize-none"
                    />
                    <Button 
                        size="icon" 
                        disabled={isLoading || !input.trim() || !kbId} 
                        onClick={handleSend}
                        className={cn(
                            "absolute right-2 top-1/2 -translate-y-1/2 h-8 w-8 transition-all",
                            isLoading ? "bg-slate-100 text-slate-400" : "bg-blue-600 hover:bg-blue-700"
                        )}
                    >
                        {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                    </Button>
                </div>
                {!kbId && (
                    <p className="text-xs text-orange-500 mt-2 text-center">
                        请在左侧选择一个知识库以启用问答功能
                    </p>
                )}
            </div>
        </div>
    );
};
