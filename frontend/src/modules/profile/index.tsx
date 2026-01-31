"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useRouter } from "next/navigation";

type UserProfile = {
  username?: string;
  full_name?: string;
  email?: string;
};

export default function ProfileModule() {
  const router = useRouter();
  const [profile, setProfile] = useState<UserProfile>({});
  const [planLabel, setPlanLabel] = useState("访客");
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const token = localStorage.getItem("access_token");
    const userRaw = localStorage.getItem("user");
    if (!token) {
      setPlanLabel("访客");
      return;
    }
    setPlanLabel("个人使用");
    try {
      const user = userRaw ? JSON.parse(userRaw) : null;
      setProfile({
        username: user?.username || "",
        full_name: user?.full_name || "",
        email: user?.email || ""
      });
    } catch {
      setProfile({});
    }
  }, []);

  const handleSave = () => {
    if (typeof window === "undefined") return;
    const userRaw = localStorage.getItem("user");
    let user: Record<string, unknown> = {};
    try {
      user = userRaw ? JSON.parse(userRaw) : {};
    } catch {
      user = {};
    }
    const nextUser = {
      ...user,
      username: profile.username || user.username,
      full_name: profile.full_name || user.full_name,
      email: profile.email || user.email
    };
    localStorage.setItem("user", JSON.stringify(nextUser));
    setMessage("已保存到本地设置");
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
    router.replace("/auth/login");
  };

  return (
    <div className="mx-auto w-full max-w-4xl space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-slate-800">个人设置</h2>
          <p className="text-xs text-slate-500">管理显示信息与本地偏好</p>
        </div>
        <Badge variant="secondary" className="text-xs">
          {planLabel}
        </Badge>
      </div>

      {message && (
        <div className="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs text-emerald-700">
          {message}
        </div>
      )}

      <Card className="p-4 space-y-3">
        <h3 className="text-sm font-semibold text-slate-700">个人信息</h3>
        <div className="grid gap-3 md:grid-cols-2">
          <label className="text-xs text-slate-500">
            显示名称
            <input
              className="mt-2 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
              value={profile.full_name || ""}
              onChange={(e) => setProfile((prev) => ({ ...prev, full_name: e.target.value }))}
              placeholder="例如：王小明"
            />
          </label>
          <label className="text-xs text-slate-500">
            用户名
            <input
              className="mt-2 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
              value={profile.username || ""}
              onChange={(e) => setProfile((prev) => ({ ...prev, username: e.target.value }))}
              placeholder="例如：ming"
            />
          </label>
          <label className="text-xs text-slate-500 md:col-span-2">
            邮箱
            <input
              className="mt-2 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
              value={profile.email || ""}
              onChange={(e) => setProfile((prev) => ({ ...prev, email: e.target.value }))}
              placeholder="name@example.com"
            />
          </label>
        </div>
        <div className="flex gap-2">
          <Button onClick={handleSave}>保存设置</Button>
          <Button variant="secondary" onClick={handleLogout}>
            退出登录
          </Button>
        </div>
      </Card>

      <Card className="p-4 space-y-2">
        <h3 className="text-sm font-semibold text-slate-700">账户状态</h3>
        <p className="text-xs text-slate-500">当前账号用于个人使用，配置保存在本地设备。</p>
      </Card>
    </div>
  );
}
