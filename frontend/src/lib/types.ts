export interface Chunk {
  chunk_id: string;
  text: string;
  start_char: number;
  end_char: number;
}

export interface UploadResponse {
  doc_id: string;
  filename: string;
  total_pages: number;
  total_chars: number;
  total_chunks: number;
  language_detected: string;
  full_text: string;
  chunks: Chunk[];
}

export interface RiskFlag {
  clause_text: string;
  plain_explanation: string;
  severity: "HIGH" | "MEDIUM" | "LOW";
  lawyer_question: string;
  indian_law_context: string;
}

export interface AnalysisResult {
  doc_id: string;
  document_type: string;
  overall_risk_score: number;
  overall_verdict: string;
  signing_recommendation: "SAFE_TO_SIGN" | "REVIEW_RECOMMENDED" | "DO_NOT_SIGN";
  risk_colour: { label: string; hex_color: string; emoji: string };
  risk_counts: { high: number; medium: number; low: number; total: number };
  flags: RiskFlag[];
  language: string;
  analysed_at: string;
}

export interface AskResponse {
  answer: string;
  source_chunks: { chunk_id: string; excerpt: string }[];
  language: string;
  model_used: string;
}

export interface SummariseResponse {
  summary_bullets: string[];
  language: string;
}

export interface Language {
  code: string;
  name: string;
  native: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources?: { chunk_id: string; excerpt: string }[];
}
