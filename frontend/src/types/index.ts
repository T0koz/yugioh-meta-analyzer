export type Tier = "T0" | "T1" | "T2" | "T3" | "Rogue";
export type Trend = "Rising" | "Stable" | "Declining";
export type BuyLabel = "Fort" | "Modéré" | "Faible";

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
  generated_at: string;
}

export interface EvolutionPoint {
  month: string;
  meta_score: number;
  share: number;
}

export interface EvolutionResponse {
  data: Record<string, EvolutionPoint[]>;
}

export interface PredictionEntry {
  archetype: string;
  current: number;
  predicted: number;
  direction: Trend;
}

export interface PredictionsResponse {
  data: PredictionEntry[];
  model: string;
}

export interface BoutiqueSignal {
  archetype: string;
  card_name: string;
  buy_score: number;
  buy_label: BuyLabel;
  cm_price: number;
  ban_tcg: string | null;
  tcg_entry_estimated: string | null;
}

export interface BoutiqueResponse {
  data: BoutiqueSignal[];
}

export interface EarlySignal {
  card_name: string;
  archetype: string;
  early_score: number;
  views_week: number;
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

export interface GraphNode {
  id: string;
  group: string | null;
  size: number;
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
