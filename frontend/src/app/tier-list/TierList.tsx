"use client";

import { useState } from "react";
import { Toolbar, pillClass } from "@/components/ds/page";
import type { TierEntry } from "@/types";
import { ArchetypeRow } from "./ArchetypeRow";

const FILTERS: { id: string; label: string; keep: (entry: TierEntry) => boolean }[] = [
  { id: "all", label: "Tous", keep: () => true },
  { id: "ranked", label: "T0–T3", keep: (e) => e.tier !== "Rogue" },
  { id: "rogue", label: "Rogue", keep: (e) => e.tier === "Rogue" },
  { id: "rising", label: "En hausse", keep: (e) => e.trend === "Rising" },
];

export function TierList({ data }: { data: TierEntry[] }) {
  const [filterId, setFilterId] = useState("all");
  const filter = FILTERS.find((f) => f.id === filterId) ?? FILTERS[0];

  // meta_score = sqrt(share × placement_score_norm) ne dépasse jamais ~0.15 en pratique :
  // la barre est calibrée en relatif au max du snapshot (pas du filtre) plutôt qu'en absolu sur [0,1].
  const maxScore = Math.max(...data.map((d) => d.meta_score), 0);
  // Le rang reste celui de la liste complète : filtrer ne renumérote pas.
  const rows = data.map((entry, i) => ({ entry, rank: i + 1 })).filter(({ entry }) => filter.keep(entry));

  return (
    <section>
      <Toolbar count={`${rows.length} / ${data.length} archétypes`}>
        {FILTERS.map((f) => (
          <button
            key={f.id}
            type="button"
            aria-pressed={f.id === filterId}
            onClick={() => setFilterId(f.id)}
            className={pillClass(f.id === filterId)}
          >
            {f.label}
          </button>
        ))}
      </Toolbar>

      <div className="overflow-hidden rounded-[6px] border border-line">
        {rows.map(({ entry, rank }) => (
          <ArchetypeRow key={entry.archetype} entry={entry} rank={rank} maxScore={maxScore} highlighted={rank === 1} />
        ))}
        {rows.length === 0 && (
          <p className="px-4 py-6 font-mono text-[12px] text-muted-text">Aucun archétype dans ce filtre.</p>
        )}
      </div>
    </section>
  );
}
