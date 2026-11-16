// Intervalle de Wilson pour une proportion k / n (lot 15, charte §3).
//
// Seul endroit du site où cet intervalle est calculé : les bandes d'incertitude des
// parts mensuelles (/evolution, page d'archétype) passent toutes par ici. Le test
// est `npm run test:stats` (frontend/scripts/test-stats.mjs), lancé par check.py.
//
// Pourquoi Wilson plutôt que l'intervalle « part ± 1,96 × erreur type » (Wald) : à
// petite part et petit effectif (2 decks sur 156), Wald descend sous zéro et se
// rétrécit à rien quand k = 0 ; Wilson reste dans [0, 1] et garde une largeur
// honnête. À relire par la collaboratrice data scientist avant mise en ligne
// (docs/journal/explication-graphique-lot15.md).
//
// Hypothèse : les decks d'un mois sont traités comme des tirages indépendants. Un
// même joueur ou un même tournoi qui fournit plusieurs listes rend l'intervalle
// trop étroit : c'est un intervalle minimal, l'incertitude réelle est plus large.
// Intervalles ponctuels (un par mois et par série) : deux bandes qui se
// chevauchent ou non ne valent pas un test d'écart entre deux mois.

/** Quantile de la loi normale pour un niveau de confiance de 95 %. */
export const Z95 = 1.959964;

/**
 * Bornes [basse, haute] de l'intervalle de Wilson, en proportion (0 à 1).
 * `n <= 0` : aucune information, l'intervalle couvre [0, 1].
 */
export function wilsonInterval(k: number, n: number, z: number = Z95): [number, number] {
  if (!(n > 0)) return [0, 1];
  const successes = Math.min(Math.max(k, 0), n);
  const p = successes / n;
  const z2 = z * z;
  const denom = 1 + z2 / n;
  const centre = (p + z2 / (2 * n)) / denom;
  const half = (z / denom) * Math.sqrt((p * (1 - p)) / n + z2 / (4 * n * n));
  // Aux bords (k = 0 ou k = n), la borne vaut exactement 0 ou 1 ; on évite les
  // résidus d'arrondi flottant du type 1e-17.
  const lo = successes === 0 ? 0 : Math.max(0, centre - half);
  const hi = successes === n ? 1 : Math.min(1, centre + half);
  return [lo, hi];
}

/** Seuil sous lequel un mois est atténué dans les séries (charte §3, validé le 17/11). */
export const WEAK_MONTH_DECKS = 100;
