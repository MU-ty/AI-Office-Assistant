import type {
  TranslationTask,
  TranslationTaskList,
  TranslationTerminology
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
    return (data.data ?? data) as T;
  } catch {
    if (!response.ok) {
      throw new Error(text || "请求失败");
    }
    return text as T;
  }
};

export async function createTranslationTask(payload: {
  source_language?: string;
  target_language: string;
  input_text: string;
  domain?: string;
}): Promise<TranslationTask> {
  const response = await fetch(`${API_BASE}/api/v1/translations`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...getAuthHeaders() },
    body: JSON.stringify(payload)
  });
  return unwrap<TranslationTask>(response);
}

export async function listTranslationTasks(params: {
  skip?: number;
  limit?: number;
  status?: string;
}): Promise<TranslationTaskList> {
  const search = new URLSearchParams();
  if (params.status) search.set("status", params.status);
  if (params.skip !== undefined) search.set("skip", String(params.skip));
  if (params.limit !== undefined) search.set("limit", String(params.limit));

  const response = await fetch(`${API_BASE}/api/v1/translations?${search}`, {
    headers: { ...getAuthHeaders() }
  });
  return unwrap<TranslationTaskList>(response);
}

export async function getTranslationTask(taskId: number): Promise<TranslationTask> {
  const response = await fetch(`${API_BASE}/api/v1/translations/${taskId}`, {
    headers: { ...getAuthHeaders() }
  });
  return unwrap<TranslationTask>(response);
}

export async function listTerminology(domain?: string): Promise<TranslationTerminology[]> {
  const search = new URLSearchParams();
  if (domain) search.set("domain", domain);
  const response = await fetch(`${API_BASE}/api/v1/translations/terminology?${search}`, {
    headers: { ...getAuthHeaders() }
  });
  return unwrap<TranslationTerminology[]>(response);
}

export async function addTerminology(payload: {
  original_term: string;
  translation: string;
  domain: string;
}): Promise<TranslationTerminology> {
  const response = await fetch(`${API_BASE}/api/v1/translations/terminology/add`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...getAuthHeaders() },
    body: JSON.stringify(payload)
  });
  return unwrap<TranslationTerminology>(response);
}

export async function rateTranslationTask(taskId: number, rating: number, feedback?: string) {
  const response = await fetch(`${API_BASE}/api/v1/translations/${taskId}/rate`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...getAuthHeaders() },
    body: JSON.stringify({ rating, feedback })
  });
  return unwrap<TranslationTask>(response);
}

export async function exportTranslationTask(taskId: number, format: "json" | "txt" | "pdf" | "docx") {
  const response = await fetch(`${API_BASE}/api/v1/translations/${taskId}/export`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...getAuthHeaders() },
    body: JSON.stringify({ format })
  });
  return unwrap<Record<string, unknown> | string>(response);
}
