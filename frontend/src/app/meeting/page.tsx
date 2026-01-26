import MeetingModule from "@/modules/meeting";

export default function MeetingPage() {
  return (
    // 页面层只负责大布局
    <div className="h-[calc(100vh-4rem)] w-full p-4 bg-slate-50">
      <MeetingModule />
    </div>
  );
}
