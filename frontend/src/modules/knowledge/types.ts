export type KnowledgeBase = {
  id: string;
  name: string;
  description?: string;
  created_at?: string;
  updated_at?: string;
  owner_id?: number;
  is_public?: boolean;
};

export type Directory = {
  id: number;
  name: string;
  parent_id: number | null;
  children: Directory[];
  knowledge_base_id?: number;
};

export type Tag = {
  id: number;
  name: string;
  color: string;
};

export type Document = {
  id: number;
  title: string;
  content?: string;
  document_type: string;
  source_type: string;
  file_path?: string;
  status: string;
  review_status?: string;
  current_version?: number;
  created_at: string;
  updated_at: string;
  tags?: Tag[];
};

export type SearchResult = {
  id: number;
  title: string;
  content: string;
  title_highlight?: string;
  content_highlight?: string[];
  score: number;
  document_type?: string;
  created_at?: string;
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
