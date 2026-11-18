import { wilsonInterval } from "@/lib/wilson";
import type { TierEntry, TierThreshold } from "@/types";

// Tier « à la limite » (audit de rigueur, A8, lot 20) : l'intervalle de Wilson à 95 % de la part
// contient un seuil de tier, donc le tier affiché pourrait être celui d'à côté avec d'autres decks.
// Seuils servis par l'API (app/tiering.py) ; Wilson calculé ici, dans son seul module (lib/wilson.ts).
// Sous `minDecks` decks, l'archétype est Rogue d'office : pas de marquage.
export function tierLimit(
  entry: TierEntry,
  nDecks: number,
  thresholds: TierThreshold[] | undefined,
  minDecks: number | null | undefined,
): TierThreshold | null {
  if (!thresholds?.length || entry.decks < (minDecks ?? 0)) return null;
  const [lo, hi] = wilsonInterval(entry.decks, nDecks);
  return thresholds.find((t) => lo < t.share && t.share < hi) ?? null;
}
