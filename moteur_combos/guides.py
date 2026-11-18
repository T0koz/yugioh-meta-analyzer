"""Combos relevés dans des guides publics (lot C3, J2) : données factuelles, aucun texte recopié.

Détail, sources et lecture : `docs/moteur-combos/combos-guides.md`. Chaque combo porte :
- sa **main de départ** : la carte de départ du guide **seule** (combo « à une carte ») ; les 4 autres cartes de la
  main sont des cartes de réponse **retirées du jeu** (`hors_jeu` : ni en main, ni dans le Deck). Premier essai avec
  les 4 cartes en main : le moteur a pris `Ghost Ogre` de la main comme matériel de Fusion (G2), le combo n'était plus
  « à une carte ». Les mains réalistes de 5 cartes sont traitées à part (`scripts/combos_j2.py`) ;
- ses **étapes** telles que le guide les donne (cartes et ordre), avec le marqueur `absente` quand l'étape passe par une
  carte qui n'est pas dans la liste du pilote (décision D1 : liste de tournoi du 08/11/2026) ;
- sa **cible** : le plateau atteint à la dernière étape réalisable avec la liste (conditions d'inclusion, § 2.4 e) ;
- ses **substitutions** : là où le guide paie un coût avec une carte absente qu'une carte de la liste peut payer à sa
  place (même clause du texte), le moteur choisit librement parmi les cartes de la liste. Déclaré, jamais caché.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace

from .modele import CibleExploration, ConditionCible as C

NADIR = "Nadir Servant"
WHITE = "Fallen of the White Dragon"
DECC = "Dogmatika Ecclesia, the Virtuous"
IECC = "Incredible Ecclesia, the Virtuous"
QUEM = "Guiding Quem, the Virtuous"
CART = "Blazing Cartesia, the Virtuous"
TFTV = "The Fallen & The Virtuous"
TITAN = "Titaniklad the Ash Dragon"
DOGMA = "The Dragon that Devours the Dogma"
EDD = "Ecclesia and the Dark Dragon"
GS = "The Golden Swordsoul"
GRANG = "Granguignol the Dusk Dragon"
CHAMP = "The Three Champions of Swordsoul"
TBKITT = "Tri-Brigade Springans Kitt"
BFUSION = "Branded Fusion"
RIND = "Rindbrumm the Striking Dragon"
COCA = "Cocatorium the Heavy Metal Avian"
MERC = "Tri-Brigade Mercourier"
ALUBER = "Aluber the Jester of Despia"
FUWALOS = "Mulcharmy Fuwalos"
BHIGH = "Branded in High Spirits"
MIRROR = "Mirrorjade the Iceblade Dragon"
ALBAZ = "Fallen of Albaz"
SARC = "Gold Sarcophagus"

INERTES = ["Ash Blossom & Joyous Spring", "Ash Blossom & Joyous Spring", "Ghost Ogre & Snow Rabbit",
           "Ghost Ogre & Snow Rabbit"]

# Cartes citées par les guides et absentes de la liste du pilote.
ABSENTES = ("Albion the Branded Dragon", "Branded Retribution", "Branded in Red", "Khaos Starsource Dragon")


@dataclass(frozen=True)
class Source:
    auteur: str
    date: str
    url: str


@dataclass(frozen=True)
class Etape:
    texte: str                  # paraphrase factuelle : carte, action, carte visée
    absente: str | None = None  # carte absente de la liste par laquelle passe l'étape


@dataclass(frozen=True)
class Jalon:
    """Action clé du guide : une déclaration (type, carte, effet) et, au besoin, un choix fait pendant la transition
    (`contient` : une réponse du script, ex. « Guiding Quem, the Virtuous/2 » pour un déclencheur activé)."""
    type: str
    carte: str
    effet: int | None = None
    contient: str | None = None

    def colle(self, arete) -> bool:
        d = arete.declaration
        return (d.type == self.type and d.carte == self.carte and (self.effet is None or d.effet == self.effet)
                and (self.contient is None or self.contient in arete.reponses))


    def colle_pas(self, arete, avant, apres) -> bool:
        return self.colle(arete)


ZONES_MOUVEMENT = ("main", "deck", "extra", "cimetiere", "bannies", "terrain")


def compter(etat, zone: str, carte: str | None) -> int:
    """Exemplaires de `carte` (toutes cartes si None) dans une zone du joueur 0."""
    j = etat.joueurs[0]
    if zone == "terrain":
        noms = [i.carte for _, i in j.cases] + [o.instance.carte for o in etat.zones_monstre_extra
                                                 if o.controleur == 0]
    else:
        noms = [i.carte for i in getattr(j, zone)]
    return len(noms) if carte is None else noms.count(carte)


@dataclass(frozen=True)
class Mouvement:
    """Une carte arrive dans `vers` pendant la transition (plus d'exemplaires après qu'avant) et, si `depuis` est
    donné, quitte cette zone (moins d'exemplaires après). `carte=None` : n'importe quelle carte."""
    carte: str | None
    vers: str = "terrain"
    depuis: str | None = None

    def __post_init__(self) -> None:
        if self.vers not in ZONES_MOUVEMENT or (self.depuis is not None and self.depuis not in ZONES_MOUVEMENT):
            raise ValueError(f"zone inconnue : {self.vers} / {self.depuis}")

    def vrai(self, avant, apres) -> bool:
        if compter(apres, self.vers, self.carte) <= compter(avant, self.vers, self.carte):
            return False
        return self.depuis is None or compter(apres, self.depuis, self.carte) < compter(avant, self.depuis, self.carte)


@dataclass(frozen=True)
class JalonPas:
    """Jalon du lot J2 plein (TOK-140), traduit mot à mot du texte figé (`combos-guides.md` § 5) : chaque champ
    donné doit être vrai sur la transition, les autres sont libres. `type`/`carte`/`effet` : la déclaration ;
    `contient` : réponses du script (ex. « Tri-Brigade Mercourier/2 », un déclencheur activé) ; `mouvements` :
    changements d'état (« Invocation Spéciale de X depuis la main » = X arrive sur le terrain et quitte la main)."""
    texte: str
    type: str | None = None
    carte: str | None = None
    effet: int | None = None
    contient: tuple[str, ...] = ()
    mouvements: tuple[Mouvement, ...] = ()

    def colle_pas(self, arete, avant, apres) -> bool:
        d = arete.declaration
        if self.type is not None and d.type != self.type:
            return False
        if self.carte is not None and d.carte != self.carte:
            return False
        if self.effet is not None and d.effet != self.effet:
            return False
        if any(c not in arete.reponses for c in self.contient):
            return False
        return all(m.vrai(avant, apres) for m in self.mouvements)


def respecte_jalons(chemin, jalons, etats=None) -> bool:
    """Les jalons apparaissent dans le chemin, dans l'ordre (sous-suite, d'autres transitions peuvent s'intercaler).
    Plusieurs jalons consécutifs peuvent tenir dans une même transition (ex. « White s'Invoque » puis « elle Invoque
    Incredible Ecclesia » : une seule transition, l'effet déclenché se résout avec elle) ; la correspondance gloutonne
    reste optimale pour une sous-suite. Les jalons du lot C3 portent chacun une déclaration différente de la
    précédente : pour eux, rien ne change. `etats` (empreinte → état) : requis par les jalons `JalonPas`."""
    k = 0
    for a in chemin:
        avant = etats[a.source] if etats is not None else None
        apres = etats[a.cible] if etats is not None and a.cible is not None else None
        while k < len(jalons) and jalons[k].colle_pas(a, avant, apres):
            k += 1
    return k == len(jalons)


def fin_de_tour_possible(cat, etat) -> bool:
    """État de Phase de Fin d'où le tour peut se terminer (aucun effet obligatoire n'attend, R23) : la « fin du
    tour » du § 5.2 de `combos-guides.md`."""
    from .regles import Declaration, Moteur, Script
    if etat.cadre.phase != "fin":
        return False
    return Moteur(cat).jouer(etat, Declaration("fin_de_tour", "—"), Script()).verdict == "legal"


@dataclass(frozen=True)
class ComboGuide:
    gid: str
    titre: str
    sources: tuple[Source, ...]
    depart: str
    etapes: tuple[Etape, ...]
    cible: CibleExploration
    substitutions: tuple[str, ...] = ()
    remarques: tuple[str, ...] = ()
    main: tuple[str, ...] = field(default=())
    jalons: tuple = ()
    lot: str = "C3"
    en_fin_de_tour: bool = False      # J2 plein : cible évaluée sur un état d'où le tour peut se terminer
    condition: object = None          # condition de plus sur l'état final (ex. « Mercourier ou Cartesia »)

    def accepter(self, rapport, etat_id) -> bool:
        if self.en_fin_de_tour:
            raise ValueError(f"{self.gid} : cible évaluée en fin de tour, utiliser accepteur(catalogue)")
        return self._jalons_et_condition(rapport, etat_id)

    def _jalons_et_condition(self, rapport, etat_id) -> bool:
        if self.condition is not None and not self.condition(rapport.etats[etat_id]):
            return False
        return respecte_jalons(rapport.chemin(etat_id), self.jalons, rapport.etats)

    def accepteur(self, cat):
        """Fonction `accepter(rapport, etat_id)` pour `explorer` : jalons, condition, et fin de tour si demandée."""
        if not self.en_fin_de_tour:
            return self.accepter

        def f(rapport, etat_id) -> bool:
            return (fin_de_tour_possible(cat, rapport.etats[etat_id])
                    and self._jalons_et_condition(rapport, etat_id))
        return f

    @property
    def main_de_depart(self) -> list[str]:
        return list(self.main) if self.main else [self.depart]

    @property
    def hors_jeu(self) -> list[str]:
        """Cartes de réponse retirées du jeu pour compléter la main à 5 cartes (règle du lot C3, § 5.2)."""
        return list(INERTES[: max(0, 5 - len(self.main_de_depart))])

    @property
    def etapes_realisables(self) -> int:
        """Nombre d'étapes avant la première qui passe par une carte absente."""
        for k, e in enumerate(self.etapes):
            if e.absente:
                return k
        return len(self.etapes)


MDM = "https://www.masterduelmeta.com/combo/"

GUIDES: tuple[ComboGuide, ...] = (
    ComboGuide(
        "G1", "Nadir Servant seule, branche « sans Droll »",
        (Source("TwilightSalt", "2026-07-19", MDM + "6a5d272ce5036dbe654fdf31"),
         Source("Mordred", "2026-08-28", MDM + "6a91128eb14e41d19f2eeca5")),
        NADIR,
        (Etape("Nadir Servant : envoie Titaniklad de l'Extra Deck au Cimetière, ajoute Fallen of the White Dragon"),
         Etape("Fallen of the White Dragon, effet 1 : envoie The Dragon that Devours the Dogma, s'Invoque"),
         Etape("Fallen of the White Dragon, effet 2 : Invoque Dogmatika Ecclesia du Deck"),
         Etape("Dogmatika Ecclesia : ajoute The Fallen & The Virtuous (posée : la Pose n'est pas codée, elle reste en main)"),
         Etape("Phase de Fin, Titaniklad : Invoque Guiding Quem du Deck ; Quem envoie Blazing Cartesia au Cimetière"),
         Etape("Phase de Fin, The Dragon that Devours the Dogma : ajoute The Fallen & The Virtuous"),
         Etape("The Fallen & The Virtuous : coût, un monstre de l'Extra Deck qui mentionne Albaz (guide : Albion the "
               "Branded Dragon) ; détruit Dogmatika Ecclesia"),
         Etape("Guiding Quem, effet 2 (une carte a quitté l'Extra Deck) : Invoque Blazing Cartesia du Cimetière"),
         Etape("Albion the Branded Dragon (Phase de Fin) : pose Branded Retribution", absente="Albion the Branded Dragon"),
         Etape("Suite au tour adverse : Fusion en Albion puis Khaos Starsource Dragon", absente="Khaos Starsource Dragon")),
        CibleExploration("G1 : White, Quem et Cartesia sur le terrain ; Titaniklad et Dogma au Cimetière",
                         (C("terrain", WHITE), C("terrain", QUEM), C("terrain", CART), C("cimetiere", TITAN),
                          C("cimetiere", DOGMA))),
        substitutions=("Coût de The Fallen & The Virtuous : Albion the Branded Dragon (absente) → n'importe quel "
                       "monstre de notre Extra Deck qui mentionne Albaz (même clause du texte)",),
        remarques=("Mordred (28/08) donne la même ligne, avec Albion the Branded Dragon qui détruit Dogmatika Ecclesia.",),
        jalons=(Jalon("activer", NADIR, 1, WHITE), Jalon("activer", WHITE, 1), Jalon("activer", TITAN, 3, QUEM),
                Jalon("activer", TFTV, 1, QUEM + "/2")),
    ),
    ComboGuide(
        "G2", "Fallen of the White Dragon seule, vers Ecclesia and the Dark Dragon et Granguignol",
        (Source("rickytau", "2026-06-04", MDM + "6a21b7fbd4f6ca4f21e03920"),
         Source("nerfmepls", "2026-06-16", MDM + "6a311f8ee8dd21fae6043715")),
        WHITE,
        (Etape("Fallen of the White Dragon, effet 1 : envoie un monstre qui mentionne Albaz (guide : Albion the Branded "
               "Dragon), s'Invoque"),
         Etape("Fallen of the White Dragon, effet 2 : Invoque Incredible Ecclesia du Deck"),
         Etape("Incredible Ecclesia : se Sacrifie, Invoque The Golden Swordsoul du Deck"),
         Etape("Invocation Synchro : Fallen of the White Dragon + The Golden Swordsoul → Ecclesia and the Dark Dragon"),
         Etape("Ecclesia and the Dark Dragon : se bannit jusqu'à la Phase de Fin, Invoque Blazing Cartesia du Deck"),
         Etape("The Golden Swordsoul (un monstre a été banni) : se bannit du Cimetière, Invoque Incredible Ecclesia du "
               "Cimetière"),
         Etape("Blazing Cartesia, effet 2 : Fusion Granguignol (Cartesia + Incredible Ecclesia), en Zone Monstre Extra"),
         Etape("Granguignol : envoie Titaniklad de l'Extra Deck au Cimetière"),
         Etape("Phase de Fin : Cartesia et Incredible Ecclesia reviennent en main ; Ecclesia and the Dark Dragon revient"),
         Etape("Albion the Branded Dragon : active Branded Opening (Aluber), Branded in Red…",
               absente="Albion the Branded Dragon")),
        CibleExploration("G2 : Granguignol et Ecclesia and the Dark Dragon sur le terrain ; Cartesia et Incredible "
                         "Ecclesia en main ; Titaniklad au Cimetière",
                         (C("terrain", GRANG), C("terrain", EDD), C("main", CART), C("main", IECC),
                          C("cimetiere", TITAN))),
        substitutions=("Coût de Fallen of the White Dragon : Albion the Branded Dragon (absente) → n'importe quel "
                       "monstre de notre Extra Deck qui mentionne Albaz",),
        remarques=("Les deux pages donnent la même séquence ; le plateau annoncé (Mirrorjade, Quem) passe ensuite par "
                   "Albion the Branded Dragon et Branded in Red, absentes.",),
        jalons=(Jalon("activer", WHITE, 1, IECC), Jalon("activer", IECC, 2, GS), Jalon("invocation_synchro", EDD),
                Jalon("activer", EDD, 1, GS + "/2"), Jalon("activer", CART, 2, GRANG + "/1"), Jalon("activer", CART, 3),
                Jalon("activer", IECC, 3)),
    ),
    ComboGuide(
        "G3", "Fallen of the White Dragon seule, par Guiding Quem et The Three Champions of Swordsoul",
        (Source("Mordred", "2026-08-28", MDM + "6a91053ec87cb24c69a2b7b7"),),
        WHITE,
        (Etape("Fallen of the White Dragon, effet 1 : envoie un monstre qui mentionne Albaz (guide : Albion the Branded "
               "Dragon), s'Invoque"),
         Etape("Fallen of the White Dragon, effet 2 : Invoque Incredible Ecclesia du Deck"),
         Etape("Invocation Synchro : Fallen of the White Dragon + Incredible Ecclesia → Ecclesia and the Dark Dragon"),
         Etape("Ecclesia and the Dark Dragon : se bannit, Invoque Guiding Quem du Deck"),
         Etape("Guiding Quem, effet 1 : envoie Tri-Brigade Springans Kitt du Deck au Cimetière"),
         Etape("Fallen of the White Dragon revient du Cimetière (page ambiguë ; lecture : effet de Tri-Brigade "
               "Springans Kitt envoyée au Cimetière)"),
         Etape("Invocation Synchro : Fallen of the White Dragon + Guiding Quem → The Three Champions of Swordsoul"),
         Etape("The Three Champions of Swordsoul : ajoute Blazing Cartesia"),
         Etape("Blazing Cartesia, effet 1 : s'Invoque de la main"),
         Etape("Blazing Cartesia, effet 2 : Fusion Granguignol (Cartesia + The Three Champions of Swordsoul)"),
         Etape("Suite (branches Droll / sans Droll) par Albion the Branded Dragon", absente="Albion the Branded Dragon")),
        CibleExploration("G3 : Granguignol sur le terrain ; The Three Champions of Swordsoul, Fallen of the White Dragon "
                         "et Guiding Quem au Cimetière",
                         (C("terrain", GRANG), C("cimetiere", CHAMP), C("cimetiere", WHITE), C("cimetiere", QUEM))),
        substitutions=("Coût de Fallen of the White Dragon : Albion the Branded Dragon (absente) → un monstre de notre "
                       "Extra Deck qui mentionne Albaz",),
        remarques=("L'étape 6 est mal étiquetée sur la page (« effet de Fallen of the White Dragon au Cimetière ») : la "
                   "cible ne fixe pas comment White revient, le moteur cherche toute façon légale.",),
        jalons=(Jalon("activer", WHITE, 1, IECC), Jalon("invocation_synchro", EDD), Jalon("activer", EDD, 1, QUEM),
                Jalon("invocation_synchro", CHAMP), Jalon("activer", CART, 1), Jalon("activer", CART, 2)),
    ),
    ComboGuide(
        "G4", "Fallen of the White Dragon seule, ligne « Fuwalos suspect » (Dogmatika Ecclesia, Quem)",
        (Source("Mordred", "2026-08-28", MDM + "6a9111ec57082c8c7e7b8a90"),),
        WHITE,
        (Etape("Fallen of the White Dragon, effet 1 : envoie The Dragon that Devours the Dogma, s'Invoque"),
         Etape("Fallen of the White Dragon, effet 2 : Invoque Dogmatika Ecclesia du Deck"),
         Etape("Dogmatika Ecclesia : ajoute Guiding Quem"),
         Etape("Invocation Normale de Guiding Quem ; Quem envoie Blazing Cartesia au Cimetière"),
         Etape("Phase de Fin, The Dragon that Devours the Dogma : ajoute The Fallen & The Virtuous"),
         Etape("The Fallen & The Virtuous : coût, un monstre de l'Extra Deck qui mentionne Albaz (guide : Albion the "
               "Branded Dragon), cible Dogmatika Ecclesia"),
         Etape("Guiding Quem, effet 2 : Invoque Blazing Cartesia du Cimetière"),
         Etape("Albion the Branded Dragon (Phase de Fin) : pose The Fallen & The Virtuous",
               absente="Albion the Branded Dragon")),
        CibleExploration("G4 : White, Quem et Cartesia sur le terrain ; Dogma au Cimetière",
                         (C("terrain", WHITE), C("terrain", QUEM), C("terrain", CART), C("cimetiere", DOGMA))),
        substitutions=("Coût de The Fallen & The Virtuous : Albion the Branded Dragon (absente) → un monstre de notre "
                       "Extra Deck qui mentionne Albaz",),
        jalons=(Jalon("activer", WHITE, 1, DECC), Jalon("invocation_normale", QUEM), Jalon("activer", DOGMA, 3, TFTV),
                Jalon("activer", TFTV, 1, QUEM + "/2")),
    ),
    ComboGuide(
        "G5", "Nadir Servant seule, branche « sous Droll » (sans recherche après Nadir)",
        (Source("TwilightSalt", "2026-07-19", MDM + "6a5d272ce5036dbe654fdf31"),),
        NADIR,
        (Etape("Nadir Servant : envoie Titaniklad, ajoute Fallen of the White Dragon"),
         Etape("Fallen of the White Dragon, effet 1 : envoie un monstre qui mentionne Albaz (guide : Albion the Branded "
               "Dragon), s'Invoque"),
         Etape("Fallen of the White Dragon, effet 2 : Invoque Incredible Ecclesia du Deck"),
         Etape("Phase de Fin, Titaniklad : Invoque Guiding Quem du Deck (la page s'arrête ici)"),
         Etape("Plateau annoncé : Incredible Ecclesia (Albaz du Deck), Quem (Cartesia du Cimetière), The Fallen & The "
               "Virtuous ; pas de séquence complète", absente="(page incomplète)")),
        CibleExploration("G5 : White, Incredible Ecclesia et Quem sur le terrain ; Titaniklad au Cimetière",
                         (C("terrain", WHITE), C("terrain", IECC), C("terrain", QUEM), C("cimetiere", TITAN))),
        substitutions=("Coût de Fallen of the White Dragon : Albion the Branded Dragon (absente) → un monstre de notre "
                       "Extra Deck qui mentionne Albaz",),
        jalons=(Jalon("activer", NADIR, 1, WHITE), Jalon("activer", WHITE, 1, IECC), Jalon("activer", TITAN, 3, QUEM)),
    ),
)

# ── Lot J2 plein (TOK-139 figé, TOK-140 traduit) ────────────────────────────────────────────────────────────────
# Traduction mot à mot de `combos-guides.md` § 5 (section figée, empreinte dans le commit TOK-139) : main, cible et
# jalons ; cible évaluée en fin de tour (§ 5.2). Les étapes ne sont pas recopiées ici : le document fait foi.
TCG5 = "docs/moteur-combos/combos-guides.md § 5"
M = Mouvement
SUB_ALBION = ("Coûts payés dans le guide par Albion the Branded Dragon (absente) : n'importe quel monstre de notre "
              "Extra Deck qui remplit la même condition (§ 2 et § 5.2)",)

# Cible de G6 telle que figée par le commit TOK-139 (avant correction) : gardée pour la mesure « tel que figé ».
CIBLE_G6_FIGEE = CibleExploration(
    "G6 (figée) : White, Dogmatika Ecclesia, Quem et Cartesia sur le terrain ; Rindbrumm, Titaniklad et Cocatorium au "
    "Cimetière ; Mercourier banni",
    (C("terrain", WHITE), C("terrain", DECC), C("terrain", QUEM), C("terrain", CART), C("cimetiere", RIND),
     C("cimetiere", TITAN), C("cimetiere", COCA), C("bannies", MERC)))

GUIDES_J2_PLEIN: tuple[ComboGuide, ...] = (
    ComboGuide(
        "G6", "Branded Fusion seule", (Source("Master Game", "2026-06-07", MDM + "6a2585f47c53112dc8c296ff"),),
        BFUSION, (Etape(TCG5 + ", G6, étapes 1 à 7"), Etape("étape 8", absente="Albion the Branded Dragon")),
        # Cible corrigée (commit TOK-139 séparé) : la version figée ajoutait « Cocatorium au Cimetière », inatteignable
        # (banni en quittant le terrain) ; voir `CIBLE_G6_FIGEE` et combos-guides.md § 5, G6.
        CibleExploration("G6 : White, Dogmatika Ecclesia, Quem et Cartesia sur le terrain ; Rindbrumm et Titaniklad au "
                         "Cimetière ; Mercourier banni",
                         (C("terrain", WHITE), C("terrain", DECC), C("terrain", QUEM), C("terrain", CART),
                          C("cimetiere", RIND), C("cimetiere", TITAN), C("bannies", MERC))),
        substitutions=SUB_ALBION, main=(BFUSION,), lot="J2 plein", en_fin_de_tour=True,
        jalons=(JalonPas("(1) activation de Branded Fusion", "activer", BFUSION),
                JalonPas("(2) Invocation Fusion de Rindbrumm", mouvements=(M(RIND, "terrain", "extra"),)),
                JalonPas("(3) Invocation Spéciale de Cocatorium depuis le Cimetière",
                         mouvements=(M(COCA, "terrain", "cimetiere"),)),
                JalonPas("(4) effet de Mercourier banni", contient=(MERC + "/2",)),
                JalonPas("(5) Invocation Spéciale de White depuis la main", mouvements=(M(WHITE, "terrain", "main"),)),
                JalonPas("(6) Invocation Spéciale de Dogmatika Ecclesia", mouvements=(M(DECC, "terrain"),)),
                JalonPas("(7) Invocation Spéciale de Quem par Titaniklad", "activer", TITAN,
                         mouvements=(M(QUEM, "terrain"),)),
                JalonPas("(8) activation de The Fallen & The Virtuous", "activer", TFTV),
                JalonPas("(9) Invocation Spéciale de Cartesia depuis le Cimetière",
                         mouvements=(M(CART, "terrain", "cimetiere"),))),
    ),
    ComboGuide(
        "G7", "Aluber + Mulcharmy Fuwalos, vers Mirrorjade",
        (Source("combatant", "2026-06-17", MDM + "6a330ada9026d5cfa564d08e"),
         Source("SirRichard Alt", "2026-06-23", MDM + "6a3a064927d579237da6ca51")),
        ALUBER, (Etape(TCG5 + ", G7, étapes 1 à 8 et 10"), Etape("étape 9", absente="PSY-Framelord Omega")),
        CibleExploration("G7 : Mirrorjade, Ecclesia and the Dark Dragon, Quem et Cartesia sur le terrain ; Rindbrumm "
                         "et Three Champions au Cimetière",
                         (C("terrain", MIRROR), C("terrain", EDD), C("terrain", QUEM), C("terrain", CART),
                          C("cimetiere", RIND), C("cimetiere", CHAMP))),
        main=(ALUBER, FUWALOS), lot="J2 plein", en_fin_de_tour=True,
        jalons=(JalonPas("(1) Invocation Normale d'Aluber", "invocation_normale", ALUBER),
                JalonPas("(2) activation de Branded in High Spirits", "activer", BHIGH),
                JalonPas("(3) Invocation Spéciale de White depuis la main", mouvements=(M(WHITE, "terrain", "main"),)),
                JalonPas("(4) Invocation Spéciale d'Incredible Ecclesia", mouvements=(M(IECC, "terrain"),)),
                JalonPas("(5) Invocation Spéciale de The Golden Swordsoul", mouvements=(M(GS, "terrain"),)),
                JalonPas("(6) Invocation Synchro d'Ecclesia and the Dark Dragon", "invocation_synchro", EDD),
                JalonPas("(7) Invocation Spéciale de Quem", mouvements=(M(QUEM, "terrain"),)),
                JalonPas("(8) Invocation Synchro de The Three Champions of Swordsoul", "invocation_synchro", CHAMP),
                JalonPas("(9) Invocation Fusion de Mirrorjade", mouvements=(M(MIRROR, "terrain", "extra"),))),
    ),
    ComboGuide(
        "G8", "Aluber + Fallen of Albaz, branche sans Bystial",
        (Source("mikethaguy", "2026-06-14", MDM + "6a2e53bbc1791e881a6e4489"),),
        ALUBER, (Etape(TCG5 + ", G8, étapes 1 à 8 (sauf Albion)"),
                 Etape("étape 8, Albion", absente="Albion the Branded Dragon")),
        CibleExploration("G8 : Ecclesia and the Dark Dragon et Quem sur le terrain (plus Mercourier ou Cartesia) ; "
                         "Granguignol, Titaniklad, Dogma, Rindbrumm et Fallen of Albaz au Cimetière ; Incredible "
                         "Ecclesia en main",
                         (C("terrain", EDD), C("terrain", QUEM), C("cimetiere", GRANG), C("cimetiere", TITAN),
                          C("cimetiere", DOGMA), C("cimetiere", RIND), C("cimetiere", ALBAZ), C("main", IECC))),
        substitutions=SUB_ALBION, main=(ALUBER, ALBAZ), lot="J2 plein", en_fin_de_tour=True,
        condition=lambda e: compter(e, "terrain", MERC) + compter(e, "terrain", CART) >= 1,
        jalons=(JalonPas("(1) Invocation Normale d'Aluber", "invocation_normale", ALUBER),
                JalonPas("(2) activation de Branded in High Spirits", "activer", BHIGH),
                JalonPas("(3) Invocation Spéciale de White depuis la main", mouvements=(M(WHITE, "terrain", "main"),)),
                JalonPas("(4) Invocation Spéciale d'Incredible Ecclesia", mouvements=(M(IECC, "terrain"),)),
                JalonPas("(5) Invocation Synchro d'Ecclesia and the Dark Dragon", "invocation_synchro", EDD),
                JalonPas("(6) Invocation Spéciale de Cartesia depuis le Deck", mouvements=(M(CART, "terrain", "deck"),)),
                JalonPas("(7) Invocation Fusion de Granguignol", mouvements=(M(GRANG, "terrain", "extra"),)),
                JalonPas("(8) Invocation Spéciale de Quem par Titaniklad", "activer", TITAN,
                         mouvements=(M(QUEM, "terrain"),)),
                JalonPas("(9) activation de The Fallen & The Virtuous", "activer", TFTV),
                JalonPas("(10) Invocation Spéciale par Quem depuis le Cimetière", contient=(QUEM + "/2",),
                         mouvements=(M(None, "terrain", "cimetiere"),))),
    ),
    ComboGuide(
        "G9", "Gold Sarcophagus seule", (Source("kanna ogata", "2026-05-20", MDM + "6a0d96f302b04933a7d3effb"),),
        SARC, (Etape(TCG5 + ", G9, étapes 1 à 5 et 7 (sauf Albion)"),
               Etape("étape 6", absente="Branded Sword")),
        CibleExploration("G9 : Ecclesia and the Dark Dragon et Quem sur le terrain ; Incredible Ecclesia en main ; "
                         "Mercourier banni",
                         (C("terrain", EDD), C("terrain", QUEM), C("main", IECC), C("bannies", MERC))),
        main=(SARC,), lot="J2 plein", en_fin_de_tour=True,
        jalons=(JalonPas("(1) activation de Gold Sarcophagus", "activer", SARC),
                JalonPas("(2) effet de Mercourier banni", contient=(MERC + "/2",)),
                JalonPas("(3) Invocation Spéciale de White depuis la main", mouvements=(M(WHITE, "terrain", "main"),)),
                JalonPas("(4) Invocation Spéciale d'Incredible Ecclesia", mouvements=(M(IECC, "terrain"),)),
                JalonPas("(5) Invocation Synchro d'Ecclesia and the Dark Dragon", "invocation_synchro", EDD),
                JalonPas("(6) Invocation Spéciale de Quem", mouvements=(M(QUEM, "terrain"),))),
    ),
    ComboGuide(
        "G10", "Aluber + Fallen of the White Dragon, par Three Champions et Granguignol",
        (Source("critboi (alt)", "2026-06-06", MDM + "6a244c9d24e0dc6684a2ab22"),),
        ALUBER, (Etape(TCG5 + ", G10, étapes 1 à 8 et 10"),
                 Etape("étape 9", absente="Branded in Red")),
        CibleExploration("G10 : Three Champions, Granguignol et Ecclesia and the Dark Dragon sur le terrain ; "
                         "Titaniklad, Quem, White, Cartesia et Aluber au Cimetière",
                         (C("terrain", CHAMP), C("terrain", GRANG), C("terrain", EDD), C("cimetiere", TITAN),
                          C("cimetiere", QUEM), C("cimetiere", WHITE), C("cimetiere", CART),
                          C("cimetiere", ALUBER))),
        main=(ALUBER, WHITE), lot="J2 plein", en_fin_de_tour=True,
        jalons=(JalonPas("(1) Invocation Spéciale de White depuis la main", mouvements=(M(WHITE, "terrain", "main"),)),
                JalonPas("(2) Invocation Spéciale d'Incredible Ecclesia", mouvements=(M(IECC, "terrain"),)),
                JalonPas("(3) Invocation Synchro d'Ecclesia and the Dark Dragon", "invocation_synchro", EDD),
                JalonPas("(4) Invocation Spéciale de Quem", mouvements=(M(QUEM, "terrain"),)),
                JalonPas("(5) Invocation Spéciale de White depuis le Cimetière",
                         mouvements=(M(WHITE, "terrain", "cimetiere"),)),
                JalonPas("(6) Invocation Synchro de The Three Champions of Swordsoul", "invocation_synchro", CHAMP),
                JalonPas("(7) Invocation Spéciale de Cartesia depuis la main", mouvements=(M(CART, "terrain", "main"),)),
                JalonPas("(8) Invocation Normale d'Aluber", "invocation_normale", ALUBER),
                JalonPas("(9) Invocation Fusion de Granguignol", mouvements=(M(GRANG, "terrain", "extra"),))),
    ),
)

TOUS_LES_GUIDES: tuple[ComboGuide, ...] = GUIDES + GUIDES_J2_PLEIN

# G6 tel que figé (avant la correction de sa cible) : compté dans le chiffre principal (avis data-scientist-ygo).
G6_FIGE = replace(GUIDES_J2_PLEIN[0], gid="G6-figé", titre=GUIDES_J2_PLEIN[0].titre + " (cible figée, avant correction)",
                  cible=CIBLE_G6_FIGEE)
