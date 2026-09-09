export type MetadataInfo = {
  title?: string;
  description?: string;
  author?: string;
  publish_date?: string;
  favicon?: string;
  canonical_url?: string;
  language?: string;
  og_tags?: Record<string, string>;
  twitter_tags?: Record<string, string>;
  schema_org?: any[];
};

export type ContentNode = {
  tag: string;
  text?: string;
  children?: ContentNode[];
  attributes?: Record<string, string>;
};

export type ImageInfo = {
  url: string;
  absolute_url: string;
  filename?: string;
  alt_text?: string;
  title?: string;
  caption?: string;
  section?: string;
  position?: number;
  width?: number;
  height?: number;
  format?: string;
  local_path?: string;
  ai_description?: string;
};

export type StructureNode = {
  tag: string;
  id?: string;
  classes?: string[];
  text_preview?: string;
  children?: StructureNode[];
};

export type PageStats = {
  heading_count: number;
  paragraph_count: number;
  image_count: number;
  link_count: number;
  table_count: number;
  list_count: number;
  code_block_count: number;
  word_count: number;
  char_count: number;
};

export type ScrapeResponse = {
  id: string;
  url: string;
  status: string;
  metadata?: MetadataInfo;
  content?: ContentNode[];
  images?: ImageInfo[];
  structure?: StructureNode;
  raw_html?: string;
  clean_html?: string;
  markdown?: string;
  text_content?: string;
  stats?: PageStats;
  technologies?: string[];
  created_at: string;
  error?: string;
};

export type CompareResponse = {
  id: string;
  url1: string;
  url2: string;
  status: string;
  text_diffs?: any[];
  structure_diffs?: any[];
  images_added?: ImageInfo[];
  images_removed?: ImageInfo[];
  similarity_score?: number;
  created_at: string;
  error?: string;
};

export type CrawlResponse = {
  id: string;
  base_url: string;
  status: string;
  pages_found: number;
  pages_scraped: number;
  pages?: any[];
  sitemap?: string;
  created_at: string;
  error?: string;
};

export type HistoryItem = {
  id: string;
  url: string;
  title?: string;
  status: string;
  created_at: string;
  image_count?: number;
  word_count?: number;
};

export type ProgressEvent = {
  status: string;
  progress: number;
  message: string;
  step: string;
};

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

export const api = {
  scrape: async (url: string, download_images: boolean = false, use_ai: boolean = false) => {
    const res = await fetch(`${API_BASE}/api/scrape`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url, download_images, use_ai }),
    });
    return res.json() as Promise<{ id: string; status: string }>;
  },
  getScrape: async (id: string) => {
    const res = await fetch(`${API_BASE}/api/scrape/${id}`);
    return res.json() as Promise<ScrapeResponse>;
  },
  enhanceScrape: async (id: string) => {
    const res = await fetch(`${API_BASE}/api/scrape/${id}/ai`, { method: "POST" });
    return res.json() as Promise<ScrapeResponse>;
  },
  compare: async (url1: string, url2: string) => {
    const res = await fetch(`${API_BASE}/api/compare`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url1, url2 }),
    });
    return res.json() as Promise<CompareResponse>;
  },
  getCompare: async (id: string) => {
    const res = await fetch(`${API_BASE}/api/compare/${id}`);
    return res.json() as Promise<CompareResponse>;
  },
  crawl: async (base_url: string, max_depth: number = 2, max_pages: number = 10) => {
    const res = await fetch(`${API_BASE}/api/crawl`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ base_url, max_depth, max_pages }),
    });
    return res.json() as Promise<{ id: string; status: string }>;
  },
  getCrawl: async (id: string) => {
    const res = await fetch(`${API_BASE}/api/crawl/${id}`);
    return res.json() as Promise<CrawlResponse>;
  },
  exportAnalysis: async (id: string, format: string) => {
    const res = await fetch(`${API_BASE}/api/export/${id}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ format }),
    });
    return res.json() as Promise<{ download_url: string; filename: string }>;
  },
  exportData: async (id: string, format: string) => {
    const res = await fetch(`${API_BASE}/api/export/${id}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ format }),
    });
    return res.json() as Promise<{ download_url: string; filename: string }>;
  },
  getHistory: async () => {
    const res = await fetch(`${API_BASE}/api/history`);
    return res.json() as Promise<HistoryItem[]>;
  },
  deleteHistory: async (id: string) => {
    const res = await fetch(`${API_BASE}/api/history/${id}`, { method: "DELETE" });
    return res.json() as Promise<{ success: boolean }>;
  }
};
