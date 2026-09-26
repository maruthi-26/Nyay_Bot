"use client";
import { useState, useEffect, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import LanguageSelector from "@/components/LanguageSelector";
import { useStore } from "@/lib/store";
import { uploadPDF, embedDocument, analyseDocument, summariseDocument } from "@/lib/api";

const STEPS = [
  { id: 1, label: "Reading your document..." },
  { id: 2, label: "Scanning for risk clauses..." },
  { id: 3, label: "Preparing translation..." },
];

export default function HomePage() {
  const router = useRouter();
  const { selected_language, setDocument, setAnalysis, setSummary } = useStore();
  const [file, setFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<number[]>([]);
  const [error, setError] = useState("");
  const [wordIdx, setWordIdx] = useState(0);
  const fileRef = useRef<HTMLInputElement>(null);

  const CYCLE_WORDS = ["English", "हिंदी", "Telugu", "தமிழ்", "ಕನ್ನಡ", "বাংলা", "मराठी"];

  // cycle typewriter words
  useEffect(() => {
    const interval = setInterval(() => {
      setWordIdx((i) => (i + 1) % CYCLE_WORDS.length);
    }, 1800);
    return () => clearInterval(interval);
  }, []);

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f?.name.endsWith(".pdf")) setFile(f);
    else setError("Only PDF files are accepted.");
  }, []);

  const handleAnalyse = async () => {
    if (!file) return;
    setProcessing(true);
    setError("");
    setCompletedSteps([]);
    try {
      setCurrentStep(1);
      const uploaded = await uploadPDF(file);
      setDocument(uploaded.doc_id, uploaded.filename, uploaded.full_text, uploaded.chunks);
      setCompletedSteps([1]);

      setCurrentStep(2);
      // Run embedding, risk analysis, and 5-bullet summary simultaneously in parallel!
      const [_, analysis, summary] = await Promise.all([
        embedDocument(uploaded.doc_id, uploaded.chunks),
        analyseDocument(uploaded.doc_id, selected_language, uploaded.full_text),
        summariseDocument(uploaded.doc_id, selected_language, uploaded.full_text),
      ]);
      setCompletedSteps([1, 2]);

      setCurrentStep(3);
      setAnalysis(analysis);
      setSummary(summary);
      setCompletedSteps([1, 2, 3]);

      setTimeout(() => router.push("/results"), 300);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Something went wrong. Please try again.");
      setProcessing(false);
      setCurrentStep(0);
      setCompletedSteps([]);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-slate-800 bg-slate-900/80 backdrop-blur-sm px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-2xl">⚖️</span>
          <span className="text-xl font-bold text-amber-400" style={{ fontFamily: "'DM Serif Display', serif" }}>NyayBot</span>
          <span className="text-slate-500 text-sm hidden sm:block">न्याय for everyone</span>
        </div>
        <span className="text-slate-500 text-xs">Built for India • AI-generated information</span>
      </header>

      {/* Processing overlay */}
      {processing && (
        <div className="fixed inset-0 z-50 bg-slate-900/95 flex items-center justify-center">
          <div className="text-center space-y-6 max-w-sm px-6">
            <div className="text-4xl animate-pulse">⚖️</div>
            <h2 className="text-xl text-amber-400" style={{ fontFamily: "'DM Serif Display', serif" }}>Analysing your document</h2>
            <div className="space-y-3">
              {STEPS.map((s) => (
                <div key={s.id} className="flex items-center gap-3">
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs transition-all ${
                    completedSteps.includes(s.id) ? "bg-green-500 text-white" :
                    currentStep === s.id ? "bg-amber-400 text-slate-900 animate-pulse" :
                    "bg-slate-700 text-slate-200"
                  }`}>
                    {completedSteps.includes(s.id) ? "✓" : s.id}
                  </div>
                  <span className={`text-sm ${                  currentStep === s.id ? "text-amber-300" : completedSteps.includes(s.id) ? "text-green-400" : "text-slate-300"}`}>
                    {s.label}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Hero */}
      <main className="flex-1 px-6 py-16 max-w-4xl mx-auto w-full">
        <div className="text-center mb-12 space-y-4">
          <h1 className="text-4xl md:text-5xl leading-tight" style={{ fontFamily: "'DM Serif Display', serif" }}>
            Your Legal Document,<br />Finally In Plain{" "}
            <span className="text-amber-400 transition-all duration-500">{CYCLE_WORDS[wordIdx]}</span>
          </h1>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            Upload a text-based legal PDF. Get a plain-language summary, potential risk flags,
            and document-based answers in your language.
          </p>
          <div className="inline-flex items-center gap-2 bg-slate-800 border border-slate-700 rounded-full px-4 py-2 text-sm text-slate-400">
            <span>🔒</span>
            <span>Your document is never stored. Ever.</span>
          </div>
        </div>

        {/* Language picker */}
        <div className="mb-8">
          <p className="text-center text-slate-400 text-sm mb-4 font-medium">Choose your language</p>
          <LanguageSelector />
        </div>

        {/* Upload zone */}
        <div
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
          onClick={() => fileRef.current?.click()}
          className={`rounded-2xl border-2 border-dashed transition-all cursor-pointer p-12 text-center ${
            dragging ? "border-amber-400 bg-amber-400/5" :
            file ? "border-green-500 bg-green-500/5" :
            "border-slate-700 hover:border-slate-500 bg-slate-900/50"
          }`}
        >
          <input ref={fileRef} type="file" accept=".pdf" className="hidden" onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) { setFile(f); setError(""); }
          }} />
          {file ? (
            <div className="space-y-2">
              <div className="text-4xl">📄</div>
              <p className="text-green-400 font-medium">{file.name}</p>
              <p className="text-slate-500 text-sm">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="text-5xl opacity-40">📋</div>
              <p className="text-slate-300 text-lg">Drop your legal document here</p>
              <p className="text-slate-500">or click to browse</p>
              <span className="inline-block bg-slate-800 text-slate-200 text-xs px-3 py-1 rounded-full border border-slate-700">PDF files up to 10MB</span>
            </div>
          )}
        </div>

        {error && (
          <div className="mt-4 bg-red-900/30 border border-red-700 rounded-xl px-4 py-3 text-red-300 text-sm">{error}</div>
        )}

        {file && (
          <div className="mt-6 flex justify-center">
            <button
              onClick={handleAnalyse}
              disabled={processing}
              className="bg-amber-400 hover:bg-amber-300 text-slate-900 font-semibold px-8 py-4 rounded-xl text-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Analyse Document →
            </button>
          </div>
        )}

        {/* Stats bar */}
        <div className="mt-16 flex flex-wrap justify-center gap-6 text-slate-300 text-sm">
          <span>11 supported Indian languages</span>
          <span>•</span>
          <span>PDFs up to 10 MB</span>
          <span>•</span>
          <span>Scanned PDF OCR not yet supported</span>
        </div>
      </main>
    </div>
  );
}
