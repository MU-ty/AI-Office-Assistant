// src/app/layout.tsx
import type { Metadata } from "next";
import "./globals.css";
import { Mic2, LayoutDashboard, History, Settings, User } from "lucide-react";

export const metadata: Metadata = {
  title: "AI Office Assistant",
  description: "AI Powered Meeting Minutes",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="flex h-screen bg-slate-100 overflow-hidden text-slate-900">
        {/* 左侧边栏 Sidebar */}
        <aside className="w-64 bg-white border-r flex flex-col shadow-sm">
          <div className="p-6 flex items-center gap-3 text-blue-600 font-bold text-xl">
            <Mic2 className="w-8 h-8" />
            <span>Office AI</span>
          </div>

          <nav className="flex-1 px-4 py-4 space-y-1">
            <div className="flex items-center gap-3 px-4 py-3 bg-blue-50 text-blue-700 rounded-xl cursor-pointer font-medium">
              <LayoutDashboard className="w-5 h-5" />
              会议纪要
            </div>
            <div className="flex items-center gap-3 px-4 py-3 text-slate-400 rounded-xl cursor-not-allowed">
              <History className="w-5 h-5" />
              历史记录 (P1)
            </div>
            <div className="flex items-center gap-3 px-4 py-3 text-slate-400 rounded-xl cursor-not-allowed">
              <Settings className="w-5 h-5" />
              全局设置 (P1)
            </div>
          </nav>

          <div className="p-4 border-t">
            <div className="flex items-center gap-3 p-2 hover:bg-slate-50 rounded-lg cursor-pointer transition-colors">
              <div className="w-9 h-9 bg-slate-200 rounded-full flex items-center justify-center">
                <User className="w-5 h-5 text-slate-500" />
              </div>
              <div className="text-sm">
                <p className="font-medium">User Admin</p>
                <p className="text-slate-500 text-xs">Free Plan</p>
              </div>
            </div>
          </div>
        </aside>

        {/* 主内容区 Main Content */}
        <main className="flex-1 flex flex-col overflow-hidden relative">
          <div className="flex-1 overflow-y-auto">{children}</div>
        </main>
      </body>
    </html>
  );
}
