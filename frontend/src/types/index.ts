export type Tier = "T0" | "T1" | "T2" | "T3" | "Rogue";
export type Trend = "Rising" | "Stable" | "Declining";
export type BuyLabel = "Fort" | "Modéré" | "Faible";
export type RiskLabel = "Critique" | "Élevé" | "Modéré" | "Faible";

export interface TierEntry {
  archetype: string;
  tier: Tier;
  meta_score: number;
  share: number;
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
}

export interface BoutiqueSignal {
  archetype: string;
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
