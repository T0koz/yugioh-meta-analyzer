#!/usr/bin/env python3
"""Garde-fou PreToolUse (Bash) du projet — sans dépendance.

Lit sur stdin le JSON du hook (tool_name, tool_input.command, cwd) et refuse (code de sortie 2,
message sur stderr) :
  - tout `git push`, sous toutes ses formes (`git -C dir push`, `git -c k=v push`…) ;
  - `--force`, `--force-with-lease`, `-f` sur un push ; `--no-verify` sur toute commande git ;
  - `rm -rf` / `rm -fr` / `rm -r -f` dont une cible est hors de `.claude/worktrees/`.
Tout le reste passe (`git merge --no-ff`, `git worktree remove`, `git commit`, `rm fichier`…).

Pourquoi : deux personnes poussent sur `main` sans revue, dépôt public. Le push se fait par Thomas,
depuis son terminal, après `python scripts/check.py`. Tests : `python .claude/hooks/test_garde_fou.py`.
"""
from __future__ import annotations

import json
import os
import re
import shlex
import sys

OPERATEURS = {";", "&", "&&", "|", "||", "|&", "(", ")", "\n"}
WRAPPERS = {"sudo", "env", "command", "nohup", "time", "exec", "xargs", "nice", "builtin"}
SHELLS = {"bash", "sh", "zsh"}
GIT_OPTIONS_AVEC_VALEUR = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path", "--super-prefix"}

AIDE_PUSH = (
    "Le push est réservé à Thomas : il se fait depuis son terminal, après `python scripts/check.py` "
    "(et un `git pull --rebase`). Prépare les commits, dis ce qui reste à pousser, puis arrête-toi."
)


def tokeniser(commande: str) -> list[str]:
    lex = shlex.shlex(commande, posix=True, punctuation_chars=";&|()\n")
    lex.whitespace = " \t\r"
    lex.whitespace_split = True
    lex.commenters = ""
    return list(lex)


def segments(commande: str) -> list[list[str]]:
    segs: list[list[str]] = [[]]
    for tok in tokeniser(commande):
        if tok and set(tok) <= set(";&|()\n"):  # opérateur (peut être « && », « ;; »…)
            if segs[-1]:
                segs.append([])
        else:
            segs[-1].append(tok)
    return [s for s in segs if s]


def sous_commandes(tok: str) -> list[str]:
    """Contenu de $(...) et `...` dans un mot (ils s'exécutent même entre guillemets doubles)."""
    return re.findall(r"\$\(([^()]*)\)", tok) + re.findall(r"`([^`]*)`", tok)


def cible_autorisee(cible: str, cwd: str) -> bool:
    if "$" in cible or "`" in cible or cible.startswith("~"):
        return False  # impossible à résoudre : on refuse par prudence
    chemin = os.path.normpath(cible if os.path.isabs(cible) else os.path.join(cwd, cible))
    return "/.claude/worktrees/" in chemin + "/" and not chemin.endswith("/.claude/worktrees")


def analyser_rm(args: list[str], cwd: str) -> str | None:
    recursif = force = False
    cibles: list[str] = []
    fin_options = False
    for a in args:
        if not fin_options and a == "--":
            fin_options = True
        elif not fin_options and a.startswith("--"):
            recursif |= a == "--recursive"
            force |= a == "--force"
        elif not fin_options and a.startswith("-") and len(a) > 1:
            recursif |= any(c in a[1:] for c in "rR")
            force |= "f" in a[1:]
        else:
            cibles.append(a)
    if recursif and force:
        for c in cibles or ["(aucune cible)"]:
            if not cible_autorisee(c, cwd):
                return (f"`rm -rf` refusé hors de `.claude/worktrees/` (cible : {c}). Supprime un fichier isolé "
                        "avec `rm fichier`, ou un worktree avec `git worktree remove`.")
    return None


def analyser_git(args: list[str]) -> str | None:
    sous = None
    i = 0
    while i < len(args):
        a = args[i]
        if a in GIT_OPTIONS_AVEC_VALEUR:
            i += 2
            continue
        if a.startswith("-"):
            i += 1
            continue
        sous = a
        break
    reste = args[i + 1:] if sous else args
    if "--no-verify" in args:
        return "`--no-verify` refusé : les vérifications (`python scripts/check.py`) ne se contournent pas."
    if sous == "push":
        return "`git push` refusé. " + AIDE_PUSH
    if sous == "commit" and any(a.startswith("-") and not a.startswith("--") and "n" in a[1:] and a != "-m"
                                and not any(c in a for c in "mFCcu") for a in reste):
        return "`git commit -n` (= --no-verify) refusé : les vérifications ne se contournent pas."
    return None


def analyser_segment(seg: list[str], cwd: str, profondeur: int) -> str | None:
    for tok in seg:
        for inner in sous_commandes(tok):
            motif = analyser(inner, cwd, profondeur + 1)
            if motif:
                return motif
    i = 0
    while i < len(seg) and (seg[i] in WRAPPERS or re.fullmatch(r"\w+=.*", seg[i])):
        i += 1
        while i < len(seg) and seg[i].startswith("-") and seg[i - 1] in WRAPPERS:
            i += 1  # options du wrapper (sudo -u, xargs -n1…)
    if i >= len(seg):
        return None
    cmd, args = os.path.basename(seg[i]), seg[i + 1:]
    if cmd == "git":
        return analyser_git(args)
    if cmd == "rm":
        return analyser_rm(args, cwd)
    if cmd in SHELLS and "-c" in args and args.index("-c") + 1 < len(args):
        return analyser(args[args.index("-c") + 1], cwd, profondeur + 1)
    if cmd == "find" and "-exec" in args:  # find … -exec rm -rf {} ;
        j = args.index("-exec")
        return analyser_segment(args[j + 1:], cwd, profondeur + 1)
    return None


def analyser(commande: str, cwd: str, profondeur: int = 0) -> str | None:
    if profondeur > 4:
        return None
    try:
        segs = segments(commande)
    except ValueError:  # guillemet non fermé : repli sur une recherche brute, par prudence
        if re.search(r"\bgit\b.*\bpush\b", commande):
            return "`git push` refusé. " + AIDE_PUSH
        if "--no-verify" in commande:
            return "`--no-verify` refusé."
        return None
    for seg in segs:
        motif = analyser_segment(seg, cwd, profondeur)
        if motif:
            return motif
    return None


def main() -> int:
    try:
        donnees = json.load(sys.stdin)
    except Exception:
        return 0  # entrée illisible : ne pas bloquer le travail sur une erreur du hook
    if donnees.get("tool_name") != "Bash":
        return 0
    commande = (donnees.get("tool_input") or {}).get("command") or ""
    motif = analyser(commande, donnees.get("cwd") or os.getcwd())
    if motif:
        print(f"Garde-fou du projet (.claude/hooks/garde_fou.py) : {motif}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
