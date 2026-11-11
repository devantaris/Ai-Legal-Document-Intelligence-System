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

export type RiskLevel = "RED" | "AMBER" | "GREEN";

export interface FallbackDrafts {
  conservative: string;
  compromise: string;
  aggressive: string;
}

export interface PlaybookFinding {
  clause_id: string | null;
  clause_type: string;
  title: string;
  risk_level: RiskLevel;
  score: number;
  page_start: number | null;
  section_path: string;
  clause_text: string;
  standard_rule: string;
  deviation_reason: string;
  action_required: string;
  fallbacks: FallbackDrafts;
}

export interface PlaybookReviewOut {
  document_id: string;
  compliance_score: number;
  overall_risk: "Low Risk" | "Moderate Risk" | "High Risk" | "Severe Exposure";
  summary: string;
  red_count: number;
  amber_count: number;
  green_count: number;
  total_evaluated: number;
  findings: PlaybookFinding[];
}

export interface ChunkLite {
  id: string;
  seq: number;
  page_start: number | null;
  page_end: number | null;
  section_path: string;
  text: string;
}

export interface DocumentContentOut {
  id: string;
  filename: string;
  page_count: number | null;
  chunks: ChunkLite[];
}

export interface DefinedTermOut {
  term: string;
  definition: string;
  page_defined: number | null;
  section_defined: string;
  frequency: number;
  chunk_ids: string[];
}

export interface DefinedTermsSummaryOut {
  document_id: string;
  total_terms: number;
  terms: DefinedTermOut[];
}

export interface PortfolioItem {
  id: string;
  filename: string;
  status: string;
  created_at: string;
  page_count: number | null;
  agreement_type: string | null;
  parties: string[];
  effective_date: string | null;
  governing_law: string | null;
  payment_terms: string | null;
  liability_cap: string | null;
  compliance_score: number | null;
  overall_risk: string | null;
}

export interface PortfolioMatrixOut {
  total_documents: number;
  documents: PortfolioItem[];
}

export interface PortfolioAnswerOut {
  answer: string;
  citations: Citation[];
  documents_referenced: string[];
}

export interface SentenceAudit {
  sentence_index: number;
  sentence_text: string;
  status: "VERIFIED" | "EXTRAPOLATED" | "UNSUPPORTED";
  entailment_score: number;
  best_matching_citation: number | null;
  supporting_quote: string;
}

export interface EntailmentAuditOut {
  fidelity_score: number;
  audit_passed: boolean;
  status_label: "100% Citation Grounded" | "High Fidelity" | "Contains Ungrounded Claims";
  verified_count: number;
  total_count: number;
  sentence_audits: SentenceAudit[];
}


