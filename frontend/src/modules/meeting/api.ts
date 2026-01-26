const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export async function createMeeting(payload: {
  title: string;
  meeting_type: string;
  start_time: string;
  location?: string;
}) {
  const response = await fetch(`${API_BASE}/api/v1/meetings`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.text();
    console.error("Create meeting error:", errorData);
    throw new Error(`创建会议失败: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

export async function uploadMeetingAudio(meetingId: string, file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(
    `${API_BASE}/api/v1/meetings/${meetingId}/upload`,
    {
      method: "POST",
      body: formData,
    },
  );

  if (!response.ok) {
    const errorData = await response.text();
    console.error("Upload error:", errorData);
    throw new Error(`文件上传失败: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

export async function fetchTaskStatus(taskId: string) {
  const response = await fetch(`${API_BASE}/api/v1/meetings/tasks/${taskId}`);

  if (!response.ok) {
    const errorData = await response.text();
    console.error("Task status error:", errorData);
    throw new Error(
      `获取任务状态失败: ${response.status} ${response.statusText}`,
    );
  }

  return response.json();
}

export async function fetchMeetingMinutes(meetingId: string) {
  const response = await fetch(
    `${API_BASE}/api/v1/meetings/${meetingId}/minutes`,
  );

  if (!response.ok) {
    const errorData = await response.text();
    console.error("Fetch minutes error:", errorData);
    throw new Error(
      `获取会议纪要失败: ${response.status} ${response.statusText}`,
    );
  }

  return response.json();
}
