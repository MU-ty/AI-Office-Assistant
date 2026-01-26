import React, { useRef } from "react";
import { Button } from "@/components/ui/button";
import { FileAudio } from "lucide-react";

interface UploadButtonProps {
  onFileSelect: (file: File) => void;
  isStarted: boolean;
}

export const UploadButton = ({
  onFileSelect,
  isStarted,
}: UploadButtonProps) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) onFileSelect(file);
  };

  return (
    <>
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept="audio/*,video/*"
        className="hidden"
      />
      {/* 上传按钮组件，用于触发文件选择对话框 */}
      <Button
        onClick={() => fileInputRef.current?.click()}
        disabled={isStarted}
        className="w-full h-12 text-base shadow-sm hover:shadow-md transition-all"
      >
        <FileAudio className="w-5 h-5 mr-2" />
        上传会议音频并开始分析
      </Button>
    </>
  );
};
