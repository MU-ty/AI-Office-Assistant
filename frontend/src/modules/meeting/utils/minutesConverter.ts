/**
 * 将后端 JSON 格式的会议纪要转换为 Markdown 格式
 */

export interface MeetingMinutesJSON {
  title: string;
  date: string;
  participants: string[];
  meeting_id: string;
  sentences: string[];
  paragraphs: string[];
  keywords: string[];
  key_sentences: string[];
  decisions: string[];
  action_items: Array<{
    content: string;
    owner: string;
    due_date: string;
  }>;
  key_points: string[];
  text_stats?: {
    char_count: number;
    word_count: number;
    sentence_count: number;
    paragraph_count: number;
  };
}

/**
 * 将 JSON 格式的会议纪要转换为 Markdown
 */
export function convertMinutesJSONToMarkdown(data: MeetingMinutesJSON): string {
  const lines: string[] = [];

  // 标题
  lines.push(`# ${data.title}`);
  lines.push("");

  // 元信息
  lines.push(`**日期：** ${data.date}`);
  lines.push("");

  // 参与者
  if (data.participants && data.participants.length > 0) {
    lines.push("## 参与者");
    data.participants.forEach((p) => {
      lines.push(`- ${p}`);
    });
    lines.push("");
  }

  // 会议内容（段落）
  if (data.paragraphs && data.paragraphs.length > 0) {
    lines.push("## 会议内容");
    lines.push("");
    data.paragraphs.forEach((p) => {
      lines.push(p);
      lines.push("");
    });
  }

  // 关键点
  if (data.key_points && data.key_points.length > 0) {
    lines.push("## 关键要点");
    data.key_points.forEach((point) => {
      lines.push(`- ${point}`);
    });
    lines.push("");
  }

  // 决议
  if (data.decisions && data.decisions.length > 0) {
    lines.push("## 关键决议");
    data.decisions.forEach((decision) => {
      lines.push(`- ${decision}`);
    });
    lines.push("");
  }

  // Action Items
  if (data.action_items && data.action_items.length > 0) {
    lines.push("## 行动事项");
    lines.push("");
    lines.push("| 任务 | 负责人 | 截止日期 |");
    lines.push("|------|--------|----------|");
    data.action_items.forEach((item) => {
      lines.push(`| ${item.content} | ${item.owner} | ${item.due_date} |`);
    });
    lines.push("");
  }

  // 统计信息
  if (data.text_stats) {
    lines.push("---");
    lines.push("");
    lines.push("**统计信息**");
    lines.push(`- 字符数: ${data.text_stats.char_count}`);
    lines.push(`- 词数: ${data.text_stats.word_count}`);
    lines.push(`- 句子数: ${data.text_stats.sentence_count}`);
    lines.push(`- 段落数: ${data.text_stats.paragraph_count}`);
  }

  return lines.join("\n");
}

/**
 * 生成执行摘要
 */
export function generateSummary(data: MeetingMinutesJSON): string {
  const summary: string[] = [];

  summary.push("## 执行摘要");
  summary.push("");

  // 关键决议
  if (data.decisions && data.decisions.length > 0) {
    const topDecisions = data.decisions.slice(0, 3);
    summary.push("**关键决议：**");
    topDecisions.forEach((d) => {
      summary.push(`- ${d}`);
    });
    summary.push("");
  }

  // Action Items
  if (data.action_items && data.action_items.length > 0) {
    const topActions = data.action_items.slice(0, 3);
    summary.push("**待办事项：**");
    topActions.forEach((item) => {
      summary.push(`- ${item.content} (${item.owner}, ${item.due_date})`);
    });
    summary.push("");
  }

  return summary.join("\n");
}
