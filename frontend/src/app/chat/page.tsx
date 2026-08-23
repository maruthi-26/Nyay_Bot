"use client";
import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useStore } from "@/lib/store";
import ChatBubble from "@/components/ChatBubble";
import { askQuestion } from "@/lib/api";
import type { ChatMessage } from "@/lib/types";

const SUGGESTIONS: Record<string, string[]> = {
  te: ["నా హక్కులు ఏమిటి?", "నేను ముందే వదిలిపోవచ్చా?", "ముఖ్యమైన తేదీలు ఏవి?", "ఏ నిబంధనలు నాకు హాని చేయవచ్చు?"],
  hi: ["मेरे क्या अधिकार हैं?", "क्या मैं जल्दी छोड़ सकता हूं?", "महत्वपूर्ण तारीखें क्या हैं?", "कौन से खंड मुझे नुकसान पहुंचा सकते हैं?"],
  ta: ["என் உரிமைகள் என்ன?", "முன்னதாக விடலாமா?", "முக்கியமான தேதிகள் என்ன?", "எந்த விதிகள் என்னை பாதிக்கலாம்?"],
  kn: ["ನನ್ನ ಹಕ್ಕುಗಳೇನು?", "ಮೊದಲೇ ಬಿಡಬಹುದೇ?", "ಪ್ರಮುಖ ದಿನಾಂಕಗಳು ಯಾವುವು?", "ಯಾವ ನಿಯಮಗಳು ನನಗೆ ಹಾನಿ ಮಾಡಬಹುದು?"],
  en: ["What are my rights?", "Can I leave early?", "What are the key dates?", "Which clauses could harm me?"],
};

export default function ChatPage() {
  const router = useRouter();
  const { doc_id, filename, selected_language, analysis_result, conversation_history, chunks, addMessage } = useStore();
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => { if (!doc_id) router.push("/"); }, [doc_id, router]);
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [conversation_history]);

  const suggestions = SUGGESTIONS[selected_language] || SUGGESTIONS.en;

  const send = async (text: string) => {
    if (!text.trim() || !doc_id) return;
    const userMsg: ChatMessage = { role: "user", content: text };
    addMessage(userMsg);
    setInput("");
    setLoading(true);
    setError("");
    try {
      const res = await askQuestion(doc_id, text, selected_language, [...conversation_history, userMsg], chunks);
      addMessage({ role: "assistant", content: res.answer, sources: res.source_chunks });
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Could not get an answer. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleMic = () => {
    if (typeof window === "undefined" || !("webkitSpeechRecognition" in window || "SpeechRecognition" in window)) {
      alert("Speech recognition not supported in this browser. Please type your question.");
      return;
    }
    const win = window as any;
    const SR = win.SpeechRecognition || win.webkitSpeechRecognition;
    if (!SR) return;
    const recognition = new SR();
    recognition.lang = selected_language;
    recognition.start();
    recognition.onresult = (e: any) => {
      if (e.results?.[0]?.[0]?.transcript) {
        setInput(e.results[0][0].transcript);
      }
    };
  };

  return (
    <div className="min-h-screen flex flex-col" style={{ background: "#0A0F1E" }}>
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-slate-800 bg-slate-900/80 backdrop-blur-sm px-6 py-3 flex items-center justify-between gap-4">
        <button onClick={() => router.push("/results")} className="text-amber-400 text-sm hover:underline shrink-0">← Results</button>
        <div className="flex items-center gap-3 overflow-hidden">
          <span className="text-slate-400 text-sm truncate">{filename}</span>
          {analysis_result && (
            <span className="shrink-0 text-xs px-2 py-1 rounded-full font-semibold" style={{
              background: analysis_result.risk_colour.hex_color + "22",
              color: analysis_result.risk_colour.hex_color,
              border: `1px solid ${analysis_result.risk_colour.hex_color}55`
            }}>
              {analysis_result.overall_risk_score}/10
            </span>
          )}
        </div>
        <div className="shrink-0 text-xs bg-slate-800 border border-slate-700 px-2 py-1 rounded-full text-slate-400">
          {selected_language.toUpperCase()}
        </div>
      </header>

      {/* Chat messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 max-w-2xl mx-auto w-full space-y-4">
        {conversation_history.length === 0 && (
          <div className="space-y-6">
            <div className="text-center">
              <div className="text-4xl mb-3">⚖️</div>
              <h2 className="text-slate-300 text-lg" style={{ fontFamily: "'DM Serif Display', serif" }}>Ask anything about your document</h2>
              <p className="text-slate-500 text-sm mt-1">I&apos;ll answer based only on what&apos;s in your document.</p>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {suggestions.map((s, i) => (
                <button
                  key={i}
                  onClick={() => send(s)}
                  className={`text-left p-3 rounded-xl border border-slate-700 bg-slate-900 hover:border-amber-500/50 hover:bg-amber-500/5 text-slate-300 text-sm transition-all fade-in stagger-${i + 1}`}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {conversation_history.map((msg, i) => (
          <ChatBubble key={i} message={msg} lang={selected_language} />
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-slate-800 border border-slate-700 rounded-2xl rounded-tl-sm px-4 py-3">
              <div className="flex gap-1">
                {[0, 1, 2].map((i) => (
                  <div key={i} className="w-2 h-2 bg-amber-400 rounded-full animate-bounce" style={{ animationDelay: `${i * 0.15}s` }} />
                ))}
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-900/30 border border-red-700 rounded-xl px-4 py-3 text-red-300 text-sm">{error}</div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Disclaimer */}
      <div className="border-t border-slate-800 bg-slate-900/60 px-6 py-2 text-center text-slate-500 text-xs">
        NyayBot provides information, not legal advice. For important decisions, always consult a qualified lawyer.
      </div>

      {/* Input bar */}
      <div className="border-t border-slate-800 bg-slate-900 px-4 py-3">
        <div className="max-w-2xl mx-auto flex gap-3 items-end">
          <div className="flex-1 bg-slate-800 border border-slate-700 rounded-xl flex items-center gap-2 px-4 py-3">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && send(input)}
              placeholder="Ask anything about your document..."
              className="flex-1 bg-transparent text-slate-200 text-sm outline-none placeholder-slate-500"
            />
            <button onClick={handleMic} className="text-slate-500 hover:text-amber-400 transition-colors text-lg" title="Voice input">🎤</button>
          </div>
          <button
            onClick={() => send(input)}
            disabled={!input.trim() || loading}
            className="bg-amber-400 hover:bg-amber-300 text-slate-900 font-bold px-4 py-3 rounded-xl transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            →
          </button>
        </div>
      </div>
    </div>
  );
}
