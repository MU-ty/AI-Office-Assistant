"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { login } from "@/modules/auth/api";

export default function LoginPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setLoading(true);
    const form = new FormData(event.currentTarget);
    const username = String(form.get("username") || "").trim();
    const password = String(form.get("password") || "").trim();
    try {
      const data = await login({ username, password });
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      localStorage.setItem("user", JSON.stringify(data.user));
      router.push("/weekly");
    } catch (err) {
      setError(err instanceof Error ? err.message : "登录失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-md shadow-xl">
      <CardHeader className="space-y-2">
        <CardTitle className="text-2xl">欢迎回来</CardTitle>
        <CardDescription>登录后即可关联周报、会议纪要等内容</CardDescription>
      </CardHeader>
      <CardContent>
        <form className="space-y-4" onSubmit={handleSubmit}>
          {error && (
            <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-600">
              {error}
            </div>
          )}
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700">用户名或邮箱</label>
            <input
              required
              name="username"
              className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              placeholder="请输入用户名或邮箱"
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700">密码</label>
            <input
              required
              type="password"
              name="password"
              className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              placeholder="请输入密码"
            />
          </div>
          <Button className="w-full" type="submit" disabled={loading}>
            {loading ? "登录中..." : "登录"}
          </Button>
        </form>
        <p className="mt-4 text-xs text-slate-500">
          没有账号？
          <Link href="/auth/register" className="ml-1 text-blue-600 hover:underline">
            去注册
          </Link>
        </p>
      </CardContent>
    </Card>
  );
}
