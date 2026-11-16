// Données du graphique « la preuve » de l'accueil : part mensuelle de Kewl Tune
// dans les decks de tournoi, en %, d'août 2025 à novembre 2026.
// Relevé en lecture seule dans `yugioh.db` (tables `meta_scores` et
// `meta_scores_ocg`) le 16 novembre 2026. Figé ici parce que `meta_scores_ocg`
// n'est pas dans la base de service : à relever de nouveau si l'exemple change,
// ou à remplacer par un endpoint quand la page d'archétype (TOK-101) en aura un.
// Un 0 est un mois avec des decks mais sans Kewl Tune, pas un mois manquant.
export const PROOF = {
  archetype: "Kewl Tune",
  asOf: "2026-11-16",
  firstMonth: "2025-08",
  ocg: [0.8, 0.8, 0.6, 0.7, 0, 2.2, 10.3, 18.3, 26.7, 17.6, 25.1, 11.6, 9.9, 6.8, 1.1, 2.1],
  tcg: [0, 0, 0, 0, 1.4, 2.6, 1.4, 1.0, 0.7, 22.5, 26.7, 32.1, 19.9, 8.9, 0.4, 0],
  // Indices des pics (avril 2026 en OCG, juillet 2026 en TCG) : 3 mois d'écart.
  ocgPeak: 8,
  tcgPeak: 11,
} as const;
