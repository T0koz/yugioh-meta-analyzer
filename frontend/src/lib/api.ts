import type {
  ArchetypeResponse,
  BanHistoryResponse,
  BanRadarKind,
  BanRadarResponse,
  BanSimResult,
  BoutiqueResponse,
  PriceHistoryResponse,
  CardImpactResponse,
  DeckIndexResponse,
  DeckResponse,
  EarlySignalsResponse,
  EvolutionResponse,
  GraphResponse,
  PredictionsResponse,
  SearchResponse,
  TierListResponse,
} from "@/types";

const LOCAL_API_URL = "http://localhost:8000/api/v1";

/**
 * Adresse de l'API (TOK-35). Le serveur et le navigateur n'ont pas besoin de la même :
 * - côté serveur (rendu, build), une adresse absolue, lue dans l'ordre :
 *   `API_URL` (build local de la voie 2), puis `BACKEND_URL` + `/api/v1` (liaison de service
 *   injectée par Vercel à l'exécution), puis `NEXT_PUBLIC_API_URL`, puis l'API locale ;
 * - côté navigateur, `NEXT_PUBLIC_API_URL` (en ligne : `/api/v1`, même domaine), puis l'API locale.
 * Sans aucune de ces variables, rien ne change : http://localhost:8000/api/v1 des deux côtés.
 */
export function apiBaseUrl(): string {
  const trim = (u: string) => u.replace(/\/+$/, "");
  if (typeof window === "undefined") {
    if (process.env.API_URL) return trim(process.env.API_URL);
    if (process.env.BACKEND_URL) return `${trim(process.env.BACKEND_URL)}/api/v1`;
    const pub = process.env.NEXT_PUBLIC_API_URL;
    // Une adresse relative (/api/v1) ne veut rien dire pour fetch côté serveur.
    if (pub && !/^https?:\/\//.test(pub)) {
      throw new Error(
        `NEXT_PUBLIC_API_URL=${pub} est relative : côté serveur, définir API_URL (adresse absolue de l'API).`,
      );
    }
    return trim(pub || LOCAL_API_URL);
  }
  return trim(process.env.NEXT_PUBLIC_API_URL || LOCAL_API_URL);
}

async function apiFetch<T>(path: string): Promise<T> {
  const res = await fetch(`${apiBaseUrl()}${path}`, { next: { revalidate: 300 } });
  if (!res.ok) throw new Error(`API error ${res.status}: ${path}`);
  return res.json() as Promise<T>;
}

export const api = {
  tierList: () => apiFetch<TierListResponse>("/meta/tier-list"),
  /** Page d'archétype ; null si le slug ne correspond à aucun archétype (404). */
  async archetype(slug: string): Promise<ArchetypeResponse | null> {
    const res = await fetch(`${apiBaseUrl()}/archetypes/${encodeURIComponent(slug)}`, { next: { revalidate: 300 } });
    if (res.status === 404) return null;
    if (!res.ok) throw new Error(`API error ${res.status}: /archetypes/${slug}`);
    return res.json() as Promise<ArchetypeResponse>;
  },
  decks: () => apiFetch<DeckIndexResponse>("/decks"),
  /** Fiche de composition ; null si aucune liste de l'archétype dans la fenêtre (404). */
  async deck(slug: string): Promise<DeckResponse | null> {
    const res = await fetch(`${apiBaseUrl()}/decks/${encodeURIComponent(slug)}`, { next: { revalidate: 300 } });
    if (res.status === 404) return null;
    if (!res.ok) throw new Error(`API error ${res.status}: /decks/${slug}`);
    return res.json() as Promise<DeckResponse>;
  },
  evolution: () => apiFetch<EvolutionResponse>("/meta/evolution"),
  predictions: () => apiFetch<PredictionsResponse>("/meta/predictions"),
  boutiqueSignals: () => apiFetch<BoutiqueResponse>("/boutique/signals"),
  boutiquePrices: () => apiFetch<PriceHistoryResponse>("/boutique/prices"),
  earlySignals: () => apiFetch<EarlySignalsResponse>("/early-signals"),
  banRadar: (params?: { limit?: number; kind?: BanRadarKind }) => {
    const query = new URLSearchParams({ limit: String(params?.limit ?? 50) });
    if (params?.kind) query.set("kind", params.kind);
    return apiFetch<BanRadarResponse>(`/ban-radar?${query}`);
  },
  /** Backtest du Ban Radar liste par liste (TOK-55). */
  banHistory: () => apiFetch<BanHistoryResponse>("/ban-radar/history"),
  cardImpact: (params?: { limit?: number; kind?: BanRadarKind }) => {
    const query = new URLSearchParams({ limit: String(params?.limit ?? 50) });
    if (params?.kind) query.set("kind", params.kind);
    return apiFetch<CardImpactResponse>(`/card-impact?${query}`);
  },
  graphSynergies: (params?: { limit?: number; minJaccard?: number }) => {
    const query = new URLSearchParams();
    if (params?.limit) query.set("limit", String(params.limit));
    if (params?.minJaccard) query.set("min_jaccard", String(params.minJaccard));
    const qs = query.toString();
    return apiFetch<GraphResponse>(`/graph/synergies${qs ? `?${qs}` : ""}`);
  },
  searchCards: (q: string, limit = 8) =>
    apiFetch<SearchResponse>(`/cards/search?q=${encodeURIComponent(q)}&limit=${limit}`),
  async simulateBan(cardName: string): Promise<BanSimResult | null> {
    const res = await fetch(`${apiBaseUrl()}/simulate-ban`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ card_name: cardName }),
      cache: "no-store",
    });
    if (res.status === 404) return null;
    if (!res.ok) throw new Error(`API error ${res.status}: /simulate-ban`);
    return res.json() as Promise<BanSimResult>;
  },
};
