"use client";

import { useHoverPreview } from "@/components/hover-preview-context";
import { Meter } from "@/components/ds/page";
import { TierTag, TrendLabel } from "@/components/ds/tags";
import { fmtNum, fmtPct } from "@/lib/format";
import type { TierEntry } from "@/types";

// Colonnes : rang · vignette · nom · tier · barre · part · tendance.
// Sous 760 px, tier et barre disparaissent (docs/design-system.md §4).
const GRID =
  "grid grid-cols-[22px_34px_minmax(0,1fr)_54px_88px] gap-2.5 px-3 min-[760px]:grid-cols-[28px_40px_minmax(0,1.2fr)_60px_minmax(80px,1fr)_64px_92px] min-[760px]:gap-4 min-[760px]:px-4";

export function ArchetypeRow({
  entry,
  rank,
  maxScore,
  highlighted,
}: {
  entry: TierEntry;
  rank: number;
  maxScore: number;
  highlighted: boolean;
}) {
  const { setPreview } = useHoverPreview();

  return (
    <div
      onMouseEnter={() => entry.image_url && setPreview({ name: entry.archetype, imageUrl: entry.image_url })}
      onMouseLeave={() => setPreview(null)}
      className={`${GRID} items-center border-t border-line py-2 transition-colors duration-200 first:border-t-0 hover:bg-ink-3 ${
        highlighted
          ? "bg-[linear-gradient(90deg,color-mix(in_srgb,var(--signal)_9%,var(--ink)),var(--ink)_60%)]"
          : "bg-ink"
      }`}
    >
      <span className="font-mono text-[12px] text-faint tabular-nums">{String(rank).padStart(2, "0")}</span>

      {entry.image_url ? (
        // eslint-disable-next-line @next/next/no-img-element -- vignette externe (YGOPRODeck)
        <img
          src={entry.image_url}
          alt=""
          className="h-12 w-[34px] rounded-[3px] border border-line-2 object-cover"
        />
      ) : (
        <span className="grid h-12 w-[34px] place-items-center rounded-[3px] border border-line-2 bg-ink-4 font-mono text-[11px] text-muted-text">
          {entry.archetype.slice(0, 2).toUpperCase()}
        </span>
      )}

      <span className="min-w-0 font-medium tracking-[-0.01em] [overflow-wrap:anywhere]">
        {entry.archetype}
        <small className="block font-mono text-[11px] font-normal tracking-[0.04em] text-muted-text">
          score {fmtNum(entry.meta_score * 100, 1)}
        </small>
      </span>

      <span className="hidden min-[760px]:block">
        <TierTag tier={entry.tier} />
      </span>

      <span className="hidden min-[760px]:block">
        <Meter value={entry.meta_score} max={maxScore} />
      </span>

      <span className="text-right font-mono text-[14px] font-medium tabular-nums">{fmtPct(entry.share * 100)}</span>

      <span className="text-right">
        <TrendLabel trend={entry.trend} />
      </span>
    </div>
  );
}
