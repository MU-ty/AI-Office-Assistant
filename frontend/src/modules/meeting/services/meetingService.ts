const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8003";

export const meetingService = {
  /**
   * 1. 创建会议记录
   */
  async createMeeting(payload: {
    title: string;
    meeting_type: string;
    start_time: string;
    location?: string;
  }) {
    const res = await fetch(`${API_BASE}/api/v1/meetings`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    return this._handleResponse(res, "创建会议失败");
  },

  /**
   * 2. 上传音频并触发 AI 分析
   */
  async uploadAudio(meetingId: string, file: File) {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API_BASE}/api/v1/meetings/${meetingId}/upload`, {
      method: "POST",
      body: formData,
    });
    return this._handleResponse(res, "音频上传失败");
  },

  /**
   * 3. 轮询任务状态 (检查 AI 是否处理完成)
   */
  async getTaskStatus(taskId: string) {
    const res = await fetch(`${API_BASE}/api/v1/meetings/tasks/${taskId}`);
    return this._handleResponse(res, "获取任务状态失败");
  },

  /**
   * 4. 获取最终生成的 Markdown 内容
   * 注意：如果后端直接返回 MD 文本，用 .text()；如果是 JSON，用 .json()
   */
  async getMinutes(meetingId: string) {
    const res = await fetch(`${API_BASE}/api/v1/meetings/${meetingId}/minutes`);
    return this._handleResponse(res, "获取会议纪要失败");
  },

  /**
   * 内部统一错误处理
   */
  async _handleResponse(response: Response, errorMsg: string) {
    if (!response.ok) {
      const errorData = await response.text();
      console.error(`${errorMsg}:`, errorData);
      throw new Error(`${errorMsg} (${response.status})`);
    }
    // 根据后端返回类型灵活处理，如果是 MD 文件通常是 text，API 接口通常是 json
    const contentType = response.headers.get("content-type");
    if (contentType?.includes("application/json")) {
      return response.json();
    }
    return response.text();
  }
};