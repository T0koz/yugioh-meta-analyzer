#!/usr/bin/env python3
"""Tests du garde-fou : `python .claude/hooks/test_garde_fou.py` (≈ 0,2 s, sans dépendance)."""
import json
import os
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).with_name("garde_fou.py")
CWD = "/repo"  # dépôt principal ; les cas « dans un worktree » passent leur propre cwd
CWD_WORKTREE = "/repo/.claude/worktrees/lot13"

BLOQUEES = [
    "git push",
    "git push origin main",
    "git push -u origin claude/x",
    "git -C /repo push origin main",
    "git -c core.editor=true push",
    "git push --force origin main",
    "git push -f",
    "git push --force-with-lease",
    "git commit --no-verify -m x",
    "git commit -n -m x",
    "git merge --no-verify x",
    "git add . && git commit -m x && git push",
    "cd /repo; git push",
    "echo ok | git push",
    "bash -c 'git push origin main'",
    "echo $(git push)",
    "rm -rf data",
    "rm -fr /repo/frontend",
    "rm -r -f frontend/.next",
    "rm --recursive --force data",
    "rm -rf ../../..",
    "rm -rf ~/code",
    "rm -rf /repo/.claude/worktrees/../data",
    "rm -rf .claude/worktrees",
    "rm -rf .claude/worktrees/a data",
    "sudo rm -rf /",
    "find data -name '*.tmp' -exec rm -rf {} ;",
    "cd frontend && npm run build && rm -rf .next",
]
AUTORISEES = [
    "git status",
    "git log --oneline -5",
    "git diff HEAD~1",
    "git merge --no-ff claude/lot13 -m 'Merge du lot 13'",
    "git worktree remove .claude/worktrees/lot13",
    "git worktree list",
    "git add CLAUDE.md",
    "git commit -q -m 'chore(outillage): hook'",
    "git commit -m \"texte qui parle de git push et de --no-verify\"",
    "git pull --rebase",
    "git branch --list",
    "git fetch origin",
    "echo 'git push est interdit'",
    "grep -rn 'git push' docs",
    ".venv/bin/python scripts/check.py --visuel",
    "cp data/serving.db data/backup_serving.db",
    "rm data/backup_serving.db",
    "rm -f .git/HEAD.lock",
    "rm -r .claude/worktrees/lot13",
    "rm -rf .claude/worktrees/lot13",
    "rm -rf /repo/.claude/worktrees/lot13/frontend/.next",
    "ls -la && cat context.md | head -5",
    "npm run build",
    "git commit -m \"$(cat <<'EOF'\nchore: message\n\nCo-Authored-By: x\nEOF\n)\"",
]


def lancer(commande: str, cwd: str = CWD) -> int:
    entree = json.dumps({"tool_name": "Bash", "tool_input": {"command": commande}, "cwd": cwd})
    return subprocess.run([sys.executable, str(HOOK)], input=entree, capture_output=True, text=True).returncode


def main() -> int:
    erreurs = [f"devait être BLOQUÉE : {c!r}" for c in BLOQUEES if lancer(c) != 2]
    erreurs += [f"devait être AUTORISÉE : {c!r}" for c in AUTORISEES if lancer(c) != 0]
    # Depuis un worktree, un chemin relatif reste dans le worktree (nettoyer son propre .next est légitime).
    erreurs += [f"worktree : devait être AUTORISÉE : {c!r}" for c in ("rm -rf frontend/.next", "rm -rf node_modules")
                if lancer(c, CWD_WORKTREE) != 0]
    erreurs += [f"worktree : devait être BLOQUÉE : {c!r}" for c in ("rm -rf /repo/data", "rm -rf ../../../data", "rm -rf ~/x")
                if lancer(c, CWD_WORKTREE) != 2]
    autre = subprocess.run([sys.executable, str(HOOK)], capture_output=True, text=True,
                           input=json.dumps({"tool_name": "Read", "tool_input": {"file_path": "x"}}))
    if autre.returncode != 0:
        erreurs.append("un outil autre que Bash doit passer")
    if erreurs:
        print("\n".join(erreurs))
        return 1
    print(f"✓ garde-fou : {len(BLOQUEES)} commandes bloquées, {len(AUTORISEES)} autorisées")
    return 0


if __name__ == "__main__":
    sys.exit(main())
