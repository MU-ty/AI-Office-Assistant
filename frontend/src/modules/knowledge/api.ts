import type {
  KnowledgeBase,
  KnowledgeItem,
  KnowledgeSearchChunk,
  Directory,
  Tag,
  SearchResult,
  Document
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8003";

const getAuthHeaders = () => {
  if (typeof window === "undefined") return {} as Record<string, string>;
  const token = localStorage.getItem("access_token");
  if (!token) return {} as Record<string, string>;
  return { Authorization: `Bearer ${token}` };
};

const unwrap = async <T>(response: Response): Promise<T> => {
  const text = await response.text();
  try {
    const data = JSON.parse(text);
    if (!response.ok) {
      throw new Error(data.detail || data.message || "请求失败");
    }
    const payload = data.data ?? data;
    if (payload && typeof payload === "object" && "data" in payload) {
      return payload.data as T;
    }
    return payload as T;
  } catch {
    if (!response.ok) {
      throw new Error(text || "请求失败");
    }
    return text as T;
  }
};

// --- Knowledge Base ---

export async function listKnowledgeBases(): Promise<KnowledgeBase[]> {
  // 优先使用新 API
  try {
    const response = await fetch(`${API_BASE}/api/v1/knowledge/knowledge-bases`, {
        headers: { ...getAuthHeaders() }
    });
    return unwrap<KnowledgeBase[]>(response);
  } catch {
    // 回退到 WeKnora API
    const response = await fetch(`${API_BASE}/api/v1/weknora/knowledge-bases`, {
        headers: { ...getAuthHeaders() }
    });
    return unwrap<KnowledgeBase[]>(response);
  }
}

export async function createKnowledgeBase(
  payload: Pick<KnowledgeBase, "name" | "description"> & { is_public?: boolean }
): Promise<KnowledgeBase> {
  const response = await fetch(`${API_BASE}/api/v1/knowledge/knowledge-bases`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...getAuthHeaders() },
    body: JSON.stringify(payload)
  });
  return unwrap<KnowledgeBase>(response);
}

export async function deleteKnowledgeBase(kbId: number): Promise<void> {
  const response = await fetch(`${API_BASE}/api/v1/knowledge/knowledge-bases/${kbId}`, {
    method: "DELETE",
    headers: { ...getAuthHeaders() }
  });
  await unwrap(response);
}

// --- Directory ---

export async function getDirectoryTree(kbId: number): Promise<Directory[]> {
    const response = await fetch(`${API_BASE}/api/v1/knowledge/knowledge-bases/${kbId}/tree`, {
        headers: { ...getAuthHeaders() }
    });
    return unwrap<Directory[]>(response);
}

export async function createDirectory(name: string, kbId: number, parentId?: number): Promise<Directory> {
    const response = await fetch(`${API_BASE}/api/v1/knowledge/directories`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...getAuthHeaders() },
        body: JSON.stringify({ name, kb_id: kbId, parent_id: parentId })
    });
    return unwrap<Directory>(response);
}

export async function moveDirectory(dirId: number, newParentId: number | null, newOrder: number = 0): Promise<Directory> {
    const response = await fetch(`${API_BASE}/api/v1/knowledge/directories/${dirId}/move`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", ...getAuthHeaders() },
        body: JSON.stringify({ new_parent_id: newParentId, new_order: newOrder })
    });
    return unwrap<Directory>(response);
}

export async function deleteDirectory(dirId: number): Promise<void> {
    const response = await fetch(`${API_BASE}/api/v1/knowledge/directories/${dirId}`, {
        method: "DELETE",
        headers: { ...getAuthHeaders() }
    });
    await unwrap(response);
}

// --- Tags ---

export async function listTags(): Promise<Tag[]> {
    const response = await fetch(`${API_BASE}/api/v1/knowledge/tags`, {
        headers: { ...getAuthHeaders() }
    });
    return unwrap<Tag[]>(response);
}

export async function createTag(name: string, color?: string): Promise<Tag> {
    const response = await fetch(`${API_BASE}/api/v1/knowledge/tags`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...getAuthHeaders() },
        body: JSON.stringify({ name, color })
    });
    return unwrap<Tag>(response);
}

// --- Search ---

export async function searchDocuments(query: string, filters?: Record<string, any>, page = 1, size = 10): Promise<{total: number, items: SearchResult[]}> {
    const response = await fetch(`${API_BASE}/api/v1/search/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...getAuthHeaders() },
        body: JSON.stringify({ query, filters, page, size })
    });
    return unwrap<{total: number, items: SearchResult[]}>(response);
}

// --- Documents (Updated) ---

export async function uploadDocument(
    file: File,
    title: string,
    kbId?: number,
    dirId?: number
): Promise<Document> {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("title", title);
    if (kbId) formData.append("kb_id", String(kbId));
    if (dirId) formData.append("dir_id", String(dirId));

    const response = await fetch(`${API_BASE}/api/v1/documents/`, {
        method: "POST",
        headers: { ...getAuthHeaders() },
        body: formData
    });
    return unwrap<Document>(response);
}

export async function getDocument(docId: string | number): Promise<Document & { content?: string }> {
    const response = await fetch(`${API_BASE}/api/v1/documents/${docId}`, {
        headers: { ...getAuthHeaders() }
    });
    return unwrap<Document & { content?: string }>(response);
}

export async function updateDocument(
    docId: string | number,
    data: Partial<Document>
): Promise<Document> {
    const response = await fetch(`${API_BASE}/api/v1/documents/${docId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", ...getAuthHeaders() },
        body: JSON.stringify(data)
    });
    return unwrap<Document>(response);
}

// --- Legacy (WeKnora) ---

export async function listKnowledge(
  kbId: string,
  page = 1,
  pageSize = 20,
  tagId?: string,
  dirId?: number | null
): Promise<KnowledgeItem[]> {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
    knowledge_base_id: kbId
  });
  if (tagId) params.set("tag_id", tagId);
  if (dirId !== undefined && dirId !== null) params.set("directory_id", String(dirId));
  
  // 使用新的自建知识库 API，而不是 WeKnora
  const response = await fetch(
    `${API_BASE}/api/v1/documents?${params.toString()}`,
    {
      headers: { ...getAuthHeaders() }
    }
  );
  return unwrap<KnowledgeItem[]>(response);
}

export async function uploadKnowledgeFile(
  kbId: string,
  file: File,
  metadata?: string,
  enableMultimodel?: boolean
): Promise<KnowledgeItem> {
  const formData = new FormData();
  formData.append("file", file);
  if (metadata) formData.append("metadata", metadata);
  if (enableMultimodel !== undefined) {
    formData.append("enable_multimodel", String(enableMultimodel));
  }
  const response = await fetch(
    `${API_BASE}/api/v1/weknora/knowledge-bases/${kbId}/knowledge/file`,
    {
      method: "POST",
      headers: { ...getAuthHeaders() },
      body: formData
    }
  );
  return unwrap<KnowledgeItem>(response);
}

export async function createKnowledgeUrl(
  kbId: string,
  url: string,
  enableMultimodel?: boolean
): Promise<KnowledgeItem> {
  const response = await fetch(
    `${API_BASE}/api/v1/weknora/knowledge-bases/${kbId}/knowledge/url`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json", ...getAuthHeaders() },
      body: JSON.stringify({ url, enable_multimodel: enableMultimodel })
    }
  );
  return unwrap<KnowledgeItem>(response);
}

export async function deleteKnowledge(knowledgeId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/api/v1/documents/${knowledgeId}`, {
    method: "DELETE",
    headers: { ...getAuthHeaders() }
  });
  await unwrap(response);
}

export async function knowledgeSearch(
  query: string,
  knowledgeBaseIds: string[]
): Promise<KnowledgeSearchChunk[]> {
  // Switch to local document search API
  const response = await fetch(`${API_BASE}/api/v1/documents/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...getAuthHeaders() },
    body: JSON.stringify({ query, knowledge_base_ids: knowledgeBaseIds, limit: 20 })
  });
  return unwrap<KnowledgeSearchChunk[]>(response);
}

// --- Chat (New) ---

export interface ChatMessage {
    role: "user" | "assistant" | "system";
    content: string;
}

export interface ChatSource {
    id: number;
    title: string;
    score: number;
    content_preview: string;
}

export async function chatWithKnowledge(
    query: string,
    history: ChatMessage[],
    knowledgeBaseIds: number[],
    onToken: (token: string) => void,
    onSources: (sources: ChatSource[]) => void,
    onError: (error: string) => void,
    onComplete: () => void
) {
    try {
        const response = await fetch(`${API_BASE}/api/v1/chat/knowledge`, {
            method: "POST",
            headers: { "Content-Type": "application/json", ...getAuthHeaders() },
            body: JSON.stringify({
                query,
                history,
                knowledge_base_ids: knowledgeBaseIds,
                top_k: 5
            })
        });

        if (!response.ok) {
            throw new Error(`请求失败: ${response.statusText}`);
        }

        if (!response.body) {
            throw new Error("响应体为空");
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            
            // 处理 SSE 格式数据 (data: {...})
            // 使用更健壮的流式解析策略：累积 buffer，直到遇到 \n\n (标准 SSE) 或者尝试逐行解析
            
            // 简单策略：只要 buffer 中包含 \n，就尝试截取到 \n 的部分进行解析
            // 如果解析成功，则消费这部分 buffer；如果失败（可能是 JSON 不完整），则继续累积
            
            let boundary = buffer.indexOf('\n');
            while (boundary !== -1) {
                const line = buffer.slice(0, boundary).trim();
                buffer = buffer.slice(boundary + 1); // 移动 buffer 指针
                
                if (line.startsWith("data: ")) {
                    const jsonStr = line.slice(6);
                    try {
                        const data = JSON.parse(jsonStr);
                        if (data.type === "token") {
                            onToken(data.content);
                        } else if (data.type === "sources") {
                            onSources(data.data);
                        } else if (data.type === "error") {
                            onError(data.content);
                        }
                    } catch (e) {
                        // 如果解析失败，可能是因为数据中包含了换行符但不是结束符（虽然标准 SSE 不应该这样）
                        // 或者数据确实坏了。在这里我们选择忽略错误，继续处理下一行，
                        // 但为了防止死循环或数据丢失，我们已经消费了 buffer。
                        // 如果是 JSON 内部的换行被误判为结束符，这会导致解析失败。
                        // 幸好我们的后端是用 json.dumps(..., ensure_ascii=False) 输出的一行 JSON，
                        // 所以每行就是一个完整的事件。
                        console.error("解析 SSE 数据失败", e, line);
                    }
                }
                
                boundary = buffer.indexOf('\n');
            }
        }
        
        onComplete();

    } catch (err) {
        onError(err instanceof Error ? err.message : String(err));
        onComplete();
    }
}
