import type {
  WorkLog,
  WorkLogListResponse,
  WeeklyReport,
  WeeklyReportListResponse
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8003";

const getAuthHeaders = () => {
  if (typeof window === "undefined") return {} as Record<string, string>;
  const token = localStorage.getItem("access_token");
  if (!token) return {} as Record<string, string>;
  return { Authorization: `Bearer ${token}` };
};

export async function createWorkLog(payload: {
  work_type: string;
  task_description: string;
  hours_spent: number;
  log_date?: string;
}): Promise<WorkLog> {
  const response = await fetch(`${API_BASE}/api/v1/reports/logs`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...getAuthHeaders() },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

export async function listWorkLogs(params: {
  date_from?: string;
  date_to?: string;
  skip?: number;
  limit?: number;
}): Promise<WorkLogListResponse> {
  const search = new URLSearchParams();
  if (params.date_from) search.set("date_from", params.date_from);
  if (params.date_to) search.set("date_to", params.date_to);
  if (params.skip !== undefined) search.set("skip", String(params.skip));
  if (params.limit !== undefined) search.set("limit", String(params.limit));

  const response = await fetch(`${API_BASE}/api/v1/reports/logs?${search}`, {
    headers: { ...getAuthHeaders() }
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

export async function deleteWorkLog(logId: number) {
  const response = await fetch(`${API_BASE}/api/v1/reports/logs/${logId}`, {
    method: "DELETE",
    headers: { ...getAuthHeaders() }
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
}

export async function createWeeklyReport(payload: {
  title?: string;
  week_start_date: string;
  week_end_date: string;
}): Promise<WeeklyReport> {
  const response = await fetch(`${API_BASE}/api/v1/reports`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...getAuthHeaders() },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

export async function listWeeklyReports(params: {
  status?: string;
  skip?: number;
  limit?: number;
}): Promise<WeeklyReportListResponse> {
  const search = new URLSearchParams();
  if (params.status) search.set("status", params.status);
  if (params.skip !== undefined) search.set("skip", String(params.skip));
  if (params.limit !== undefined) search.set("limit", String(params.limit));

  const response = await fetch(`${API_BASE}/api/v1/reports?${search}`, {
    headers: { ...getAuthHeaders() }
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

export async function getWeeklyReport(reportId: number): Promise<WeeklyReport> {
  const response = await fetch(`${API_BASE}/api/v1/reports/${reportId}`, {
    headers: { ...getAuthHeaders() }
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

export async function updateWeeklyReport(
  reportId: number,
  payload: { title?: string; summary?: string; content?: string }
): Promise<WeeklyReport> {
  const response = await fetch(`${API_BASE}/api/v1/reports/${reportId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", ...getAuthHeaders() },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

export async function submitWeeklyReport(reportId: number): Promise<WeeklyReport> {
  const response = await fetch(`${API_BASE}/api/v1/reports/${reportId}/submit`, {
    method: "POST",
    headers: { ...getAuthHeaders() }
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

export async function exportWeeklyReport(
  reportId: number,
  format: "markdown" | "html" | "pdf" | "docx"
) {
  const response = await fetch(
    `${API_BASE}/api/v1/reports/${reportId}/export?format=${format}`,
    { method: "POST", headers: { ...getAuthHeaders() } }
  );
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}
