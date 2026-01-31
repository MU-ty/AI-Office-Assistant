/**
 * 办公助手 API 模块
 * 包含会议创建、音频上传、状态查询及纪要导出功能
 */

// 1. 获取基础配置：优先使用环境变量，本地开发默认 8003 端口
const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8003";

const getAuthHeaders = () => {
  if (typeof window === "undefined") return {} as Record<string, string>;
  const token = localStorage.getItem("access_token");
  if (!token) return {} as Record<string, string>;
  return { Authorization: `Bearer ${token}` };
};

/**
 * 导出会议纪要 (新接入功能)
 * @param meetingId 会议的唯一标识
 * @param format 导出格式：'markdown' | 'pdf' | 'docx'
 */
export async function exportMeetingMinutes(meetingId: string, format: string) {
  // 根据后端 main.py 的路由前缀 /api/v1/meetings 拼接
  const response = await fetch(
    `${API_BASE}/api/v1/meetings/${meetingId}/export?format=${format}`,
    {
      method: "POST", // 后端修复说明明确要求使用 POST
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeaders(),
      },
    }
  );

  if (!response.ok) {
    const errorData = await response.text();
    console.error("导出接口异常:", errorData);
    throw new Error(`导出失败: ${response.status} - ${errorData}`);
  }

  // 返回格式示例: { "meeting_id": "...", "format": "pdf", "file_path": "/uploads/xxx.pdf", "filename": "xxx.pdf" }
  // 或者 Markdown 格式: { "content": "#纪要...", "filename": "xxx.md" }
  return response.json();
}

/**
 * 获取会议纪要详情
 */
export async function fetchMeetingMinutes(meetingId: string) {
  const response = await fetch(`${API_BASE}/api/v1/meetings/${meetingId}/minutes`, {
    headers: { ...getAuthHeaders() }
  });
  if (!response.ok) throw new Error("获取会议纪要失败");
  return response.json();
}

/**
 * 创建会议
 */
export async function createMeeting(payload: {
  title: string;
  meeting_type: string;
  start_time: string;
  location?: string;
}) {
  const response = await fetch(`${API_BASE}/api/v1/meetings`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...getAuthHeaders() },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error("创建会议失败");
  return response.json();
}

/**
 * 上传音频文件
 */
export async function uploadMeetingAudio(meetingId: string, file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE}/api/v1/meetings/${meetingId}/upload`, {
    method: "POST",
    headers: { ...getAuthHeaders() },
    body: formData, // 注意：上传文件不需要手动设置 Content-Type，浏览器会自动处理边界
  });
  if (!response.ok) throw new Error("音频上传失败");
  return response.json();
}

/**
 * 查询 AI 处理任务状态
 */
export async function fetchTaskStatus(taskId: string) {
  const response = await fetch(`${API_BASE}/api/v1/meetings/tasks/${taskId}`);
  if (!response.ok) throw new Error("查询任务状态失败");
  return response.json();
}