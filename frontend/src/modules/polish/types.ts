export type PolishIssue = {
  id: number;
  task_id: number;
  issue_type: string;
  severity: string;
  location: { start: number; end: number };
  original_content: string;
  suggested_content: string;
  reason?: string | null;
  status: string;
  rule_id?: string | null;
  confidence?: number | null;
  accepted_at?: string | null;
  created_at?: string | null;
};

export type PolishTask = {
  id: number;
  user_id?: number | null;
  document_id?: number | null;
  original_text: string;
  polished_text?: string | null;
  status: string;
  polish_level: string;
  total_issues: number;
  fixed_issues: number;
  accuracy: number;
  created_at?: string | null;
  updated_at?: string | null;
  completed_at?: string | null;
};

export type PolishTaskList = {
  total: number;
  skip: number;
  limit: number;
  items: PolishTask[];
};
