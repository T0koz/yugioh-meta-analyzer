"""
Mots et tournures interdits dans les textes du site (charte « ton et explication »).

    python scripts/check_copy.py            # avertissements, code de sortie 0
    python scripts/check_copy.py --strict   # code de sortie 1 s'il reste une occurrence
    python scripts/check_copy.py --dump     # liste de tous les textes visibles relevés (TSV)

Source des règles : `docs/charte-ton-et-explication.md` §1 et §5 (validée par Thomas le 17/11),
consigne de ton du 16/11 (`docs/planning/2026-11-17/regles.md`). Inventaire et propositions :
`docs/textes-avant-apres.md` (lot 16).

Le script ne lit que les textes **visibles** de `frontend/src/` : nœuds texte JSX et chaînes
littérales qui ressemblent à une phrase (lettre + espace, ou lettre accentuée). Commentaires,
imports, classes CSS, adresses et noms de variables sont écartés. L'extraction est heuristique :
un faux positif se déclare dans `ALLOW` (fichier + extrait exact), jamais en affaiblissant une règle.

Branché dans `scripts/check.py` en étape **non bloquante** tant que les textes du lot 16 ne sont
pas appliqués ; il passera en `--strict` ensuite.

Bibliothèque standard uniquement (tourne sans venv ni node_modules).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "frontend" / "src"

W = r"(?<![\wÀ-ÿ’'])"  # début de mot (lettres accentuées comprises)
E = r"(?![\wÀ-ÿ])"     # fin de mot

# (catégorie, motif, explication). Appliqués au texte visible seulement.
RULES: list[tuple[str, re.Pattern[str], str]] = [
    # Appels à l'action, impératifs adressés au lecteur (charte §1, §5 ; consigne du 16/11)
    ("appel à l'action", re.compile(
        W + r"(regarde[zs]?|essaie[sz]?|essayez|découvre[sz]?|découvrez|clique[sz]?|cliquez|inscri[st]|"
        r"inscrivez|commence[sz]?|commencez|profite[sz]?|profitez|explore[sz]?|explorez|testez|agir|agissez|"
        r"anticipez|surveille[sz]?|surveillez|achète|achetez|réessaie[sz]?|réessayez|voir la preuve|voir la|voir les?|"
        r"en savoir plus|n’attendez|n'attendez|ne ratez)" + E, re.I),
     "impératif ou appel à l'action : le site décrit, il ne dit pas quoi faire"),
    ("conseil", re.compile(r"à (surveiller|croiser|suivre de près|acheter|jouer absolument)" + E, re.I),
     "conseil ou consigne implicite"),
    # Promesses (charte §5)
    ("promesse", re.compile(
        W + r"(avant tout le monde|avant la méta|avant les autres|qui montent|qui monte|qui va|qui sera|"
        r"sera banni|seront bannies?|(?<!sans )garanties?|à coup sûr|longueur d’avance|longueur d'avance|"
        r"ne manquez|imbattable|mois prochain)" + E, re.I),
     "promesse : le site ne garantit ni ne prédit au-delà de ce qui est mesuré"),
    # Superlatifs non mesurés (charte §5)
    ("superlatif", re.compile(
        W + r"(incroyables?|révolutionnaires?|ultimes?|exceptionnel(le)?s?|parfaite?s?|idéale?s?|idéaux|"
        r"puissante?s?|indispensables?|incontournables?|(le|la|les) meilleure?s?|énormes?|spectaculaires?|"
        r"magiques?|trustent|écrasante?s?)" + E, re.I),
     "superlatif ou terme fort non mesuré : à remplacer par la mesure ou à supprimer"),
    # Vouvoiement commercial et tutoiement (charte §1)
    ("vouvoiement", re.compile(W + r"(vous|votre|vos)" + E, re.I), "vouvoiement commercial"),
    ("tutoiement", re.compile(W + r"(tu|ton|ta|tes|toi)" + E, re.I), "tutoiement adressé au lecteur"),
    # Ponctuation (charte §1, §5) ; « Yu-Gi-Oh! » est le nom de la marque.
    ("exclamation", re.compile(r"(?<!Yu-Gi-Oh)!(?![=\w])"), "point d'exclamation"),
    ("question", re.compile(r"\?\s*$"), "question (interdite dans un titre ; à vérifier ailleurs)"),
    # Notations de formule et noms de variables (charte §2, §5 : aucune formule affichée)
    ("formule", re.compile(
        r"[≥≤α∑Σσ√∝]|\b[a-z]+_[a-z_]+\b|\b(Jaccard|Ridge|Pearson|logit|z-score|p-value|AUC)\b|"
        r"\bp ?[<=] ?0[.,]\d|\w ?= ?[\w(]|\bα\b"),
     "notation de formule ou nom de variable affiché"),
]

# Faux positifs connus : (chemin relatif à frontend/src, extrait exact du texte).
ALLOW: set[tuple[str, str]] = set()

CODE_MARKERS = re.compile(
    r"\b(const|let|return|export|function|typeof|keyof|satisfies|type [A-Z]\w*|useRef|useState|import)\b|=>|\)\)|\?\?|"
    r"\w\.\w+\s*[?:(]|^\s*[;)]|[;{]\s*$|^\s*:\s")
CLASS_LIKE = re.compile(r"\]:|^\[&|^[\w:/\-\[\]\.%#()!,&>*~+@=' ]+$")


def strip_comments(code: str) -> str:
    """Remplace les commentaires par des espaces (numéros de ligne conservés), sans toucher aux chaînes."""
    out: list[str] = []
    i, n = 0, len(code)
    while i < n:
        c = code[i]
        if c in "\"'`":
            j = skip_string(code, i)
            out.append(code[i:j])
            i = j
        elif code.startswith("//", i) and (i == 0 or code[i - 1] != ":"):
            j = code.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i))
            i = j
        elif code.startswith("/*", i):
            j = code.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append(re.sub(r"[^\n]", " ", code[i:j]))
            i = j
        else:
            out.append(c)
            i += 1
    return "".join(out)


def skip_string(code: str, i: int, sink: list | None = None) -> int:
    """Fin de la chaîne qui commence en i. Les chaînes trouvées (y compris dans les `${}` d'un
    gabarit) sont ajoutées à `sink` sous la forme (début, texte)."""
    q, n, j = code[i], len(code), i + 1
    if q != "`":
        while j < n and code[j] != q and code[j] != "\n":
            j += 2 if code[j] == "\\" else 1
        if sink is not None:
            sink.append((i, code[i + 1:j]))
        return min(j + 1, n)
    parts: list[str] = []
    while j < n and code[j] != "`":
        if code[j] == "\\":
            parts.append(code[j:j + 2])
            j += 2
        elif code.startswith("${", j):
            depth, k = 1, j + 2
            while k < n and depth:
                if code[k] in "\"'`":
                    k = skip_string(code, k, sink)
                    continue
                depth += {"{": 1, "}": -1}.get(code[k], 0)
                k += 1
            parts.append("{…}")
            j = k
        else:
            parts.append(code[j])
            j += 1
    if sink is not None:
        sink.append((i, "".join(parts)))
    return min(j + 1, n)


def looks_like_text(s: str) -> bool:
    s = s.strip()
    if len(s) < 2 or not re.search(r"[A-Za-zÀ-ÿ]", s.replace("{…}", "")):
        return False
    if re.match(r"^(https?:|/|\.{1,2}/|@/|#|var\(|rgba?\(|url\(|[\w-]+-\{…\}$)", s):
        return False
    if re.search(r"\.(tsx?|css|png|webp|jpe?g|svg|woff2?|json|xml)\b", s) and " " not in s:
        return False
    has_accent = bool(re.search(r"[À-ÿ’«»…·→]", s.replace("{…}", "")))
    if " " not in s and not has_accent:
        return False
    if not has_accent and CLASS_LIKE.search(s) and re.search(r"[-:\[]", s):
        return False
    if CODE_MARKERS.search(s) or re.match(r"^(use |[\d.]+(px|deg|s)\b|M?\{…\} )", s):
        return False
    return True


SKIP_BEFORE = re.compile(
    r"((import|from|require\()\s*$)|"
    r"\b(className|class|href|src|key|id|type|role|rel|d|viewBox|fill|stroke|transform|style|variant|size|"
    r"as|lang|target|sizes|fetchPriority|loading|mode|kind|name|htmlFor|tone|color|fontFamily|"
    r"data-[\w-]+)\s*[=:]\s*\{?\s*$|\b(cn|clsx|cva|controlClass|getPropertyValue|querySelector)\(\s*$")
JSX_TEXT_RE = re.compile(r"(?<![=\-])>(?P<body>[^<>{}]*[A-Za-zÀ-ÿ][^<>{}]*)(?=<|\{)")
# Texte JSX qui suit une expression (`{" "}`, `<InfoTooltip … />{" "}`) et finit sur une balise.
JSX_AFTER_EXPR_RE = re.compile(r"\}(?P<body>[^<>{}]*[a-zà-ÿ]{3,} [^<>{}]*)(?=</|<[A-Za-z])")


def extract(path: Path) -> list[tuple[int, str]]:
    code = strip_comments(path.read_text(encoding="utf-8"))
    found: list[tuple[int, str]] = []
    strings: list[tuple[int, str]] = []
    i, n = 0, len(code)
    mask = list(code)
    while i < n:
        if code[i] in "\"'`":
            j = skip_string(code, i, strings)
            for k in range(i, j):  # masque les chaînes pour la recherche des nœuds texte JSX
                if mask[k] != "\n":
                    mask[k] = " "
            i = j
        else:
            i += 1
    for start, body in strings:
        if SKIP_BEFORE.search(code[max(0, start - 60):start]):
            continue
        if looks_like_text(body):
            found.append((code.count("\n", 0, start) + 1, " ".join(body.split())))
    if path.suffix == ".tsx":
        # Les balises de mise en valeur (<Em>, <strong>…) ne coupent pas une phrase.
        masked = re.sub(r"</?(Em|strong|b|em)\b[^<>{}]*>", lambda m: " " * len(m.group(0)), "".join(mask))
        for m in [*JSX_TEXT_RE.finditer(masked), *JSX_AFTER_EXPR_RE.finditer(masked)]:
            body = " ".join(m.group("body").split())
            if body and re.search(r"[A-Za-zÀ-ÿ]", body) and not CODE_MARKERS.search(body) and "&&" not in body:
                lead = len(m.group("body")) - len(m.group("body").lstrip())
                found.append((masked.count("\n", 0, m.start("body") + lead) + 1, body))
    return sorted(set(found))


def files() -> list[Path]:
    return sorted(p for p in SRC.rglob("*") if p.suffix in {".ts", ".tsx"} and not p.name.endswith(".d.ts")
                  and "/tests/" not in p.as_posix())


def scan() -> tuple[int, list[tuple[str, int, str, str, str]]]:
    hits, total = [], 0
    for path in files():
        rel = path.relative_to(SRC).as_posix()
        for line, text in extract(path):
            total += 1
            if (rel, text) in ALLOW:
                continue
            for cat, rx, _ in RULES:
                m = rx.search(text)
                if m:
                    hits.append((rel, line, cat, m.group(0).strip(), text))
    return total, hits


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--strict", action="store_true", help="code de sortie 1 s'il reste une occurrence")
    parser.add_argument("--dump", action="store_true", help="lister tous les textes visibles relevés (TSV)")
    args = parser.parse_args()

    if args.dump:
        for path in files():
            for line, text in extract(path):
                print(f"{path.relative_to(SRC).as_posix()}:{line}\t{text}")
        return 0

    total, hits = scan()
    by_cat: dict[str, int] = {}
    for rel, line, cat, word, text in hits:
        by_cat[cat] = by_cat.get(cat, 0) + 1
        excerpt = text if len(text) <= 110 else text[:107] + "…"
        print(f"  {rel}:{line}  [{cat}] « {word} »  —  {excerpt}")
    summary = ", ".join(f"{c} {k}" for c, k in sorted(by_cat.items(), key=lambda x: -x[1])) or "aucune"
    print(f"Textes lus : {total} ; occurrences : {len(hits)} ({summary})")
    return 1 if (args.strict and hits) else 0


if __name__ == "__main__":
    sys.exit(main())
