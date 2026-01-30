import { Button } from "@/components/ui/button";
import { 
  FileText, 
  FileCode, 
  FileType, 
  Loader2,
  Download 
} from "lucide-react";
import { useMeetingDownload } from "../hooks/useMeetingDownload";

interface DownloadButtonsProps {
  meetingId: string | undefined;
  isVisible?: boolean;
}

export const DownloadButtons = ({ meetingId, isVisible = true }: DownloadButtonsProps) => {
  const { handleDownload, downloadingFormat } = useMeetingDownload(meetingId);

  if (!isVisible || !meetingId) {
    return null;
  }

  return (
    <div className="h-auto border-t border-slate-200 bg-slate-50 p-4 flex items-center gap-3">
      <span className="text-xs font-semibold text-slate-400 uppercase ml-2">
        导出纪要:
      </span>

      <Button
        variant="outline"
        size="sm"
        disabled={!!downloadingFormat}
        onClick={() => handleDownload("markdown")}
        className="gap-2"
      >
        <FileCode className="w-4 h-4" />
        Markdown
      </Button>

      <Button
        variant="outline"
        size="sm"
        disabled={!!downloadingFormat}
        onClick={() => handleDownload("pdf")}
        className="gap-2 border-red-200 text-red-600 hover:bg-red-50 hover:text-red-700"
      >
        {downloadingFormat === "pdf" ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          <FileText className="w-4 h-4" />
        )}
        PDF 格式
      </Button>

      <Button
        variant="outline"
        size="sm"
        disabled={!!downloadingFormat}
        onClick={() => handleDownload("docx")}
        className="gap-2 border-blue-200 text-blue-600 hover:bg-blue-50 hover:text-blue-700"
      >
        {downloadingFormat === "docx" ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          <FileType className="w-4 h-4" />
        )}
        Word 格式
      </Button>

      <Button
        variant="ghost"
        size="sm"
        className="ml-auto text-slate-400"
      >
        <Download className="w-4 h-4 mr-2" />
        分享纪要
      </Button>
    </div>
  );
};