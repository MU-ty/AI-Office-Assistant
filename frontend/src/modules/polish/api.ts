import type { PolishIssue, PolishTask, PolishTaskList } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

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

export async function createPolishTask(payload: {
  original_text: string;
  polish_level: string;
  auto_fix_enabled: boolean;
  document_id?: number;
}): Promise<PolishTask & { issues: PolishIssue[] }> {
  const response = await fetch(`${API_BASE}/api/v1/polish`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...getAuthHeaders() },
    body: JSON.stringify(payload)
  });
  return unwrap<PolishTask & { issues: PolishIssue[] }>(response);
}

export async function listPolishTasks(params: {
  skip?: number;
  limit?: number;
  status?: string;
}): Promise<PolishTaskList> {
  const search = new URLSearchParams();
  if (params.status) search.set("status", params.status);
  if (params.skip !== undefined) search.set("skip", String(params.skip));
  if (params.limit !== undefined) search.set("limit", String(params.limit));

  const response = await fetch(`${API_BASE}/api/v1/polish?${search}`, {
    headers: { ...getAuthHeaders() }
  });
  return unwrap<PolishTaskList>(response);
}

export async function getPolishTask(
  taskId: number
): Promise<PolishTask & { issues: PolishIssue[] }> {
  const response = await fetch(`${API_BASE}/api/v1/polish/${taskId}`, {
    headers: { ...getAuthHeaders() }
  });
  return unwrap<PolishTask & { issues: PolishIssue[] }>(response);
}

export async function getPolishIssues(taskId: number, filter_type?: string) {
  const search = new URLSearchParams();
  if (filter_type) search.set("filter_type", filter_type);
  const response = await fetch(`${API_BASE}/api/v1/polish/${taskId}/issues?${search}`, {
    headers: { ...getAuthHeaders() }
  });
  return unwrap<{ issues: PolishIssue[] }>(response);
}

export async function acceptPolishIssue(taskId: number, issueId: number) {
  const response = await fetch(`${API_BASE}/api/v1/polish/${taskId}/issues/${issueId}/accept`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...getAuthHeaders() },
    body: JSON.stringify({})
  });
  return unwrap<PolishIssue>(response);
}

export async function rejectPolishIssue(taskId: number, issueId: number, reason?: string) {
  const response = await fetch(`${API_BASE}/api/v1/polish/${taskId}/issues/${issueId}/reject`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...getAuthHeaders() },
    body: JSON.stringify(reason ? { reason } : {})
  });
  return unwrap<PolishIssue>(response);
}

export async function exportPolishResult(taskId: number, format: "json" | "txt") {
  const response = await fetch(`${API_BASE}/api/v1/polish/${taskId}/export`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...getAuthHeaders() },
    body: JSON.stringify({ format })
  });
  return unwrap<Record<string, unknown> | string>(response);
}
