const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8003";

export type LoginResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: {
    id: number;
    username: string;
    email: string;
    full_name?: string | null;
  };
};

export async function login(payload: { username: string; password: string }): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE}/api/v1/users/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    const text = await response.text();
    try {
      const data = JSON.parse(text);
      throw new Error(data.detail || data.message || text);
    } catch {
      throw new Error(text || "登录失败");
    }
  }
  return response.json();
}

export async function register(payload: {
  username: string;
  email: string;
  password: string;
  full_name?: string;
}) {
  const response = await fetch(`${API_BASE}/api/v1/users/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    const text = await response.text();
    try {
      const data = JSON.parse(text);
      throw new Error(data.detail || data.message || text);
    } catch {
      throw new Error(text || "注册失败");
    }
  }
  return response.json();
}
