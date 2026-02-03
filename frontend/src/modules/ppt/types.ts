export type PPTProject = {
  id: number;
  title: string;
  description?: string | null;
  status: string;
  theme?: string | null;
  theme_palette?: { bg?: string; text?: string } | null;
  slides?: PPTSlide[];
  outline?: { title?: string; slides?: PPTSlide[] } | null;
  file_path?: string | null;
  created_at?: string;
  updated_at?: string;
};

export type PPTSlide = {
  title: string;
  bullets: string[];
  notes?: string;
};

export type PPTProjectList = {
  total: number;
  skip: number;
  limit: number;
  items: PPTProject[];
};
