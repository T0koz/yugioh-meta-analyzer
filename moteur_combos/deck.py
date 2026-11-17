"""Chargement du deck source, lecture des textes, noms et archétypes, validité du deck.

Lecture de textes, pas d'interprétation de règles : on extrait des clauses (« always treated as »,
« once per turn ») pour les **enregistrer** et vérifier que le schéma sait les représenter.
Ce qu'elles font en jeu est de la tranche 0.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from .base import maintenant
from .modele import CARTES_LISANT_LA_POSITION

ZONES_DECK = ("main", "extra", "side")


@dataclass(frozen=True)
class CarteDeck:
    nom: str
    card_id: int
    zone: str
    nombre: int
    type: str | None
    attribut: str | None
    race: str | None
    niveau: int | None
    atk: int | None
    defense: int | None
    ban_tcg: str | None
    text_sha256: str | None


@dataclass(frozen=True)
class DeckSource:
    ref: str
    libelle: str
    format: str | None
    liste: str | None
    fichier: Path
    fichier_sha256: str
    cartes: tuple[CarteDeck, ...]

    def par_nom(self) -> dict[str, CarteDeck]:
        """Une entrée par nom (une carte n'est que dans une zone dans ce deck ; vérifié par `charger_deck`)."""
        return {c.nom: c for c in self.cartes}

    def total(self, zone: str) -> int:
        return sum(c.nombre for c in self.cartes if c.zone == zone)


@dataclass
class TexteCarte:
    card_id: int
    nom: str
    texte: str
    frame_type: str | None

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.texte.encode()).hexdigest()


def charger_deck(chemin: Path) -> DeckSource:
    brut = chemin.read_bytes()
    data = json.loads(brut)
    cartes = tuple(
        CarteDeck(
            nom=c["name"], card_id=c["card_id"], zone=c["zone"], nombre=c["amount"], type=c["type"],
            attribut=c["attribute"], race=c["race"], niveau=c["level"], atk=c["atk"], defense=c["def"],
            ban_tcg=c["ban_tcg"], text_sha256=c["text_sha256"],
        )
        for c in data["cards"]
    )
    erreurs = []
    for c in cartes:
        if c.zone not in ZONES_DECK:
            erreurs.append(f"{c.nom} : zone inconnue {c.zone!r}")
        if c.card_id is None:
            erreurs.append(f"{c.nom} : absente de la table cards")
    doublons = [n for n, k in Counter(c.nom for c in cartes).items() if k > 1]
    if doublons:  # le chargement des départs suppose une seule zone d'origine par nom
        erreurs.append(f"cartes présentes dans plusieurs zones du deck : {doublons}")
    if erreurs:
        raise ValueError("deck source invalide :\n  " + "\n  ".join(erreurs))
    deck = data["deck"]
    return DeckSource(
        ref=deck["id"],
        libelle=f"{deck.get('archetype')} — {deck.get('tournament_type')} — {str(deck.get('created'))[:10]}",
        format=deck.get("format"),
        liste=deck.get("list_name"),
        fichier=chemin,
        fichier_sha256=hashlib.sha256(brut).hexdigest(),
        cartes=cartes,
    )


def lire_textes(con_ref: sqlite3.Connection, card_ids: list[int]) -> dict[int, TexteCarte]:
    marques = ",".join("?" * len(card_ids))
    lignes = con_ref.execute(
        f"SELECT id, REPLACE(REPLACE(name, '<', ''), '>', '') AS nom, desc, frame_type "
        f"FROM cards WHERE id IN ({marques})",
        card_ids,
    ).fetchall()
    return {r["id"]: TexteCarte(r["id"], r["nom"], r["desc"] or "", r["frame_type"]) for r in lignes}


def tous_les_noms(con_ref: sqlite3.Connection) -> set[str]:
    return {r[0] for r in con_ref.execute("SELECT REPLACE(REPLACE(name, '<', ''), '>', '') FROM cards")}


def verifier_empreintes(deck: DeckSource, textes: dict[int, TexteCarte]) -> list[str]:
    """Écarts entre `text_sha256` du JSON et le texte lu dans la base (errata, ou base différente)."""
    ecarts = []
    for c in deck.cartes:
        t = textes.get(c.card_id)
        if t is None:
            ecarts.append(f"{c.nom} (id {c.card_id}) : absente de la base de référence")
        elif t.nom != c.nom:
            ecarts.append(f"{c.nom} : la base l'appelle {t.nom!r}")
        elif t.sha256 != c.text_sha256:
            ecarts.append(f"{c.nom} : texte changé depuis l'extraction ({c.text_sha256[:12]}… → {t.sha256[:12]}…)")
    return ecarts


# ── Noms et archétypes (definitions-et-schema.md § 3.5, R03, R11) ─────────────────────────────

# « always treated as "X" » (un nom) — guillemet juste après « as ».
_TRAITE_NOM = re.compile(r'always treated as "([^"]+)"')
# « always treated as a "X" and "Y" card » (des archétypes).
_TRAITE_ARCHETYPE = re.compile(r'always treated as an? ((?:"[^"]+"(?:,? (?:and|or) )?)+)\s*cards?\b')
# Une chaîne citée suivie d'un mot de catégorie : « "Despia" monster », « "Branded" Spell/Trap »…
_REFERENCE_CATEGORIE = re.compile(
    r'"([^"]+)"((?:,? (?:or|and) "[^"]+")*)\s+'
    r'(?:monsters?|cards?|Spells?|Traps?|Spell/Traps?|Fusion|Synchro|Tuner|Spell Cards?)\b'
)


def noms_traites_comme(texte: str) -> list[str]:
    return _TRAITE_NOM.findall(texte)


def archetypes_traites_comme(texte: str) -> list[str]:
    out = []
    for groupe in _TRAITE_ARCHETYPE.findall(texte):
        out += re.findall(r'"([^"]+)"', groupe)
    return out


def vocabulaire_archetypes(textes: list[str], noms_existants: set[str]) -> set[str]:
    """Archétypes cités par les textes : chaînes suivies d'une catégorie, moins les noms de cartes.
    (« "Fallen of Albaz" card » est un nom de carte, pas un archétype.)"""
    vocab = set()
    for t in textes:
        for m in _REFERENCE_CATEGORIE.finditer(t):
            vocab.add(m.group(1))
            vocab.update(re.findall(r'"([^"]+)"', m.group(2)))
    return {v for v in vocab if v not in noms_existants}


def etiquettes(nom: str, texte: str, vocabulaire: set[str]) -> set[tuple[str, str, str]]:
    """(tag, kind, origin) : noms portés et archétypes d'une carte.
    Archétype par le nom = le mot figure dans le nom imprimé (sous-chaîne, sensible à la casse :
    « Despian Luluwalilith » est « Despia » ; ⚖ hypothèse de lecture, cf. R11)."""
    tags = {(nom, "nom", "nom_imprime")}
    tags |= {(n, "nom", "traite_comme") for n in noms_traites_comme(texte)}
    tags |= {(a, "archetype", "nom_imprime") for a in vocabulaire if a in nom}
    tags |= {(a, "archetype", "traite_comme") for a in archetypes_traites_comme(texte)}
    # Une même étiquette peut venir du nom ET d'une clause : on garde l'origine « nom_imprime ».
    garde: dict[tuple[str, str], str] = {}
    for tag, kind, origin in sorted(tags, key=lambda x: x[2]):  # 'nom_imprime' < 'traite_comme'
        garde.setdefault((tag, kind), origin)
    return {(t, k, o) for (t, k), o in garde.items()}


# ── Validité du deck (§ 2.6) ───────────────────────────────────────────────────────────────────

LIMITE_BANLIST = {"Forbidden": 0, "Limited": 1, "Semi-Limited": 2}


def controle_validite(deck: DeckSource, noms_portes: dict[str, set[str]]) -> list[str]:
    """Contrôle de construction. `noms_portes[nom imprimé]` = noms de la carte (« always treated as » compris).
    Renvoie la liste des violations (vide = deck valide)."""
    violations = []
    if not 40 <= deck.total("main") <= 60:
        violations.append(f"Main Deck de {deck.total('main')} cartes (40 à 60)")
    if deck.total("extra") > 15:
        violations.append(f"Extra Deck de {deck.total('extra')} cartes (15 au plus)")
    if deck.total("side") > 15:
        violations.append(f"Side Deck de {deck.total('side')} cartes (15 au plus)")
    par_nom: dict[str, int] = defaultdict(int)
    detail: dict[str, list[str]] = defaultdict(list)
    for c in deck.cartes:
        for n in noms_portes.get(c.nom, {c.nom}):
            par_nom[n] += c.nombre
            detail[n].append(f"{c.nom} ×{c.nombre}")
    for n, k in sorted(par_nom.items()):
        if k > 3:
            violations.append(f"nom « {n} » : {k} exemplaires ({', '.join(detail[n])}) — 3 au plus")
    imprimes: dict[str, int] = defaultdict(int)
    for c in deck.cartes:
        imprimes[c.nom] += c.nombre
    for c in deck.cartes:
        plafond = LIMITE_BANLIST.get(c.ban_tcg or "", 3)
        if imprimes[c.nom] > plafond:
            violations.append(f"{c.nom} : {imprimes[c.nom]} exemplaires, statut {c.ban_tcg} ({plafond} au plus)")
    return sorted(set(violations))


# ── Clauses « une fois par tour » ──────────────────────────────────────────────────────────────

_CLAUSES_LIMITE = [
    ("activation_par_nom", re.compile(r'You can only activate 1 "([^"]+)" per turn')),
    ("par_nom_carte", re.compile(r'You can only use 1 "([^"]+)" effect per turn, and only once that turn')),
    ("par_nom_effet", re.compile(
        r'You can only use (?:this effect|each effect|each of the following effects) of "([^"]+)" once per turn')),
    ("invocation_par_nom", re.compile(r'You can only Special Summon "([^"]+)" once per turn')),
    ("par_exemplaire", re.compile(r"\bOnce per turn\b")),
]
_PHRASE_TOUR = re.compile(r"[^.\n]*\b(?:per turn|once per turn)\b[^.\n]*", re.IGNORECASE)


@dataclass
class AnalyseLimites:
    clauses: list[tuple[str, str | None]] = field(default_factory=list)  # (forme, nom cité)
    non_reconnues: list[str] = field(default_factory=list)
    nom_different: list[str] = field(default_factory=list)                # nom cité ≠ nom imprimé


def analyser_limites(nom: str, texte: str) -> AnalyseLimites:
    a = AnalyseLimites()
    for phrase in _PHRASE_TOUR.findall(texte):
        trouve = False
        for forme, motif in _CLAUSES_LIMITE:
            for m in motif.finditer(phrase):
                trouve = True
                cite = m.group(1) if m.groups() else None
                a.clauses.append((forme, cite))
                if cite is not None and cite != nom:
                    a.nom_different.append(cite)
        if not trouve:
            a.non_reconnues.append(phrase.strip())
    return a


# ── Écriture dans combos.db ────────────────────────────────────────────────────────────────────

def enregistrer_carte(con: sqlite3.Connection, carte: CarteDeck, texte: TexteCarte,
                      tags: set[tuple[str, str, str]]) -> str:
    """Insère ou met à jour une carte. Ne rétrograde jamais un statut, sauf si le texte a changé :
    alors la formalisation ne vaut plus, retour à `non_traitee` (détection d'errata).
    Renvoie 'nouvelle', 'inchangee' ou 'texte_change'."""
    maintenant_ = maintenant()
    homonyme = con.execute("SELECT card_id FROM cb_card WHERE name = ? AND card_id <> ?",
                           (carte.nom, carte.card_id)).fetchone()
    if homonyme is not None:
        # Piège connu : YGOPRODeck renumérote parfois une carte (même nom, autre id).
        raise ValueError(f"{carte.nom} : déjà en base sous l'id {homonyme['card_id']}, le deck dit {carte.card_id} "
                         "(renumérotation YGOPRODeck ?) — à traiter à la main, rien n'est écrit")
    raison_absent = "texte absent de la source" if not texte.texte else None
    ancienne = con.execute("SELECT text_sha256 FROM cb_card WHERE card_id = ?", (carte.card_id,)).fetchone()
    lit_position = int(carte.nom in CARTES_LISANT_LA_POSITION)
    valeurs = dict(
        card_id=carte.card_id, name=carte.nom, text=texte.texte, text_sha256=texte.sha256,
        text_fetched=maintenant_, frame_type=texte.frame_type, card_type=carte.type, attribute=carte.attribut,
        race=carte.race, level=carte.niveau, atk=carte.atk, def_=carte.defense, reads_position=lit_position,
        updated_at=maintenant_,
    )
    if ancienne is None:
        con.execute(
            "INSERT INTO cb_card (card_id, name, text, text_sha256, text_fetched, frame_type, card_type, attribute,"
            " race, level, atk, def, reads_position, status, status_reason, updated_at) VALUES (:card_id, :name,"
            " :text, :text_sha256, :text_fetched, :frame_type, :card_type, :attribute, :race, :level, :atk, :def_,"
            " :reads_position, 'non_traitee', :raison, :updated_at)",
            {**valeurs, "raison": raison_absent},
        )
        etat = "nouvelle"
    elif ancienne["text_sha256"] != texte.sha256:
        con.execute(
            "UPDATE cb_card SET name = :name, text = :text, text_sha256 = :text_sha256, text_fetched = :text_fetched,"
            " frame_type = :frame_type, card_type = :card_type, attribute = :attribute, race = :race, level = :level,"
            " atk = :atk, def = :def_, reads_position = :reads_position, status = 'non_traitee',"
            " status_reason = 'texte changé depuis la dernière lecture (errata ?)', verified_by = NULL,"
            " updated_at = :updated_at WHERE card_id = :card_id",
            valeurs,
        )
        # Les effets formalisés sur l'ancien texte ne valent plus rien non plus.
        con.execute("UPDATE cb_effect SET status = 'non_traitee' WHERE card_id = ?", (carte.card_id,))
        etat = "texte_change"
    else:
        con.execute("UPDATE cb_card SET reads_position = ? WHERE card_id = ?", (lit_position, carte.card_id))
        etat = "inchangee"
    con.execute("DELETE FROM cb_card_name_tag WHERE card_id = ?", (carte.card_id,))
    con.executemany(
        "INSERT INTO cb_card_name_tag (card_id, tag, kind, origin) VALUES (?, ?, ?, ?)",
        [(carte.card_id, t, k, o) for t, k, o in sorted(tags)],
    )
    return etat


def enregistrer_deck(con: sqlite3.Connection, deck: DeckSource, fichier_relatif: str) -> None:
    con.execute(
        "INSERT INTO cb_deck (deck_ref, label, format, list_name, source_file, source_sha256, loaded_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?) ON CONFLICT (deck_ref) DO UPDATE SET label = excluded.label,"
        " format = excluded.format, list_name = excluded.list_name, source_file = excluded.source_file,"
        " source_sha256 = excluded.source_sha256, loaded_at = excluded.loaded_at",
        (deck.ref, deck.libelle, deck.format, deck.liste, fichier_relatif, deck.fichier_sha256, maintenant()),
    )
    con.execute("DELETE FROM cb_deck_card WHERE deck_ref = ?", (deck.ref,))
    con.executemany(
        "INSERT INTO cb_deck_card (deck_ref, card_id, zone, amount, ban_tcg) VALUES (?, ?, ?, ?, ?)",
        [(deck.ref, c.card_id, c.zone, c.nombre, c.ban_tcg) for c in deck.cartes],
    )
