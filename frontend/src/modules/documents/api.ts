import type { DocumentItem, DocumentSummary } from "./types";

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
    return (data.data ?? data) as T;
  } catch {
    if (!response.ok) {
      throw new Error(text || "请求失败");
    }
    return text as T;
  }
};

export async function uploadDocumentFile(title: string, file: File): Promise<DocumentItem> {
  const formData = new FormData();
  formData.append("title", title);
  formData.append("file", file);
  const response = await fetch(`${API_BASE}/api/v1/documents/`, {
    method: "POST",
    headers: { ...getAuthHeaders() },
    body: formData
  });
  return unwrap<DocumentItem>(response);
}

export async function uploadDocumentText(title: string, content: string): Promise<DocumentItem> {
  const response = await fetch(`${API_BASE}/api/v1/documents/text`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...getAuthHeaders() },
    body: JSON.stringify({ title, content })
  });
  return unwrap<DocumentItem>(response);
}

export async function uploadDocumentUrl(title: string, url: string): Promise<DocumentItem> {
  const response = await fetch(`${API_BASE}/api/v1/documents/url`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...getAuthHeaders() },
    body: JSON.stringify({ title, url })
  });
  return unwrap<DocumentItem>(response);
}

export async function listDocuments(): Promise<DocumentItem[]> {
  const response = await fetch(`${API_BASE}/api/v1/documents/`, {
    headers: { ...getAuthHeaders() }
  });
  return unwrap<DocumentItem[]>(response);
}

export async function getDocument(docId: number): Promise<DocumentItem> {
  const response = await fetch(`${API_BASE}/api/v1/documents/${docId}`, {
    headers: { ...getAuthHeaders() }
  });
  return unwrap<DocumentItem>(response);
}

export async function summarizeDocument(
  docId: number,
  summary_level: "one_liner" | "paragraph" | "full"
): Promise<DocumentSummary> {
  const response = await fetch(`${API_BASE}/api/v1/documents/${docId}/summarize`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...getAuthHeaders() },
    body: JSON.stringify({ summary_level })
  });
  return unwrap<DocumentSummary>(response);
}
