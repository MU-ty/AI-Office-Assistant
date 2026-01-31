"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { register } from "@/modules/auth/api";

export default function RegisterPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setLoading(true);
    const form = new FormData(event.currentTarget);
    const password = String(form.get("password") || "").trim();
    const confirm = String(form.get("confirm") || "").trim();
    if (password !== confirm) {
      setError("两次密码不一致");
      setLoading(false);
      return;
    }
    try {
      await register({
        username: String(form.get("username") || "").trim(),
        email: String(form.get("email") || "").trim(),
        password,
        full_name: String(form.get("full_name") || "").trim() || undefined
      });
      router.push("/auth/login");
    } catch (err) {
      setError(err instanceof Error ? err.message : "注册失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-md shadow-xl">
      <CardHeader className="space-y-2">
        <CardTitle className="text-2xl">创建账号</CardTitle>
        <CardDescription>注册后即可关联周报与会议纪要数据</CardDescription>
      </CardHeader>
      <CardContent>
        <form className="space-y-4" onSubmit={handleSubmit}>
          {error && (
            <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-600">
              {error}
            </div>
          )}
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700">用户名</label>
            <input
              required
              name="username"
              className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              placeholder="请输入用户名"
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700">邮箱</label>
                      <div className="space-y-2">
                        <label className="text-sm font-medium text-slate-700">姓名（可选）</label>
                        <input
                          name="full_name"
                          className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                          placeholder="请输入姓名"
                        />
                      </div>
            <input
              required
              type="email"
              name="email"
              className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              placeholder="name@example.com"
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700">密码</label>
            <input
              required
              type="password"
              name="password"
              className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              placeholder="至少 8 位"
              minLength={8}
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700">确认密码</label>
            <input
              required
              type="password"
              name="confirm"
              className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              placeholder="再次输入密码"
              minLength={8}
            />
          </div>
          <Button className="w-full" type="submit" disabled={loading}>
            {loading ? "注册中..." : "注册"}
          </Button>
        </form>
        <p className="mt-4 text-xs text-slate-500">
          已有账号？
          <Link href="/auth/login" className="ml-1 text-blue-600 hover:underline">
            去登录
          </Link>
        </p>
      </CardContent>
    </Card>
  );
}
