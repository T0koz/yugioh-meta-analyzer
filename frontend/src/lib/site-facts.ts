// Chiffres de vitrine (hero de la tier list, home, boutique) qui ne sont
// exposés par aucun endpoint. À mettre à jour à la main quand la base est
// rafraîchie. Sources : context.md (« Nettoyage du backlog fiabilité »),
// docs/evaluation-prediction.md (TOK-73), docs/tok-74-kewl-tune.md.
export const SITE_FACTS = {
  // Decklists légales + Genesys au 2026-11-14 (TCG 11 618, OCG 12 330).
  decklists: 23_948,
  decklistsTcg: 11_618,
  decklistsOcg: 12_330,
  cardsTracked: 13_797,
  // Corrélation OCG → TCG à 4 mois, TCG pur : r ≈ 0,53, IC 95 % [0,43 ; 0,59],
  // 105 archétypes. L'ancien r = 0,771 (n = 43) n'est plus reproductible.
  ocgTcgCorrelation: 0.53,
  ocgTcgCorrelationCi: [0.43, 0.59] as const,
  ocgTcgArchetypes: 105,
  // Le signal est à peu près constant de 2 à 6 mois : « 4 mois » était un artefact du choix du max.
  ocgTcgLagRange: "2 à 6 mois",
  // Fenêtre d'arrivée OCG → TCG (notebook 10, P10-P90 = 75-202 jours sur 1 897 cartes 2022-2025 sorties en
  // TCG). Couverture hors échantillon (audit de rigueur, A2, recalculée au lot 20 le 2026-11-18) : P10-P90
  // estimés sur les cartes sorties en OCG en 2022-2023 (n = 1 078, 89 à 202 jours), appliqués aux cartes de
  // 2024 et de 2025. Mesure par carte, parmi les cartes déjà sorties en TCG seulement (biais du survivant).
  arrivalWindowCards: 1_897,
  arrivalCoverage: [
    { year: 2024, pct: 67, cards: 367 },
    { year: 2025, pct: 62, cards: 470 },
  ] as const,
  // Non recalculé depuis le rafraîchissement : ne pas afficher de date de fraîcheur.
  graphCommunities: 63,
  // Ban Radar rejoué la veille des 10 banlists TCG du backtest (2024-04-15 au
  // 2026-10-19) : places du top 10 suivies d'une restriction, sur 10 × 10 places.
  // Ce sont des places, pas des cartes distinctes. À recalculer à chaque banlist.
  banBacktestLists: 10,
  banTop10HitsGeneric: 6,
  banTop10HitsArchetype: 19,
  // Backtest du Ban Radar du 2026-11-16 (decks légaux, `build_ban_history.py`, table
  // `ban_backtest_lists`, 20 listes retenues) : cartes touchées dans le top 25 de la veille,
  // pour le score (`top_n_hits`) et pour le classement par part des decks
  // (`baseline_top_n_hits`), sommées sur les 10 listes de chaque format ; listes où le score
  // fait mieux / moins bien ; listes où son rang médian est meilleur. Verdict TOK-115 validé
  // le 17/11 (docs/journal/ban-radar-tcg-diagnostic.md). À recalculer à chaque banlist.
  // `periodFrom` : la même période dans une phrase (« les 10 banlists TCG d’avril 2024… »).
  banBacktestDate: "2026-11-16",
  banBacktestTotalLists: 20,
  banTop25: [
    { format: "TCG", period: "avril 2024 à octobre 2026", periodFrom: "d’avril 2024 à octobre 2026", lists: 10, radar: 29, staples: 16, better: 6, worse: 1, medianBetter: 3 },
    { format: "OCG", period: "avril 2024 à octobre 2026", periodFrom: "d’avril 2024 à octobre 2026", lists: 10, radar: 41, staples: 18, better: 9, worse: 1, medianBetter: 8 },
  ],
};

// « 62 à 67 % » : couverture hors échantillon de la fenêtre d'arrivée, à écrire partout où la fenêtre s'affiche.
const coverage = SITE_FACTS.arrivalCoverage.map((c) => c.pct);
export const ARRIVAL_COVERAGE_RANGE = `${Math.min(...coverage)} à ${Math.max(...coverage)} %`;
