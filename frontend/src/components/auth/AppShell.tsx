"use client";

import { ReactNode, useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import Link from "next/link";
import { Mic2, LayoutDashboard, History, Settings, User, BookOpenCheck, FileText, Languages, Presentation } from "lucide-react";

export default function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [displayName, setDisplayName] = useState("未登录");
  const [planLabel, setPlanLabel] = useState("访客");
  const isAuthRoute = pathname.startsWith("/auth");

  useEffect(() => {
    if (typeof window === "undefined") return;
    const token = localStorage.getItem("access_token");
    const userRaw = localStorage.getItem("user");
    if (!token) {
      setDisplayName("未登录");
      setPlanLabel("访客");
      return;
    }
    try {
      const user = userRaw ? JSON.parse(userRaw) : null;
      setDisplayName(user?.full_name || user?.username || "已登录");
      setPlanLabel("个人使用");
    } catch {
      setDisplayName("已登录");
      setPlanLabel("个人使用");
    }
  }, [pathname]);

  if (isAuthRoute) {
    return <div className="flex-1 overflow-y-auto">{children}</div>;
  }

  return (
    <>
      <aside className="w-64 bg-white border-r flex flex-col shadow-sm">
        <div className="p-6 flex items-center gap-3 text-blue-600 font-bold text-xl">
          <Mic2 className="w-8 h-8" />
          <span>Office AI</span>
        </div>

        <nav className="flex-1 px-4 py-4 space-y-1">
          <Link
            href="/meeting"
            className="flex items-center gap-3 px-4 py-3 bg-blue-50 text-blue-700 rounded-xl cursor-pointer font-medium"
          >
            <LayoutDashboard className="w-5 h-5" />
            会议纪要
          </Link>
          <Link
            href="/weekly"
            className="flex items-center gap-3 px-4 py-3 text-slate-700 rounded-xl hover:bg-slate-100"
          >
            <LayoutDashboard className="w-5 h-5" />
            周报生成
          </Link>
          <Link
            href="/polish"
            className="flex items-center gap-3 px-4 py-3 text-slate-700 rounded-xl hover:bg-slate-100"
          >
            <BookOpenCheck className="w-5 h-5" />
            学术润色
          </Link>
          <Link
            href="/documents"
            className="flex items-center gap-3 px-4 py-3 text-slate-700 rounded-xl hover:bg-slate-100"
          >
            <FileText className="w-5 h-5" />
            文献摘要
          </Link>
          <Link
            href="/translation"
            className="flex items-center gap-3 px-4 py-3 text-slate-700 rounded-xl hover:bg-slate-100"
          >
            <Languages className="w-5 h-5" />
            多语言翻译
          </Link>
          <Link
            href="/ppt"
            className="flex items-center gap-3 px-4 py-3 text-slate-700 rounded-xl hover:bg-slate-100"
          >
            <Presentation className="w-5 h-5" />
            PPT生成
          </Link>
          {/* <Link
            href="/auth/login"
            className="flex items-center gap-3 px-4 py-3 text-slate-700 rounded-xl hover:bg-slate-100"
          >
            <User className="w-5 h-5" />
            登录 / 注册
          </Link> */}
          <Link
            href="/history"
            className="flex items-center gap-3 px-4 py-3 text-slate-700 rounded-xl hover:bg-slate-100"
          >
            <History className="w-5 h-5" />
            历史记录
          </Link>
          <div className="flex items-center gap-3 px-4 py-3 text-slate-400 rounded-xl cursor-not-allowed">
            <Settings className="w-5 h-5" />
            全局设置 (P1)
          </div>
        </nav>

        <div className="p-4 border-t">
          <Link
            href="/profile"
            className="flex items-center gap-3 p-2 hover:bg-slate-50 rounded-lg transition-colors"
          >
            <div className="w-9 h-9 bg-slate-200 rounded-full flex items-center justify-center">
              <User className="w-5 h-5 text-slate-500" />
            </div>
            <div className="text-sm">
              <p className="font-medium">{displayName}</p>
              <p className="text-slate-500 text-xs">{planLabel}</p>
            </div>
          </Link>
          <button
            type="button"
            className="mt-3 w-full rounded-md border border-slate-200 px-3 py-2 text-xs text-slate-600 hover:bg-slate-50"
            onClick={() => {
              localStorage.removeItem("access_token");
              localStorage.removeItem("refresh_token");
              localStorage.removeItem("user");
              router.replace("/auth/login");
            }}
          >
            退出登录
          </button>
        </div>
      </aside>

      <main className="flex-1 flex flex-col overflow-hidden relative">
        <div className="flex-1 overflow-y-auto">{children}</div>
      </main>
    </>
  );
}
