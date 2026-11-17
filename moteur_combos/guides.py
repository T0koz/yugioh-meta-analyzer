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

from dataclasses import dataclass, field

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


def respecte_jalons(chemin, jalons) -> bool:
    """Les jalons apparaissent dans le chemin, dans l'ordre (sous-suite, d'autres transitions peuvent s'intercaler)."""
    k = 0
    for a in chemin:
        if k < len(jalons) and jalons[k].colle(a):
            k += 1
    return k == len(jalons)


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
    jalons: tuple[Jalon, ...] = ()

    def accepter(self, rapport, etat_id) -> bool:
        return respecte_jalons(rapport.chemin(etat_id), self.jalons)

    @property
    def main_de_depart(self) -> list[str]:
        return list(self.main) if self.main else [self.depart]

    @property
    def hors_jeu(self) -> list[str]:
        return [] if self.main else list(INERTES)

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
