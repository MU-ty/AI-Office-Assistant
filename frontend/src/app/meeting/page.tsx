import MeetingModule from "@/modules/meeting";
import { Suspense } from "react";

export default function MeetingPage() {
  return (
    // 页面层只负责大布局
    <div className="h-[calc(100vh-4rem)] w-full p-4 bg-slate-50">
      <Suspense fallback={
        <div className="flex items-center justify-center h-full">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      }>
        <MeetingModule />
      </Suspense>
    </div>
  );
}
