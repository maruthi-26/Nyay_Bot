"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useStore } from "@/lib/store";
import RiskScoreGauge from "@/components/RiskScoreGauge";
import FlagCard from "@/components/FlagCard";
import { getAudio, playBase64Audio, speakWithBrowser } from "@/lib/api";

const REC_STYLES: Record<string, { bg: string; text: string; label: string }> = {
  SAFE_TO_SIGN:         { bg: "bg-green-900/40 border-green-700",  text: "text-green-300",  label: "✓ Generally safe to sign" },
  REVIEW_RECOMMENDED:   { bg: "bg-amber-900/40 border-amber-700",  text: "text-amber-300",  label: "⚠ Review before signing" },
  DO_NOT_SIGN:          { bg: "bg-red-900/40 border-red-700",      text: "text-red-300",    label: "✗ Do not sign without legal advice" },
};

export default function ResultsPage() {
  const router = useRouter();
  const { analysis_result, summary, filename, doc_id } = useStore();
  const [summaryCardText, setSummaryCardText] = useState("");
  const [showCard, setShowCard] = useState(false);
  const [speakingIdx, setSpeakingIdx] = useState<number | null>(null);

  useEffect(() => {
    if (!doc_id || !analysis_result) router.push("/");
  }, [doc_id, analysis_result, router]);

  if (!analysis_result || !summary) {
    return <div className="min-h-screen flex items-center justify-center text-slate-400">Loading...</div>;
  }

  const rec = REC_STYLES[analysis_result.signing_recommendation] || REC_STYLES.REVIEW_RECOMMENDED;

  const handleSpeakBullet = async (text: string, idx: number) => {
    setSpeakingIdx(idx);
    try {
      const { audio_base64 } = await getAudio(text, analysis_result.language);
      if (audio_base64) {
        const audio = playBase64Audio(audio_base64);
        audio.onended = () => setSpeakingIdx(null);
      } else {
        speakWithBrowser(text, analysis_result.language);
        setTimeout(() => setSpeakingIdx(null), 3000);
      }
    } catch {
      setSpeakingIdx(null);
    }
  };

  return (
    <div className="min-h-screen" style={{ background: "#0A0F1E" }}>
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-slate-800 bg-slate-900/80 backdrop-blur-sm px-6 py-4 flex items-center justify-between">
        <button onClick={() => router.push("/")} className="text-amber-400 text-sm hover:underline">← New document</button>
        <span className="text-slate-400 text-sm truncate max-w-xs">{filename}</span>
        <button onClick={() => router.push("/chat")} className="bg-amber-400 text-slate-900 text-sm font-semibold px-4 py-2 rounded-lg hover:bg-amber-300 transition-colors">
          💬 Ask questions →
        </button>
      </header>

      <div className="max-w-3xl mx-auto px-6 py-10 space-y-10">

        {/* Risk Score Hero */}
        <div className="text-center space-y-4 fade-in">
          <h2 className="text-slate-400 text-sm font-medium uppercase tracking-widest">Document Risk Score</h2>
          <RiskScoreGauge score={analysis_result.overall_risk_score} color={analysis_result.risk_colour.hex_color} />
          <p className="text-slate-300 text-lg max-w-xl mx-auto leading-relaxed">{analysis_result.overall_verdict}</p>
          <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full border text-sm font-medium ${rec.bg} ${rec.text}`}>
            {rec.label}
          </div>
        </div>

        {/* Risk counts */}
        <div className="grid grid-cols-3 gap-4">
          {[
            { label: "High Risk", count: analysis_result.risk_counts.high, color: "text-red-400", bg: "bg-red-900/20 border-red-800/40" },
            { label: "Medium Risk", count: analysis_result.risk_counts.medium, color: "text-amber-400", bg: "bg-amber-900/20 border-amber-800/40" },
            { label: "Low Risk", count: analysis_result.risk_counts.low, color: "text-green-400", bg: "bg-green-900/20 border-green-800/40" },
          ].map((item) => (
            <div key={item.label} className={`rounded-xl border p-4 text-center ${item.bg}`}>
              <div className={`text-2xl font-bold ${item.color}`}>{item.count}</div>
              <div className="text-slate-400 text-xs mt-1">{item.label}</div>
            </div>
          ))}
        </div>

        {/* Document type */}
        <div className="flex items-center gap-2 text-sm">
          <span className="text-slate-500">Document type:</span>
          <span className="bg-slate-800 border border-slate-700 text-slate-300 px-3 py-1 rounded-full text-xs">{analysis_result.document_type}</span>
        </div>

        {/* Summary bullets */}
        <div id="summary-section" className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-3 scroll-mt-24">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-amber-400 font-semibold" style={{ fontFamily: "'DM Serif Display', serif", fontSize: 20 }}>
              What this document says
            </h3>
            <span className="text-xs text-slate-500">Plain Language Summary</span>
          </div>
          {summary.summary_bullets.map((bullet, i) => (
            <div key={i} className={`flex items-start gap-3 fade-in stagger-${i + 1}`}>
              <span className="text-amber-400 mt-1 text-sm">📌</span>
              <p className="text-slate-300 text-sm leading-relaxed flex-1">{bullet}</p>
              <button
                onClick={() => handleSpeakBullet(bullet, i)}
                disabled={speakingIdx === i}
                className="text-slate-600 hover:text-amber-400 transition-colors text-xs shrink-0 disabled:animate-pulse"
                title="Listen in your language"
              >
                🔊
              </button>
            </div>
          ))}
        </div>

        {/* Flagged clauses */}
        <div className="space-y-4">
          <h3 className="font-semibold text-slate-200" style={{ fontFamily: "'DM Serif Display', serif", fontSize: 20 }}>
            Clauses to watch out for
          </h3>
          {analysis_result.flags.length === 0 ? (
            <div className="bg-green-900/20 border border-green-800/40 rounded-xl p-6 text-green-300 text-center">
              ✓ No significant risk clauses detected in this document.
            </div>
          ) : (
            analysis_result.flags.map((flag, i) => <FlagCard key={i} flag={flag} />)
          )}
        </div>

        {/* Action buttons */}
        <div className="flex flex-wrap gap-4 pt-4">
          <button
            onClick={() => router.push("/chat")}
            className="flex-1 bg-amber-400 hover:bg-amber-300 text-slate-900 font-semibold px-6 py-3 rounded-xl transition-colors"
          >
            💬 Ask a question
          </button>
          <button
            onClick={() => {
              const text = summary.summary_bullets.map((b) => `• ${b}`).join("\n\n");
              setSummaryCardText(text);
              setShowCard(true);
              document.getElementById("summary-section")?.scrollIntoView({ behavior: "smooth" });
            }}
            className="flex-1 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 font-medium px-6 py-3 rounded-xl transition-colors"
          >
            📄 Summary card
          </button>
        </div>
      </div>

      {/* Summary card modal - Fixed centered in viewport */}
      {showCard && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in"
          onClick={() => setShowCard(false)}
        >
          <div
            className="bg-slate-900 border border-slate-700 rounded-2xl p-6 max-w-lg w-full space-y-4 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-amber-400 font-semibold text-lg" style={{ fontFamily: "'DM Serif Display', serif" }}>
                📄 Document Summary Card
              </h3>
              <button
                onClick={() => setShowCard(false)}
                className="text-slate-400 hover:text-white text-lg font-bold w-7 h-7 rounded-full flex items-center justify-center hover:bg-slate-800"
              >
                ✕
              </button>
            </div>
            <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-4 max-h-96 overflow-y-auto space-y-3">
              {summary.summary_bullets.map((bullet, idx) => (
                <div key={idx} className="flex items-start gap-2.5 text-sm text-slate-200">
                  <span className="text-amber-400 shrink-0 mt-0.5">📌</span>
                  <p className="leading-relaxed">{bullet}</p>
                </div>
              ))}
            </div>
            <div className="flex gap-3 pt-2">
              <button
                onClick={() => {
                  navigator.clipboard.writeText(summaryCardText);
                  alert("Summary copied to clipboard!");
                }}
                className="flex-1 bg-amber-400 text-slate-900 font-semibold py-2.5 rounded-xl text-sm hover:bg-amber-300 transition-colors flex items-center justify-center gap-2"
              >
                📋 Copy summary
              </button>
              <button
                onClick={() => {
                  setShowCard(false);
                  document.getElementById("summary-section")?.scrollIntoView({ behavior: "smooth" });
                }}
                className="px-4 py-2.5 border border-slate-700 text-slate-300 hover:bg-slate-800 rounded-xl text-sm transition-colors"
              >
                View on page
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
