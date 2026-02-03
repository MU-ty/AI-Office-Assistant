export type KnowledgeBase = {
  id: string;
  name: string;
  description?: string;
  created_at?: string;
  updated_at?: string;
};

export type KnowledgeItem = {
  id: string;
  title?: string;
  description?: string;
  source?: string;
  parse_status?: string;
  enable_status?: string;
  file_type?: string;
  created_at?: string;
};

export type KnowledgeSearchChunk = {
  id: string;
  content?: string;
  knowledge_id?: string;
  knowledge_title?: string;
  score?: number;
  chunk_type?: string;
  knowledge_source?: string;
  knowledge_filename?: string;
};
