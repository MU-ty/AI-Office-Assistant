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
