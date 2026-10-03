export type DocStatus = "uploaded" | "parsing" | "embedding" | "ready" | "failed";

export interface User {
  id: string;
  email: string;
  created_at: string;
}

export interface DocumentOut {
  id: string;
  filename: string;
  mime: string;
  status: DocStatus;
  page_count: number | null;
  size_bytes: number;
  error: string | null;
  has_summary: boolean;
  has_key_terms: boolean;
  clause_count: number;
  chunk_count: number;
  created_at: string;
}

export interface Citation {
  n: number;
  chunk_id: string;
  document_id: string;
  filename: string;
  page: number | null;
  section_path: string;
  quote: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations: Citation[] | null;
  created_at: string;
}

export interface Clause {
  id: string;
  seq: number;
  clause_type: string;
  title: string;
  page_start: number | null;
  page_end: number | null;
  section_path: string;
  text: string;
}

export interface Party {
  name: string;
  role: string | null;
}

export interface KeyTerms {
  agreement_type: string | null;
  parties: Party[];
  effective_date: string | null;
  term: string | null;
  governing_law: string | null;
  payment_terms: string | null;
  termination: string | null;
  renewal: string | null;
  confidentiality: string | null;
  indemnification: string | null;
  dispute_resolution: string | null;
  obligations: string[];
  special_notes: string[];
}

export interface LlmInfo {
  provider: string;
  llm_model: string | null;
  embed_model: string | null;
  embedding_dim: number;
  available: boolean;
  error: string | null;
}

export type CompareStatus = "modified" | "added" | "removed";

export interface CompareItem {
  status: CompareStatus;
  change_level: string;
  change_summary: string;
  similarity?: number;
  a: ClauseLite | null;
  b: ClauseLite | null;
}

export interface ClauseLite {
  id: string;
  clause_type: string;
  title: string;
  page_start: number | null;
  page_end: number | null;
  section_path: string;
  text: string;
}

export interface CompareResult {
  document_a: { id: string; filename: string };
  document_b: { id: string; filename: string };
  counts: { modified: number; added: number; removed: number; unchanged: number };
  summary: string;
  items: CompareItem[];
}
