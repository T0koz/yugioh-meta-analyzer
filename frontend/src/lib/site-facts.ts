// Chiffres de vitrine (hero de la tier list, home, boutique) qui ne sont
// exposés par aucun endpoint. À mettre à jour à la main quand la base est
// rafraîchie. Sources : context.md (« Nettoyage du backlog fiabilité »),
// docs/evaluation-prediction.md (TOK-73), docs/tok-74-kewl-tune.md.
export const SITE_FACTS = {
  // Decklists légales + Genesys au 2026-11-14 (TCG 11 618, OCG 12 330).
  decklists: 23_948,
  cardsTracked: 13_797,
  // Corrélation OCG → TCG à 4 mois, TCG pur : r ≈ 0,53, IC 95 % [0,43 ; 0,59],
  // 105 archétypes. L'ancien r = 0,771 (n = 43) n'est plus reproductible.
  ocgTcgCorrelation: 0.53,
  ocgTcgCorrelationCi: [0.43, 0.59] as const,
  ocgTcgArchetypes: 105,
  // Le signal est à peu près constant de 2 à 6 mois : « 4 mois » était un artefact du choix du max.
  ocgTcgLagRange: "2 à 6 mois",
  // Non recalculé depuis le rafraîchissement : ne pas afficher de date de fraîcheur.
  graphCommunities: 63,
  // Ban Radar rejoué la veille des 10 banlists TCG du backtest (2024-04-15 au
  // 2026-10-19) : places du top 10 suivies d'une restriction, sur 10 × 10 places.
  // Ce sont des places, pas des cartes distinctes. À recalculer à chaque banlist.
  banBacktestLists: 10,
  banTop10HitsGeneric: 6,
  banTop10HitsArchetype: 19,
};
