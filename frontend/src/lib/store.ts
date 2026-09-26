import { create } from "zustand";
import type { AnalysisResult, SummariseResponse, ChatMessage, Chunk } from "./types";

interface NyayBotStore {
  doc_id: string | null;
  filename: string | null;
  full_text: string | null;
  chunks: Chunk[];
  selected_language: string;
  analysis_result: AnalysisResult | null;
  summary: SummariseResponse | null;
  conversation_history: ChatMessage[];
  setDocument: (doc_id: string, filename: string, full_text: string, chunks: Chunk[]) => void;
  setLanguage: (lang: string) => void;
  setAnalysis: (r: AnalysisResult) => void;
  setSummary: (s: SummariseResponse) => void;
  addMessage: (m: ChatMessage) => void;
  reset: () => void;
}

export const useStore = create<NyayBotStore>()(
  (set) => ({
    doc_id: null, filename: null, full_text: null, chunks: [],
    selected_language: "hi", analysis_result: null, summary: null,
    conversation_history: [],
    setDocument: (doc_id, filename, full_text, chunks) =>
      set({ doc_id, filename, full_text, chunks, analysis_result: null, summary: null, conversation_history: [] }),
    setLanguage: (lang) => set({ selected_language: lang }),
    setAnalysis: (r) => set({ analysis_result: r }),
    setSummary: (s) => set({ summary: s }),
    addMessage: (m) => set((st) => ({ conversation_history: [...st.conversation_history, m] })),
    reset: () => set({ doc_id: null, filename: null, full_text: null, chunks: [], analysis_result: null, summary: null, conversation_history: [] }),
  })
);
