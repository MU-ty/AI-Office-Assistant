export type DocumentItem = {
  id: number;
  title: string;
  document_type: string;
  source_type: string;
  source_url?: string | null;
  file_path?: string | null;
  created_at?: string;
  updated_at?: string;
  latest_summary?: DocumentSummary | null;
};

export type DocumentSummary = {
  id: number;
  document_id: number;
  summary_level: string;
  summary_text: string;
  quality_score?: number | null;
  model_name?: string | null;
  created_at?: string;
};
