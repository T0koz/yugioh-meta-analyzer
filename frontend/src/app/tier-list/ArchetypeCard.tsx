"use client";

import { useHoverPreview } from "@/components/hover-preview-context";
import type { Tier, TierEntry, Trend } from "@/types";

const TIER_BADGE: Record<Tier, string> = {
  T0: "bg-red-500 text-white",
  T1: "bg-orange-400 text-white",
  T2: "bg-yellow-400 text-black",
  T3: "bg-blue-400 text-white",
  Rogue: "bg-slate-400 text-slate-900",
};

const TREND_ICON: Record<Trend, string> = { Rising: "↑", Stable: "→", Declining: "↓" };
const TREND_COLOR: Record<Trend, string> = {
  Rising: "text-green-500",
  Stable: "text-slate-400",
  Declining: "text-red-400",
};

export function ArchetypeCard({ entry, maxScore }: { entry: TierEntry; maxScore: number }) {
  const { setPreview } = useHoverPreview();
  const scorePct = maxScore > 0 ? (entry.meta_score / maxScore) * 100 : 0;

  return (
    <div
      onMouseEnter={() => entry.image_url && setPreview({ name: entry.archetype, imageUrl: entry.image_url })}
      onMouseLeave={() => setPreview(null)}
      className="flex h-24 rounded-xl border border-slate-800 bg-slate-900 overflow-hidden cursor-default"
    >
      <div
        className="w-1/4 shrink-0 relative bg-slate-800 bg-cover bg-center"
        style={{
          backgroundImage: entry.image_url ? `url(${entry.image_url})` : undefined,
        }}
      >
        <span
          className={`absolute top-1.5 left-1.5 text-[10px] font-bold px-1.5 py-0.5 rounded ${TIER_BADGE[entry.tier]}`}
        >
          {entry.tier}
        </span>
      </div>
      <div className="w-3/4 px-3.5 py-2.5 flex flex-col justify-center gap-1.5 min-w-0">
        <p className="text-sm font-medium truncate">{entry.archetype}</p>
        <div>
          <div className="flex justify-between text-[11px] text-slate-500 mb-0.5">
            <span>Meta score</span>
            <span className="text-slate-300 tabular-nums">{(entry.meta_score * 100).toFixed(1)}</span>
          </div>
          <div className="h-1 rounded-full bg-slate-700 overflow-hidden">
            <div className="h-full bg-indigo-400 rounded-full" style={{ width: `${scorePct}%` }} />
          </div>
        </div>
        <div className="flex justify-between items-center text-[11px]">
          <span className="text-slate-400 tabular-nums">{(entry.share * 100).toFixed(1)}% share</span>
          <span className={`font-semibold ${TREND_COLOR[entry.trend]}`}>
            {TREND_ICON[entry.trend]} {entry.trend}
          </span>
        </div>
      </div>
    </div>
  );
}
