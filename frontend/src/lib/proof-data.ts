import type { ArchetypeMonth, ArchetypeResponse } from "@/types";

// Graphique « la preuve » de l'accueil : part mensuelle de Kewl Tune dans les decks
// de tournoi, en %, d'août 2025 à novembre 2026, en OCG et en TCG.
// Jusqu'à TOK-116 les valeurs étaient figées ici (relevé du 16/11/2026, décision 0041) ;
// elles viennent maintenant de GET /archetypes/kewl-tune (`history` pour le TCG,
// `ocg_history` pour l'OCG). La fenêtre reste fixe : les textes de l'accueil nomment
// ses mois (pic d'avril 2026, août 2025 à novembre 2026).
// Un 0 est un mois avec des decks mais sans Kewl Tune, pas un mois manquant.
export const PROOF_EXAMPLE = {
  archetype: "Kewl Tune",
  /** Slug servi par l'API (backend/app/slugs.py) : le front ne le recalcule pas. */
  slug: "kewl-tune",
  firstMonth: "2025-08",
  lastMonth: "2026-11",
} as const;

export interface Proof {
  archetype: string;
  /** Date de calcul de la chaîne OCG servie par l'API. */
  asOf: string;
  firstMonth: string;
  /** Parts en %, arrondies à 0,1 point (comme le relevé figé qu'elles remplacent). */
  ocg: number[];
  tcg: number[];
  /** Indices des pics (premier mois du maximum). */
  ocgPeak: number;
  tcgPeak: number;
  /**
   * Plus petit et plus grand effectif mensuel OCG (tous archétypes) de la fenêtre, lus dans `total_decks` :
   * la légende dit l'échelle de l'incertitude sans la dessiner. null si un mois de la fenêtre n'est pas servi
   * (l'historique TCG de Kewl Tune ne commence qu'en décembre 2025, d'où l'OCG seul).
   */
  ocgDecksRange: readonly [number, number] | null;
}

function monthsOf(first: string, last: string): string[] {
  const [y0, m0] = first.split("-").map(Number);
  const [y1, m1] = last.split("-").map(Number);
  const out: string[] = [];
  for (let i = 0; i <= (y1 - y0) * 12 + (m1 - m0); i++) {
    const d = new Date(y0, m0 - 1 + i, 1);
    out.push(`${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`);
  }
  return out;
}

const argmax = (values: number[]) => values.reduce((best, v, i) => (v > values[best] ? i : best), 0);

/**
 * Parts de la fenêtre à partir de l'historique servi, qui commence au premier mois où
 * l'archétype apparaît dans le format : un mois antérieur vaut donc 0. null si la série
 * n'atteint pas le dernier mois de la fenêtre ou s'il lui manque un mois.
 */
function series(history: ArchetypeMonth[], months: string[]) {
  if (!history.length || history[history.length - 1].month < months[months.length - 1]) return null;
  const byMonth = new Map(history.map((m) => [m.month, m]));
  const start = history[0].month;
  const shares = months.map((month) => {
    const m = byMonth.get(month);
    if (m) return m.total_decks ? Math.round((m.decks / m.total_decks) * 1000) / 10 : 0;
    return month < start ? 0 : null;
  });
  return shares.some((v) => v === null) ? null : (shares as number[]);
}

function totalsRange(history: ArchetypeMonth[], months: string[]): readonly [number, number] | null {
  const byMonth = new Map(history.map((m) => [m.month, m.total_decks]));
  const totals = months.map((month) => byMonth.get(month));
  if (totals.some((n) => n === undefined || n <= 0)) return null;
  return [Math.min(...(totals as number[])), Math.max(...(totals as number[]))] as const;
}

/** null si l'API ne couvre pas toute la fenêtre (base de service antérieure à TOK-116). */
export function buildProof(response: ArchetypeResponse | null): Proof | null {
  if (!response || !response.ocg_history_computed_at) return null;
  const months = monthsOf(PROOF_EXAMPLE.firstMonth, PROOF_EXAMPLE.lastMonth);
  const ocg = series(response.ocg_history, months);
  const tcg = series(response.history, months);
  if (!ocg || !tcg) return null;
  const ocgPeak = argmax(ocg);
  const tcgPeak = argmax(tcg);
  // Le texte de l'accueil cite les trois mois qui précèdent chaque pic.
  if (ocgPeak < 3 || tcgPeak < 3) return null;
  return {
    archetype: response.archetype,
    asOf: response.ocg_history_computed_at,
    firstMonth: PROOF_EXAMPLE.firstMonth,
    ocg,
    tcg,
    ocgPeak,
    tcgPeak,
    ocgDecksRange: totalsRange(response.ocg_history, months),
  };
}
