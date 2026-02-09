export function formatDate(value?: string) {
  if (!value) return "";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return d.toISOString().slice(0, 10);
}

export function toIsoDateTime(date: string, endOfDay = false) {
  if (!date) return "";
  return endOfDay ? `${date}T23:59:59` : `${date}T00:00:00`;
}

export function getCurrentWeekRange() {
  const now = new Date();
  const day = (now.getDay() + 6) % 7; // Monday = 0
  const start = new Date(now);
  start.setDate(now.getDate() - day);
  const end = new Date(start);
  end.setDate(start.getDate() + 6);
  return {
    start: start.toISOString().slice(0, 10),
    end: end.toISOString().slice(0, 10)
  };
}

export function normalizeSummary(summary?: string | null) {
  if (!summary) return "";
  return summary
    .replace(/^本周工作总结:?\s*/g, "本周完成：")
    .replace(/AI|智能|自动生成/g, "")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

export function getSummaryTemplate() {
  return [
    "本周完成：",
    "- ",
    "",
    "问题与风险：",
    "- ",
    "",
    "下周计划：",
    "- "
  ].join("\n");
}

export function getDetailTemplate() {
  return [
    "本周完成：",
    "1. ",
    "",
    "问题与风险：",
    "1. ",
    "",
    "下周计划：",
    "1. "
  ].join("\n");
}

type SectionKey = "completed" | "risks" | "plans";

const sectionMap: Record<string, SectionKey> = {
  "本周完成": "completed",
  "问题与风险": "risks",
  "下周计划": "plans"
};

export function parseWeeklySections(text?: string | null) {
  const result = {
    completed: [] as string[],
    risks: [] as string[],
    plans: [] as string[]
  };
  if (!text) return result;

  const lines = text.split(/\r?\n/).map((line) => line.trim());
  let current: SectionKey | null = null;

  for (const line of lines) {
    if (!line) continue;
    const header = line.replace(/[:：]\s*$/, "");
    if (sectionMap[header]) {
      current = sectionMap[header];
      continue;
    }
    if (!current) continue;
    const cleaned = line.replace(/^[-*\d\.\)]+\s*/, "").trim();
    if (cleaned) {
      result[current].push(cleaned);
    }
  }

  return result;
}

export function getSummaryPreview(summary?: string | null) {
  if (!summary) return "暂无摘要";
  const sections = parseWeeklySections(summary);
  const all = [...sections.completed, ...sections.risks, ...sections.plans];
  if (!all.length) return summary.slice(0, 60);
  return all.slice(0, 2).join("；");
}

export function getPlaceholderCount(text?: string | null) {
  if (!text) return 0;
  const lines = text.split(/\r?\n/);
  let count = 0;
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    if (trimmed === "-" || trimmed === "-" || trimmed === "- " || trimmed === "1." || trimmed === "1." || trimmed === "1. " || trimmed.endsWith(":") || trimmed.endsWith("：")) {
      count += 1;
    }
  }
  return count;
}
