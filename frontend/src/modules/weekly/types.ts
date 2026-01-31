export type WorkLog = {
  id: number;
  user_id?: number | null;
  work_type: string;
  task_description: string;
  hours_spent: number;
  log_date: string;
  created_at: string;
};

export type WeeklyReport = {
  id: number;
  user_id?: number | null;
  title?: string | null;
  week: string;
  week_start_date: string;
  week_end_date: string;
  summary?: string | null;
  content?: string | null;
  status: string;
  total_hours: number;
  created_at: string;
  updated_at: string;
  review_feedback?: string | null;
  reviewer_id?: number | null;
  reviewed_at?: string | null;
};

export type WorkLogListResponse = {
  total: number;
  skip: number;
  limit: number;
  items: WorkLog[];
};

export type WeeklyReportListResponse = {
  total: number;
  skip: number;
  limit: number;
  items: WeeklyReport[];
};
