// Chiffres de vitrine (hero de la tier list, home, boutique) qui ne sont
// exposés par aucun endpoint. À mettre à jour à la main quand la base est
// rafraîchie. Sources : context.md (« Nettoyage du backlog fiabilité »),
// docs/evaluation-prediction.md (TOK-73), docs/tok-74-kewl-tune.md.
export const SITE_FACTS = {
  // Decklists relevées au 2026-11-14, toutes légalités confondues (TCG 11 618, OCG 12 330). Parmi elles, 22 422 sont
  // légales à la date du tournoi (`deck_legality.legal = 1` : TCG 10 369, OCG 12 053) et seules comptées dans les
  // calculs ; 611 illégales, 915 Genesys non évaluables. Relevé du 2026-11-18 (TOK-82).
  decklists: 23_948,
  decklistsTcg: 11_618,
  decklistsOcg: 12_330,
  decklistsLegal: 22_422,
  decklistsLegalTcg: 10_369,
  decklistsLegalOcg: 12_053,
  // Table `cards` au 2026-11-18 (cartes ajoutées chaque lundi par fetch_new_cards.py).
  cardsTracked: 14_084,
  // Corrélation OCG → TCG à 4 mois, TCG pur : r ≈ 0,53, IC 95 % [0,43 ; 0,59],
  // 105 archétypes. L'ancien r = 0,771 (n = 43) n'est plus reproductible.
  ocgTcgCorrelation: 0.53,
  ocgTcgCorrelationCi: [0.43, 0.59] as const,
  ocgTcgArchetypes: 105,
  // Le signal est à peu près constant de 2 à 6 mois : « 4 mois » était un artefact du choix du max.
  ocgTcgLagRange: "2 à 6 mois",
  // Audit de rigueur (A3) : le classement OCG du signal boutique suit presque la seule part des decks OCG.
  // Corrélation de rang (Spearman) entre `ocg_score` et `share_ocg`, 89 archétypes de `ocg_archetype_scores`,
  // recalculée au lot 20 le 2026-11-18 (0,9396). À recalculer quand le notebook 10 change.
  ocgScoreShareRho: 0.94,
  ocgScoreArchetypes: 89,
  // Fenêtre d'arrivée OCG → TCG (notebook 10, P10-P90 = 75-202 jours sur 1 897 cartes 2022-2025 sorties en
  // TCG). Vérification comptée en archétypes, l'unité affichée (TOK-130, docs/journal/fenetre-survie-tok-130.md,
  // validé le 19/11, bloc A4) : arrivée (la moitié des cartes inédites sorties en TCG) dans la fenêtre pour
  // 27 archétypes sur 36 de 2024 à 2026 (16 cohortes ; 2024-2025 en partie dans l'échantillon d'estimation) et
  // 12 sur 18 pour 2026 seule, postérieure au calcul. Remplace la couverture par carte (62-67 %, audit A2).
  arrivalWindowCards: 1_897,
  arrivalCoverage: [
    { period: "2024-2026", hits: 27, archetypes: 36 },
    { period: "2026", hits: 12, archetypes: 18 },
  ] as const,
  // Graphe du notebook 03, non recalculé au rafraîchissement du 2026-11-16 (TOK-136) : sa date de calcul n'est pas
  // enregistrée, ne pas afficher de date de fraîcheur. 663 cartes réparties en 63 communautés.
  graphCommunities: 63,
  graphCards: 663,
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

// Vérification de la fenêtre d'arrivée, à écrire partout où la fenêtre s'affiche (seule source de ces chiffres) :
// « arrivée dans la fenêtre pour 27 archétypes sur 36 (2024-2026) ; 12 sur 18 pour 2026 ».
const [coverageAll, coverageRecent] = SITE_FACTS.arrivalCoverage;
export const ARRIVAL_COVERAGE = `arrivée dans la fenêtre pour ${coverageAll.hits} archétypes sur ${coverageAll.archetypes} (${coverageAll.period}) ; ${coverageRecent.hits} sur ${coverageRecent.archetypes} pour ${coverageRecent.period}`;
// Forme courte, pour un en-tête de colonne ou une ligne de métadonnées ; la forme longue est dans le pied.
export const ARRIVAL_COVERAGE_SHORT = `juste pour ${coverageAll.hits} archétypes sur ${coverageAll.archetypes}`;
