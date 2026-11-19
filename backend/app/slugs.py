"""Identifiant d'URL d'un archétype (TOK-101), sans accès à la base.

Les noms d'archétype portent des espaces, des barres obliques, des points et des
symboles (« Harpie/Amazoness », « D/D/D », « @Ignister », « Live☆Twin ») : aucun
ne passe tel quel dans un segment d'URL (un `%2F` est décodé ou refusé selon le
serveur). Le slug ne garde que a-z, 0-9 et le tiret.

Le slug est calculé ICI et servi par l'API (`slug`, `archetype_slug`) : le front
ne le recalcule jamais, il n'y a donc qu'une seule règle. La résolution inverse
(slug → nom) se fait en comparant les slugs de tous les archétypes connus.
"""

import hashlib
import re
import unicodedata


def slugify(name: str) -> str:
    """« Harpie/Amazoness » → « harpie-amazoness », « Live☆Twin » → « live-twin ».

    Un nom non vide sans aucun caractère a-z ou 0-9 (« ☆☆ », un nom en japonais) ne donne jamais un slug vide, qui
    ferait un lien `/decks/` cassé (TOK-149) : repli sur « x- » + 10 caractères de son empreinte SHA-1, stable d'un
    calcul à l'autre et déjà normalisé (`resolve` le retrouve). Aucun archétype n'est dans ce cas au 17/11 (231 noms).
    """
    decomposed = unicodedata.normalize("NFKD", name)
    without_accents = "".join(c for c in decomposed if not unicodedata.combining(c))
    slug = re.sub(r"[^a-z0-9]+", "-", without_accents.lower()).strip("-")
    if slug or not name.strip():
        return slug
    return "x-" + hashlib.sha1(name.encode("utf-8")).hexdigest()[:10]


def resolve(slug: str, names: list[str]) -> str | None:
    """Nom dont le slug vaut `slug`. `names` est trié par l'appelant : en cas de
    collision (aucune sur les 231 archétypes du 2026-11-17), le premier gagne.

    L'entrée est elle-même normalisée : « Branded » ou « BRANDED » rendent la page
    de « branded ». Ce n'est pas du confort : le cache de pages de Next est rangé
    par chemin, et sur un disque insensible à la casse (macOS) une 404 calculée pour
    « /archetype/Branded » écrasait la page de « /archetype/branded ». Avec la même
    réponse pour toutes les casses, il n'y a plus rien à écraser. L'adresse
    canonique reste le slug servi par l'API (`slug`), seul utilisé dans les liens.
    """
    wanted = slugify(slug)
    if not wanted:
        return None
    for name in names:
        if slugify(name) == wanted:
            return name
    return None
