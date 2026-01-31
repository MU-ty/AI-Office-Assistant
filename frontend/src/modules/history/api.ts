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

export async function fetchMeetingHistory() {
  const response = await fetch(`${API_BASE}/api/v1/meetings?skip=0&limit=5`, {
    headers: { ...getAuthHeaders() }
  });
  return unwrap<Array<Record<string, unknown>>>(response);
}

export async function fetchWeeklyHistory() {
  const response = await fetch(`${API_BASE}/api/v1/reports?skip=0&limit=5`, {
    headers: { ...getAuthHeaders() }
  });
  return unwrap<{ items: Array<Record<string, unknown>> }>(response);
}

export async function fetchPolishHistory() {
  const response = await fetch(`${API_BASE}/api/v1/polish?skip=0&limit=5`, {
    headers: { ...getAuthHeaders() }
  });
  return unwrap<{ items: Array<Record<string, unknown>> }>(response);
}

export async function fetchDocumentHistory() {
  const response = await fetch(`${API_BASE}/api/v1/documents/`, {
    headers: { ...getAuthHeaders() }
  });
  return unwrap<Array<Record<string, unknown>>>(response);
}

export async function fetchTranslationHistory() {
  const response = await fetch(`${API_BASE}/api/v1/translations?skip=0&limit=5`, {
    headers: { ...getAuthHeaders() }
  });
  return unwrap<{ items: Array<Record<string, unknown>> }>(response);
}

export async function fetchPptHistory() {
  const response = await fetch(`${API_BASE}/api/v1/ppt?skip=0&limit=5`, {
    headers: { ...getAuthHeaders() }
  });
  return unwrap<{ items: Array<Record<string, unknown>> }>(response);
}
