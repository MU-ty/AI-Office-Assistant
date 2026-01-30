import { useState } from 'react';
import { exportMeetingMinutes } from '../api';

export const useMeetingDownload = (meetingId: string | undefined) => {
  const [downloadingFormat, setDownloadingFormat] = useState<string | null>(null);

  const handleDownload = async (format: "markdown" | "pdf" | "docx") => {
    if (!meetingId) {
      console.error("错误：未获取到有效的会议 ID");
      return;
    }

    setDownloadingFormat(format);
    try {
      const data = await exportMeetingMinutes(meetingId, format);
      const API_BASE =
        process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

      let downloadUrl = "";

      if (format === "markdown") {
        // 后端返回的是 { content: "..." }
        const blob = new Blob([data.content], { type: "text/markdown" });
        downloadUrl = URL.createObjectURL(blob);
      } else {
        // 后端返回的是 { file_path: "/uploads/..." }
        // 必须拼接 API 基地址才能访问静态资源
        downloadUrl = data.file_path.startsWith("http")
          ? data.file_path
          : `${API_BASE}${data.file_path}`;
      }

      // 创建虚拟链接并触发下载
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.download = data.filename || `meeting_minutes_${meetingId}.${format}`;
      link.target = "_blank"; // 确保在新标签页打开，不离开当前页面
      
      document.body.appendChild(link);
      link.click();

      // 清理
      document.body.removeChild(link);
      if (format === "markdown") URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      console.error("下载执行失败:", error);
      alert("下载失败，请检查后端服务是否正常运行，或依赖包是否安装。");
    } finally {
      setDownloadingFormat(null);
    }
  };

  return { handleDownload, downloadingFormat };
};