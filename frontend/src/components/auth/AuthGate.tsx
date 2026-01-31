"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";

export default function AuthGate({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const isAuthRoute = pathname.startsWith("/auth");
    const token = localStorage.getItem("access_token");

    if (!token && !isAuthRoute) {
      router.replace("/auth/login");
      return;
    }

    if (token && isAuthRoute) {
      router.replace("/weekly");
      return;
    }

    setReady(true);
  }, [pathname, router]);

  if (!ready) {
    return null;
  }

  return <>{children}</>;
}
