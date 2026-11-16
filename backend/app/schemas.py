from typing import Literal, Optional

from pydantic import BaseModel

Tier = Literal["T0", "T1", "T2", "T3", "Rogue"]
Trend = Literal["Rising", "Stable", "Declining"]
BuyLabel = Literal["Fort", "Modéré", "Faible"]
RiskLabel = Literal["Critique", "Élevé", "Modéré", "Faible"]


class TierEntry(BaseModel):
    archetype: str
    # Identifiant d'URL de la page d'archétype (app/slugs.py) : le front ne le recalcule pas.
    slug: str
    tier: Tier
    meta_score: float
    share: float
    decks: int  # decks de l'archétype dans la fenêtre (numérateur de `share`)
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
    # Decks de tournoi comptés chaque mois (taille d'échantillon, « AAAA-MM » → n).
    decks_by_month: dict[str, int] = {}


class PredictionEntry(BaseModel):
    archetype: str
    current: float
    predicted: float
    direction: Trend
    image_url: Optional[str] = None


class PredictionsResponse(BaseModel):
    data: list[PredictionEntry]
    model: str
    # Mois observé (« AAAA-MM ») : la prévision porte sur le mois suivant.
    data_month: Optional[str] = None
    computed_at: Optional[str] = None  # date du calcul (« AAAA-MM-JJ »)


class BoutiqueSignal(BaseModel):
    archetype: str
    archetype_slug: str  # identifiant d'URL de la page d'archétype (app/slugs.py)
    card_name: str
    # Classement dans le lot (0-100, le premier vaut toujours 100) : ce n'est PAS une force
    # de signal, seulement l'ordre d'affichage (archétype + prix de la carte).
    buy_score: float
    # Libellé ABSOLU, rang de l'archétype parmi tous les archétypes OCG (TOK-113, suite) :
    # Fort = 10 % du haut, Modéré = 25 %, Faible = le reste. NULL si la table
    # `ocg_archetype_scores` est absente de la base servie ou ne contient pas l'archétype.
    signal_label: Optional[BuyLabel] = None
    archetype_rank: Optional[int] = None  # 1 = archétype OCG le plus fort
    cm_price: float
    ban_tcg: Optional[str] = None
    image_url: Optional[str] = None
    # Fenêtre d'arrivée en TCG de l'archétype (intervalle à 80 %, « AAAA-MM-JJ »),
    # NULL si la source n'en a pas calculé.
    tcg_window_start: Optional[str] = None
    tcg_window_end: Optional[str] = None


class SignalLabelRule(BaseModel):
    """Règle du libellé, pour que le front l'affiche sans la recopier."""

    population: int  # nombre d'archétypes OCG classés
    strong_max_rank: int  # rang maximal (inclus) du libellé Fort
    moderate_max_rank: int  # rang maximal (inclus) du libellé Modéré
    provisional: bool = True
    note: str


class BoutiqueResponse(BaseModel):
    data: list[BoutiqueSignal]
    # NULL quand les libellés sont indisponibles (aucun signal_label dans `data`).
    label_rule: Optional[SignalLabelRule] = None
    computed_at: Optional[str] = None  # date du calcul (« AAAA-MM-JJ »)


class EarlySignal(BaseModel):
    card_name: str
    # NULL pour les cartes sans archétype dans YGOPRODeck (ex. Fydraulis Harmonia)
    archetype: str | None
    early_score: float
    views_week: int
    image_url: Optional[str] = None


class EarlySignalsResponse(BaseModel):
    data: list[EarlySignal]
    computed_at: Optional[str] = None  # date du calcul (« AAAA-MM-JJ »)


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


# ---------- Page d'archétype (TOK-101) ----------


class ArchetypeTcg(BaseModel):
    """Position dans la tier list courante (mêmes règles : app/tiering.py)."""

    tier: Tier
    trend: Trend
    rank: int  # rang dans la tier list (1 = plus forte part)
    n_archetypes: int  # archétypes classés dans la fenêtre
    share: float
    decks: int
    meta_score: float
    # Fenêtre précédente (base de la tendance) ; NULL s'il n'y en a pas.
    share_prev: Optional[float] = None
    decks_prev: int = 0
    n_decks_prev: int = 0


class TierWindow(BaseModel):
    """Fenêtre courante de la tier list (mois « AAAA-MM » cumulés, decks comptés)."""

    start: str
    end: str
    n_decks: int


class ArchetypeMonth(BaseModel):
    month: str  # « AAAA-MM »
    decks: int  # 0 = aucun deck de l'archétype ce mois-là
    total_decks: int
    share: float


class ArchetypeKeyCard(BaseModel):
    card_name: str
    decks: int  # decks de la fenêtre qui jouent la carte
    deck_share: float  # en pourcentage de tous les decks de la fenêtre
    mean_copies: float
    current_status: str
    image_url: Optional[str] = None


class ArchetypeKeyCards(BaseModel):
    data: list[ArchetypeKeyCard]
    as_of: str
    n_decks_window: int


class ArchetypeOcg(BaseModel):
    share: float
    decks: int
    computed_at: Optional[str] = None


class ArchetypeBoutique(BaseModel):
    signal_label: Optional[BuyLabel] = None
    archetype_rank: Optional[int] = None
    label_rule: Optional[SignalLabelRule] = None
    tcg_window_start: Optional[str] = None
    tcg_window_end: Optional[str] = None
    computed_at: Optional[str] = None
    signals: list[BoutiqueSignal]


class ArchetypeResponse(BaseModel):
    archetype: str
    slug: str
    image_url: Optional[str] = None
    # Fenêtre de la tier list, servie même quand l'archétype n'y a aucun deck.
    tcg_window: Optional[TierWindow] = None
    # NULL si l'archétype n'a aucun deck dans la fenêtre courante de la tier list.
    tcg: Optional[ArchetypeTcg] = None
    # Un point par mois, du premier mois où l'archétype apparaît au dernier mois de la base.
    history: list[ArchetypeMonth] = []
    # NULL si aucune carte suivie n'a cet archétype pour deck d'attache.
    key_cards: Optional[ArchetypeKeyCards] = None
    ocg: Optional[ArchetypeOcg] = None
    boutique: Optional[ArchetypeBoutique] = None
