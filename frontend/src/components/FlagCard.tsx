"use client";
import { useState } from "react";
import type { RiskFlag } from "@/lib/types";

const SEVERITY_STYLES: Record<string, string> = {
  HIGH: "border-red-500 bg-red-500/5",
  MEDIUM: "border-amber-500 bg-amber-500/5",
  LOW: "border-slate-600 bg-slate-800/40",
};
const BADGE_STYLES: Record<string, string> = {
  HIGH: "bg-red-900/60 text-red-300 border border-red-700",
  MEDIUM: "bg-amber-900/60 text-amber-300 border border-amber-700",
  LOW: "bg-slate-700 text-slate-300 border border-slate-600",
};

export default function FlagCard({ flag }: { flag: RiskFlag }) {
  const [open, setOpen] = useState(false);
  return (
    <div className={`rounded-xl border-l-4 ${SEVERITY_STYLES[flag.severity]} cursor-pointer`} onClick={() => setOpen(!open)}>
      <div className="flex items-start justify-between gap-3 p-4">
        <div className="flex items-start gap-3">
          <span className={`text-xs font-semibold px-2 py-1 rounded-md shrink-0 ${BADGE_STYLES[flag.severity]}`}>{flag.severity}</span>
          <p className="text-slate-300 text-sm leading-relaxed">{flag.clause_text.slice(0, 100)}{flag.clause_text.length > 100 ? "..." : ""}</p>
        </div>
        <span className="text-slate-500 text-lg shrink-0">{open ? "−" : "+"}</span>
      </div>
      {open && (
        <div className="px-4 pb-4 border-t border-slate-700/50 pt-3 space-y-3">
          <div className="bg-slate-900/60 rounded-lg p-3 text-slate-400 text-sm italic border-l-2 border-slate-600">
            &ldquo;{flag.clause_text}&rdquo;
          </div>
          <p className="text-slate-200 text-sm leading-relaxed">{flag.plain_explanation}</p>
          {flag.indian_law_context && (
            <div className="flex items-center gap-2">
              <span className="text-xs bg-blue-900/50 text-blue-300 border border-blue-700 px-2 py-1 rounded-md">Indian Law</span>
              <span className="text-slate-400 text-xs">{flag.indian_law_context}</span>
            </div>
          )}
          <div className="bg-amber-900/20 border border-amber-800/40 rounded-lg p-3">
            <p className="text-amber-300 text-xs font-semibold mb-1">Ask a lawyer:</p>
            <p className="text-amber-200 text-sm italic">{flag.lawyer_question}</p>
          </div>
        </div>
      )}
    </div>
  );
}
