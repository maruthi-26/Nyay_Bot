"use client";
import type { ChatMessage } from "@/lib/types";
import { getAudio, playBase64Audio, speakWithBrowser } from "@/lib/api";
import { useState } from "react";

interface Props { message: ChatMessage; lang: string; }

export default function ChatBubble({ message, lang }: Props) {
  const [playing, setPlaying] = useState(false);
  const isUser = message.role === "user";

  const handleSpeak = async () => {
    setPlaying(true);
    try {
      const { audio_base64, provider } = await getAudio(message.content, lang);
      if (audio_base64) {
        const audio = playBase64Audio(audio_base64);
        audio.onended = () => setPlaying(false);
      } else {
        speakWithBrowser(message.content, lang);
        setTimeout(() => setPlaying(false), 3000);
      }
    } catch {
      speakWithBrowser(message.content, lang);
      setTimeout(() => setPlaying(false), 3000);
    }
  };

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="bg-amber-500 text-slate-900 rounded-2xl rounded-tr-sm px-4 py-3 max-w-xs md:max-w-md text-sm font-medium">
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start">
      <div className="bg-slate-800 border border-slate-700 rounded-2xl rounded-tl-sm px-4 py-3 max-w-xs md:max-w-lg space-y-2">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-amber-400 text-xs font-semibold">⚖ NyayBot</span>
        </div>
        <p className="text-slate-200 text-sm leading-relaxed">{message.content}</p>
        {message.sources && message.sources.length > 0 && (
          <p className="text-slate-500 text-xs">Source: {message.sources.map(s => s.chunk_id).join(", ")}</p>
        )}
        <button
          onClick={handleSpeak}
          disabled={playing}
          className="flex items-center gap-1.5 text-slate-400 hover:text-amber-400 text-xs transition-colors disabled:opacity-50"
        >
          <span>{playing ? "🔊" : "🔈"}</span>
          <span>{playing ? "Playing..." : "Listen"}</span>
        </button>
      </div>
    </div>
  );
}
