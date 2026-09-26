import type { UploadResponse, AnalysisResult, AskResponse, SummariseResponse, Language, ChatMessage, Chunk } from "./types";

const configuredBase = process.env.NEXT_PUBLIC_API_URL?.trim();
const BASE = configuredBase
  ? (/^https?:\/\//i.test(configuredBase) ? configuredBase : `https://${configuredBase}`).replace(/\/+$/, "")
  : process.env.NODE_ENV === "development"
    ? "http://localhost:8000"
    : null;

function apiUrl(path: string): string {
  if (!BASE) {
    throw new Error("The API URL is not configured. Set NEXT_PUBLIC_API_URL to the deployed backend URL and rebuild the frontend.");
  }
  return `${BASE}${path}`;
}

async function post<T>(path: string, body: object): Promise<T> {
  const res = await fetch(apiUrl(path), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

export async function uploadPDF(file: File): Promise<UploadResponse> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(apiUrl("/upload"), { method: "POST", body: form });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(err.detail || "Upload failed");
  }
  return res.json();
}

export async function embedDocument(doc_id: string, chunks: UploadResponse["chunks"]): Promise<void> {
  await post("/embed", { doc_id, chunks });
}

export async function analyseDocument(doc_id: string, language: string, full_text: string): Promise<AnalysisResult> {
  return post("/analyse", { doc_id, language, full_text });
}

export async function summariseDocument(doc_id: string, language: string, full_text: string): Promise<SummariseResponse> {
  return post("/summarise", { doc_id, language, full_text });
}

export async function askQuestion(
  doc_id: string, question: string, language: string,
  conversation_history: ChatMessage[],
  chunks?: Chunk[]
): Promise<AskResponse> {
  try {
    return await post("/ask", { doc_id, question, language, conversation_history, chunks });
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : String(err);
    if (errorMsg.includes("not indexed") && chunks && chunks.length > 0) {
      await embedDocument(doc_id, chunks);
      return await post("/ask", { doc_id, question, language, conversation_history, chunks });
    }
    throw err;
  }
}

export async function translateText(text: string, target_lang: string): Promise<{ translated_text: string }> {
  return post("/translate", { text, target_lang });
}

export async function getAudio(text: string, lang: string): Promise<{ audio_base64: string | null; provider: string }> {
  return post("/speak", { text, lang });
}

export async function getLanguages(): Promise<Language[]> {
  const res = await fetch(apiUrl("/languages"));
  return res.json();
}

export function playBase64Audio(base64: string) {
  const audio = new Audio(`data:audio/wav;base64,${base64}`);
  audio.play();
  return audio;
}

export function speakWithBrowser(text: string, langCode: string) {
  if (!("speechSynthesis" in window)) return;
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = langCode;
  window.speechSynthesis.speak(utterance);
}
