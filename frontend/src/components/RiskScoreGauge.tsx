"use client";
import { useEffect, useRef } from "react";

interface Props { score: number; color: string; }

export default function RiskScoreGauge({ score, color }: Props) {
  const numRef = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    let start = 0;
    const end = score;
    const duration = 2000;
    const step = (timestamp: number, startTime: number) => {
      const progress = Math.min((timestamp - startTime) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      if (numRef.current) numRef.current.textContent = Math.round(eased * end).toString();
      if (progress < 1) requestAnimationFrame((ts) => step(ts, startTime));
    };
    requestAnimationFrame((ts) => step(ts, ts));
  }, [score]);

  const radius = 80;
  const stroke = 12;
  const normalizedRadius = radius - stroke / 2;
  const circumference = 2 * Math.PI * normalizedRadius;
  const dash = (score / 10) * circumference;

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative" style={{ width: 200, height: 200 }}>
        <svg width="200" height="200" viewBox="0 0 200 200">
          <circle cx="100" cy="100" r={normalizedRadius} fill="none" stroke="#1e293b" strokeWidth={stroke} />
          <circle
            cx="100" cy="100" r={normalizedRadius} fill="none"
            stroke={color} strokeWidth={stroke}
            strokeDasharray={`${dash} ${circumference}`}
            strokeLinecap="round"
            transform="rotate(-90 100 100)"
            style={{ transition: "stroke-dasharray 2s ease-out" }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span ref={numRef} style={{ color, fontSize: 52, fontWeight: 700, lineHeight: 1 }}>0</span>
          <span className="text-slate-400 text-sm">/10</span>
        </div>
      </div>
    </div>
  );
}
