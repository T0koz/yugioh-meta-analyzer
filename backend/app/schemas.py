from typing import Literal, Optional

from pydantic import BaseModel

Tier = Literal["T0", "T1", "T2", "T3", "Rogue"]
Trend = Literal["Rising", "Stable", "Declining"]
BuyLabel = Literal["Fort", "Modéré", "Faible"]
RiskLabel = Literal["Critique", "Élevé", "Modéré", "Faible"]


class TierEntry(BaseModel):
    archetype: str
    tier: Tier
    meta_score: float
    share: float
    trend: Trend
    image_url: Optional[str] = None


class TierListResponse(BaseModel):
    data: list[TierEntry]
    # Fenêtre de calcul : mois « AAAA-MM » du premier et du dernier mois cumulés.
    window_start: str
    window_end: str
    n_decks: int


class EvolutionPoint(BaseModel):
    month: str
    meta_score: float
    share: float


class EvolutionResponse(BaseModel):
    data: dict[str, list[EvolutionPoint]]
    # Vignette de chaque archétype (absente si aucune carte connue).
    images: dict[str, str] = {}


class PredictionEntry(BaseModel):
    archetype: str
    current: float
    predicted: float
    direction: Trend
    image_url: Optional[str] = None


class PredictionsResponse(BaseModel):
    data: list[PredictionEntry]
    model: str


class BoutiqueSignal(BaseModel):
    archetype: str
    card_name: str
    buy_score: float
    buy_label: BuyLabel
    cm_price: float
    ban_tcg: Optional[str] = None
    image_url: Optional[str] = None
    # Fenêtre d'arrivée en TCG de l'archétype (intervalle à 80 %, « AAAA-MM-JJ »),
    # NULL si la source n'en a pas calculé.
    tcg_window_start: Optional[str] = None
    tcg_window_end: Optional[str] = None


class BoutiqueResponse(BaseModel):
    data: list[BoutiqueSignal]


class EarlySignal(BaseModel):
    card_name: str
    # NULL pour les cartes sans archétype dans YGOPRODeck (ex. Fydraulis Harmonia)
    archetype: str | None
    early_score: float
    views_week: int
    image_url: Optional[str] = None


class EarlySignalsResponse(BaseModel):
    data: list[EarlySignal]


class CommunityImpact(BaseModel):
    community_id: int
    fragmentation: float


class BanSimRequest(BaseModel):
    card_name: str


class BanSimResult(BaseModel):
    removed_card: str
    image_url: Optional[str] = None
    affected_archetypes: list[str]
    community_impact: CommunityImpact
    bridge_score: float


class SearchResult(BaseModel):
    name: str
    archetype: Optional[str] = None
    image_url: Optional[str] = None


class SearchResponse(BaseModel):
    data: list[SearchResult]


class BanRadarCriteria(BaseModel):
    """Contribution de chaque critère, déjà pondérée, en points de score final."""

    ubiquity: float
    carrier: float
    copies: float
    restriction: float
    momentum: float
    bridge: float


class BanRadarEntry(BaseModel):
    card_name: str
    ban_risk_score: float
    risk_label: RiskLabel
    current_status: str
    deck_share: float
    decks: int
    n_archetypes: int
    mean_copies: float
    top_archetype: Optional[str] = None
    image_url: Optional[str] = None
    criteria: BanRadarCriteria


class BanRadarResponse(BaseModel):
    data: list[BanRadarEntry]
    as_of: str
    n_decks_window: int
    weights: dict[str, float]


class CardImpactEntry(BaseModel):
    card_name: str
    bridge_score: float
    n_archetypes: int
    decks: int
    top_archetype: Optional[str] = None
    image_url: Optional[str] = None


class CardImpactResponse(BaseModel):
    data: list[CardImpactEntry]
    as_of: str
    n_decks_window: int


class GraphNode(BaseModel):
    id: str
    group: Optional[str] = None
    size: float
    image_url: Optional[str] = None


class GraphEdge(BaseModel):
    source: str
    target: str
    weight: float


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
