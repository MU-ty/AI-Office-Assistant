import type { PPTProject, PPTProjectList } from "./types";

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

export async function createPPTProject(payload: {
  title: string;
  description?: string;
  source_content: string;
  theme?: string;
  theme_palette?: { bg?: string; text?: string } | null;
}): Promise<PPTProject> {
  const response = await fetch(`${API_BASE}/api/v1/ppt/`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...getAuthHeaders() },
    body: JSON.stringify(payload)
  });
  return unwrap<PPTProject>(response);
}

export async function importPPTProject(payload: {
  title: string;
  description?: string;
  theme?: string;
  theme_palette?: { bg?: string; text?: string } | null;
  file: File;
}): Promise<PPTProject> {
  const formData = new FormData();
  formData.append("title", payload.title);
  if (payload.description) formData.append("description", payload.description);
  if (payload.theme) formData.append("theme", payload.theme);
  if (payload.theme_palette) formData.append("theme_palette", JSON.stringify(payload.theme_palette));
  formData.append("file", payload.file);

  const response = await fetch(`${API_BASE}/api/v1/ppt/import`, {
    method: "POST",
    headers: { ...getAuthHeaders() },
    body: formData
  });
  return unwrap<PPTProject>(response);
}

export async function listPPTProjects(params: {
  skip?: number;
  limit?: number;
  status?: string;
}): Promise<PPTProjectList> {
  const search = new URLSearchParams();
  if (params.status) search.set("status", params.status);
  if (params.skip !== undefined) search.set("skip", String(params.skip));
  if (params.limit !== undefined) search.set("limit", String(params.limit));

  const response = await fetch(`${API_BASE}/api/v1/ppt?${search}`, {
    headers: { ...getAuthHeaders() }
  });
  return unwrap<PPTProjectList>(response);
}

export async function getPPTProject(projectId: number): Promise<PPTProject> {
  const response = await fetch(`${API_BASE}/api/v1/ppt/${projectId}`, {
    headers: { ...getAuthHeaders() }
  });
  return unwrap<PPTProject>(response);
}

export async function generatePPTSlides(
  projectId: number,
  tone: string,
  theme?: string,
  theme_palette?: { bg?: string; text?: string } | null
): Promise<PPTProject> {
  const response = await fetch(`${API_BASE}/api/v1/ppt/${projectId}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...getAuthHeaders() },
    body: JSON.stringify({ tone, theme, theme_palette })
  });
  return unwrap<PPTProject>(response);
}

export async function exportPPT(projectId: number): Promise<{ path: string } & Record<string, unknown>> {
  const response = await fetch(`${API_BASE}/api/v1/ppt/${projectId}/export`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...getAuthHeaders() },
    body: JSON.stringify({ format: "pptx" })
  });
  return unwrap<{ path: string } & Record<string, unknown>>(response);
}
