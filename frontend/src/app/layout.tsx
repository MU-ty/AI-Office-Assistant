// src/app/layout.tsx
import type { Metadata } from "next";
import "./globals.css";
import AuthGate from "@/components/auth/AuthGate";
import AppShell from "@/components/auth/AppShell";

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
        <AuthGate>
          <AppShell>{children}</AppShell>
        </AuthGate>
      </body>
    </html>
  );
}
