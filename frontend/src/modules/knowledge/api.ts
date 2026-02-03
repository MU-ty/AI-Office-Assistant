import type {
  KnowledgeBase,
  KnowledgeItem,
  KnowledgeSearchChunk
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

export async function listKnowledgeBases(): Promise<KnowledgeBase[]> {
  const response = await fetch(`${API_BASE}/api/v1/weknora/knowledge-bases`, {
    headers: { ...getAuthHeaders() }
  });
  return unwrap<KnowledgeBase[]>(response);
}

export async function createKnowledgeBase(
  payload: Pick<KnowledgeBase, "name" | "description">
): Promise<KnowledgeBase> {
  const response = await fetch(`${API_BASE}/api/v1/weknora/knowledge-bases`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...getAuthHeaders() },
    body: JSON.stringify(payload)
  });
  return unwrap<KnowledgeBase>(response);
}

export async function listKnowledge(
  kbId: string,
  page = 1,
  pageSize = 20,
  tagId?: string
): Promise<KnowledgeItem[]> {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize)
  });
  if (tagId) params.set("tag_id", tagId);
  const response = await fetch(
    `${API_BASE}/api/v1/weknora/knowledge-bases/${kbId}/knowledge?${params.toString()}`,
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
  const response = await fetch(`${API_BASE}/api/v1/weknora/knowledge/${knowledgeId}`, {
    method: "DELETE",
    headers: { ...getAuthHeaders() }
  });
  await unwrap(response);
}

export async function knowledgeSearch(
  query: string,
  knowledgeBaseIds: string[]
): Promise<KnowledgeSearchChunk[]> {
  const response = await fetch(`${API_BASE}/api/v1/weknora/knowledge-search`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...getAuthHeaders() },
    body: JSON.stringify({ query, knowledge_base_ids: knowledgeBaseIds })
  });
  return unwrap<KnowledgeSearchChunk[]>(response);
}
