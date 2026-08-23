"use client";
import { useStore } from "@/lib/store";

const LANGUAGES = [
  { code:"en", name:"English", native:"English" },
  { code:"hi", name:"Hindi", native:"हिंदी" },
  { code:"te", name:"Telugu", native:"తెలుగు" },
  { code:"ta", name:"Tamil", native:"தமிழ்" },
  { code:"kn", name:"Kannada", native:"ಕನ್ನಡ" },
  { code:"bn", name:"Bengali", native:"বাংলা" },
  { code:"mr", name:"Marathi", native:"मराठी" },
  { code:"gu", name:"Gujarati", native:"ગુજરાતી" },
  { code:"ml", name:"Malayalam", native:"മലയാളം" },
  { code:"pa", name:"Punjabi", native:"ਪੰਜਾਬੀ" },
  { code:"or", name:"Odia", native:"ଓଡ଼ିଆ" },
];

export default function LanguageSelector() {
  const { selected_language, setLanguage } = useStore();
  return (
    <div className="flex flex-wrap gap-2 justify-center">
      {LANGUAGES.map((l) => (
        <button
          key={l.code}
          onClick={() => setLanguage(l.code)}
          className={`px-3 py-2 rounded-lg border text-center transition-all ${
            selected_language === l.code
              ? "border-amber-400 bg-amber-400/10 text-amber-300"
              : "border-slate-700 text-slate-400 hover:border-slate-500"
          }`}
        >
          <div className="text-base font-medium">{l.native}</div>
          <div className="text-xs opacity-60">{l.name}</div>
        </button>
      ))}
    </div>
  );
}
