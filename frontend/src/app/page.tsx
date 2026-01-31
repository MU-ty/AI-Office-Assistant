// src/app/page.tsx
import { redirect } from 'next/navigation';

export default function RootPage() {
  // 访问根路径时自动跳转到会议纪要模块
  redirect('/meeting');
}