import MeetingModule from "@/modules/meeting";

export default function MeetingPage() {
  return (
    // 这里使用 flex 和 justify-center 是为了让你的 Meeting 卡片在右侧主区域美观居中
    <div className="h-full flex flex-col items-center justify-start py-8 px-4 bg-slate-100">
      <MeetingModule />
    </div>
  );
}