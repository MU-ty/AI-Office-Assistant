export type ChatMessage = {
  id: string;
  role: "assistant";
  content: string;
  section?: string;
};

/**
 * 将纪要 Markdown 文本拆成聊天消息数组。
 * - 默认按空行分段；可按需调整规则（如按一级/二级标题分段）。
 */
export function minutesToMessages(raw: string): ChatMessage[] {
  if (!raw) return [];

  const segments = raw
    // 以空行分段，避免超长气泡
    .split(/\n\s*\n/)
    .map((s) => s.trim())
    .filter(Boolean);

  return segments.map((seg, idx) => {
    const headingMatch = seg.match(/^#{1,6}\s+(.*)/);
    return {
      id: `minutes-${idx}`,
      role: "assistant",
      content: seg,
      section: headingMatch?.[1],
    } satisfies ChatMessage;
  });
}
