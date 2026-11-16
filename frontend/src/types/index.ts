export type Tier = "T0" | "T1" | "T2" | "T3" | "Rogue";
export type Trend = "Rising" | "Stable" | "Declining";
export type BuyLabel = "Fort" | "Modéré" | "Faible";
export type RiskLabel = "Critique" | "Élevé" | "Modéré" | "Faible";

export interface TierEntry {
  archetype: string;
  /** Identifiant d'URL de la page d'archétype, calculé par l'API. */
  slug: string;
  tier: Tier;
  meta_score: number;
  share: number;
  /** Decks de l'archétype dans la fenêtre. */
  decks: number;
  trend: Trend;
  image_url: string | null;
}

export interface TierListResponse {
  data: TierEntry[];
  /** Fenêtre de calcul : premier et dernier mois cumulés (« AAAA-MM »). */
  window_start: string;
  window_end: string;
  n_decks: number;
}

export interface EvolutionPoint {
  month: string;
  meta_score: number;
  share: number;
}

export interface EvolutionResponse {
  data: Record<string, EvolutionPoint[]>;
  /** Vignette par archétype ; absente si aucune carte connue. */
  images: Record<string, string>;
  /** Decks de tournoi comptés chaque mois (« AAAA-MM » → n). */
  decks_by_month: Record<string, number>;
}

export interface PredictionEntry {
  archetype: string;
  current: number;
  predicted: number;
  direction: Trend;
  image_url: string | null;
}

export interface PredictionsResponse {
  data: PredictionEntry[];
  model: string;
  /** Mois observé (« AAAA-MM ») : la prévision porte sur le mois suivant. */
  data_month: string | null;
  computed_at: string | null;
}

export interface BoutiqueSignal {
  archetype: string;
  /** Identifiant d'URL de la page d'archétype, calculé par l'API. */
  archetype_slug: string;
  card_name: string;
  /** Classement dans le lot (0-100, le premier vaut toujours 100) : ordre d'affichage, PAS une force de signal. */
  buy_score: number;
  /** Libellé absolu : rang de l'archétype parmi tous les archétypes OCG. null si indisponible. */
  signal_label: BuyLabel | null;
  /** 1 = archétype OCG le plus fort ; null si indisponible. */
  archetype_rank: number | null;
  cm_price: number;
  ban_tcg: string | null;
  image_url: string | null;
  /** Fenêtre d'arrivée en TCG de l'archétype, intervalle à 80 % (« AAAA-MM-JJ »). */
  tcg_window_start: string | null;
  tcg_window_end: string | null;
}

/** Règle du libellé `signal_label` (Fort = rang ≤ strong_max_rank, Modéré = rang ≤ moderate_max_rank, sinon Faible). */
export interface SignalLabelRule {
  population: number;
  strong_max_rank: number;
  moderate_max_rank: number;
  provisional: boolean;
  note: string;
}

export interface BoutiqueResponse {
  data: BoutiqueSignal[];
  /** null quand aucun libellé n'est calculable. */
  label_rule: SignalLabelRule | null;
  computed_at: string | null;
}

/** Relevé de prix Cardmarket d'une carte (TOK-103). */
export interface PricePoint {
  date: string;
  price: number;
}

/** Période sans relevé : dernier relevé avant, premier après, écart en jours. Ne pas relier. */
export interface PriceGap {
  start: string;
  end: string;
  days: number;
}

export interface CardPriceHistory {
  card_name: string;
  points: PricePoint[];
  gaps: PriceGap[];
  /** Moins de `min_points` relevés : points seulement, aucune ligne. */
  sparse: boolean;
}

export interface PriceHistoryResponse {
  cards: CardPriceHistory[];
  period_start: string | null;
  period_end: string | null;
  snapshot_count: number;
  max_step_days: number;
  min_points: number;
  source: string;
  computed_at: string | null;
}

export interface EarlySignal {
  card_name: string;
  archetype: string | null;
  early_score: number;
  views_week: number;
  image_url: string | null;
}

export interface EarlySignalsResponse {
  data: EarlySignal[];
  computed_at: string | null;
}

export interface BanSimResult {
  removed_card: string;
  image_url: string | null;
  affected_archetypes: string[];
  community_impact: { community_id: number; fragmentation: number };
  bridge_score: number;
}

/** `generic` = staple sans deck d'attache, `archetype` = pièce de moteur. */
export type BanRadarKind = "generic" | "archetype";

/** Contribution de chaque critère au score, déjà pondérée, en points. */
export interface BanRadarCriteria {
  ubiquity: number;
  carrier: number;
  copies: number;
  restriction: number;
  momentum: number;
  bridge: number;
}

export interface BanRadarEntry {
  card_name: string;
  ban_risk_score: number;
  risk_label: RiskLabel;
  current_status: string;
  deck_share: number;
  decks: number;
  n_archetypes: number;
  mean_copies: number;
  top_archetype: string | null;
  image_url: string | null;
  criteria: BanRadarCriteria;
}

export interface BanRadarResponse {
  data: BanRadarEntry[];
  as_of: string;
  n_decks_window: number;
  weights: Record<string, number>;
}

/** Carte d'une banlist rejouée (TOK-55) : du top prévu la veille, touchée, ou les deux. */
export interface BanHistoryCard {
  card_name: string;
  /** Nul : carte touchée hors classement (moins de 5 decks dans la fenêtre). */
  rank: number | null;
  ban_risk_score: number | null;
  /** Rang si l'on classait par part des decks seule (base « staples les plus jouées »). */
  baseline_rank: number | null;
  hit: boolean;
  in_top: boolean;
  generic: boolean;
  top_archetype: string | null;
  status_before: string;
  status_after: string;
  image_url: string | null;
}

/** Banlist rejouée la veille de son entrée en vigueur. Champs de classement nuls si écartée. */
export interface BanHistoryList {
  format: "TCG" | "OCG";
  effective_date: string;
  as_of: string;
  retained: boolean;
  skip_reason: "decks" | "hits" | null;
  /** Place de la liste par rapport au calage des poids (2026-08-14) : seules les « prospective » lui sont postérieures. */
  sample: "calage" | "validation" | "retrospective" | "prospective";
  n_decks: number;
  n_hits: number;
  n_cards: number | null;
  n_hits_ranked: number | null;
  n_hits_missing: number | null;
  median_rank: number | null;
  random_rank: number | null;
  /** 5e et 95e centiles du rang médian d'autant de cartes tirées au hasard. */
  random_low: number | null;
  random_high: number | null;
  top_n_hits: number | null;
  top10pct_hits: number | null;
  top25pct_hits: number | null;
  baseline_median_rank: number | null;
  baseline_top_n_hits: number | null;
  cards: BanHistoryCard[];
}

export interface BanHistoryResponse {
  lists: BanHistoryList[];
  computed_at: string;
  top_n: number;
  min_decks: number;
  min_hits: number;
}

export interface CardImpactEntry {
  card_name: string;
  bridge_score: number;
  n_archetypes: number;
  decks: number;
  top_archetype: string | null;
  image_url: string | null;
}

export interface CardImpactResponse {
  data: CardImpactEntry[];
  as_of: string;
  n_decks_window: number;
}

export interface GraphNode {
  id: string;
  group: string | null;
  size: number;
  image_url: string | null;
}

export interface GraphEdge {
  source: string;
  target: string;
  weight: number;
}

export interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface SearchResult {
  name: string;
  archetype: string | null;
  image_url: string | null;
}

export interface SearchResponse {
  data: SearchResult[];
}

// ---------- Page d'archétype (TOK-101) ----------

export interface ArchetypeTcg {
  tier: Tier;
  trend: Trend;
  /** Rang dans la tier list (1 = plus forte part). */
  rank: number;
  n_archetypes: number;
  share: number;
  decks: number;
  meta_score: number;
  /** Fenêtre précédente, base de la tendance ; null s'il n'y en a pas. */
  share_prev: number | null;
  decks_prev: number;
  n_decks_prev: number;
}

/** Fenêtre courante de la tier list (mois « AAAA-MM »). */
export interface TierWindow {
  start: string;
  end: string;
  n_decks: number;
}

export interface ArchetypeMonth {
  month: string;
  decks: number;
  total_decks: number;
  share: number;
}

export interface ArchetypeKeyCard {
  card_name: string;
  decks: number;
  /** En pourcentage de tous les decks de la fenêtre. */
  deck_share: number;
  mean_copies: number;
  current_status: string;
  image_url: string | null;
}

export interface ArchetypeResponse {
  archetype: string;
  slug: string;
  image_url: string | null;
  tcg_window: TierWindow | null;
  /** null si aucun deck dans la fenêtre courante de la tier list. */
  tcg: ArchetypeTcg | null;
  history: ArchetypeMonth[];
  key_cards: { data: ArchetypeKeyCard[]; as_of: string; n_decks_window: number } | null;
  ocg: { share: number; decks: number; computed_at: string | null } | null;
  boutique: {
    signal_label: BuyLabel | null;
    archetype_rank: number | null;
    label_rule: SignalLabelRule | null;
    tcg_window_start: string | null;
    tcg_window_end: string | null;
    computed_at: string | null;
    signals: BoutiqueSignal[];
  } | null;
}

// ── Decks (TOK-114) ──────────────────────────────────────────────────────────

export type Zone = "main" | "extra" | "side";
/** « base » : au moins `rule.base_min_share` des listes ; « appoint » : au moins `rule.flex_min_share`. */
export type CardRole = "base" | "appoint";

export interface DeckProfileRule {
  base_min_share: number;
  flex_min_share: number;
  /** Listes en dessous desquelles aucune part n'est calculée. */
  min_decks: number;
}

export interface DeckCardStat {
  card_name: string;
  /** Listes de l'archétype qui contiennent la carte dans cette zone. */
  n_lists: number;
  /** n_lists / listes de l'archétype, de 0 à 1. */
  share: number;
  /** Médiane des exemplaires parmi les listes qui la jouent. */
  median_copies: number;
  role: CardRole | null;
  image_url: string | null;
}

export interface DeckIndexEntry {
  archetype: string;
  slug: string;
  tier: Tier;
  decks: number;
  share: number;
  has_profile: boolean;
  image_url: string | null;
  base_cards: number;
  base_copies: number;
  preview: DeckCardStat[];
}

export interface DeckIndexResponse {
  data: DeckIndexEntry[];
  window: TierWindow | null;
  rule: DeckProfileRule;
  computed_at: string | null;
}

export interface RecentDeck {
  deck_id: string;
  author: string | null;
  tournament_type: string | null;
  /** 1 = vainqueur, 2 = finaliste, 3,5 = demi-finaliste, 8 = top 8… */
  placement: number;
  date: string;
  zones: { zone: Zone; n_cards: number; cards: { card_name: string; amount: number; image_url: string | null }[] }[];
}

export interface DeckResponse {
  archetype: string;
  slug: string;
  image_url: string | null;
  tier: Tier | null;
  decks: number;
  share: number;
  has_profile: boolean;
  window: TierWindow;
  rule: DeckProfileRule;
  computed_at: string;
  /** Vide sous l'effectif minimal. */
  zones: { zone: Zone; cards: DeckCardStat[] }[];
  recent_decks: RecentDeck[];
}
