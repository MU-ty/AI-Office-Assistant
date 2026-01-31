export type TranslationTask = {
  id: number;
  user_id?: number;
  source_language: string;
  target_language: string;
  input_text: string;
  translated_text: string;
  status: string;
  domain?: string | null;
  quality_score?: number | null;
  rating?: number | null;
  feedback?: string | null;
  created_at?: string;
  updated_at?: string;
};

export type TranslationTaskList = {
  total: number;
  skip: number;
  limit: number;
  items: TranslationTask[];
};

export type TranslationTerminology = {
  id: number;
  user_id?: number;
  original_term: string;
  translation: string;
  domain: string;
  created_at?: string;
};
