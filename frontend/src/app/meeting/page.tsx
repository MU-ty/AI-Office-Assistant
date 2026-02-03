import MeetingModule from "@/modules/meeting";
import { Suspense } from "react";

export default function MeetingPage() {
  return (
    <div className="h-screen">
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
