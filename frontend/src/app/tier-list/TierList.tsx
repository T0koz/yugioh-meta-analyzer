"use client";

import { useState } from "react";
import { Pill } from "@/components/ds/control";
import { Toolbar } from "@/components/ds/page";
import { wilsonInterval } from "@/lib/wilson";
import { tierLimit } from "@/lib/tiers";
import type { TierEntry, TierThreshold } from "@/types";
import { ArchetypeRow } from "./ArchetypeRow";

const FILTERS: { id: string; label: string; keep: (entry: TierEntry) => boolean }[] = [
  { id: "all", label: "Tous", keep: () => true },
  { id: "ranked", label: "T0–T3", keep: (e) => e.tier !== "Rogue" },
  { id: "rogue", label: "Rogue", keep: (e) => e.tier === "Rogue" },
  { id: "rising", label: "En hausse", keep: (e) => e.trend === "Rising" },
];

export function TierList({
  data,
  nDecks,
  thresholds,
  minDecks,
}: {
  data: TierEntry[];
  nDecks: number;
  thresholds?: TierThreshold[];
  minDecks?: number | null;
}) {
  const [filterId, setFilterId] = useState("all");
  const filter = FILTERS.find((f) => f.id === filterId) ?? FILTERS[0];

  // La barre montre la part de méta (la mesure sur laquelle la liste est triée) et
  // son intervalle à 95 %, sur une échelle commune qui s'arrête à la plus haute
  // borne de la liste complète (pas du filtre).
  const maxShare = Math.max(...data.map((d) => wilsonInterval(d.decks, nDecks)[1]), 0);
  // Le rang reste celui de la liste complète : filtrer ne renumérote pas.
  const rows = data.map((entry, i) => ({ entry, rank: i + 1 })).filter(({ entry }) => filter.keep(entry));

  return (
    <section>
      <Toolbar count={`${rows.length} / ${data.length} archétypes`}>
        {FILTERS.map((f) => (
          <Pill key={f.id} pressed={f.id === filterId} onClick={() => setFilterId(f.id)}>
            {f.label}
          </Pill>
        ))}
      </Toolbar>

      <div className="overflow-hidden rounded-[6px] border border-line">
        {rows.map(({ entry, rank }) => (
          <ArchetypeRow
            key={entry.archetype}
            entry={entry}
            rank={rank}
            nDecks={nDecks}
            maxShare={maxShare}
            limit={tierLimit(entry, nDecks, thresholds, minDecks)}
            highlighted={rank === 1}
          />
        ))}
        {rows.length === 0 && (
          <p className="px-4 py-6 font-mono text-[12px] text-muted-text">Aucun archétype dans ce filtre.</p>
        )}
      </div>
    </section>
  );
}
