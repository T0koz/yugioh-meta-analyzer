"""
Recalcule toute la chaîne dérivée dans le bon ordre (TOK-69).

    python scripts/refresh_all.py              # chaîne complète
    python scripts/refresh_all.py --from 05    # reprend à partir d'une étape (préfixe du nom)
    python scripts/refresh_all.py --list       # affiche l'ordre
    python scripts/refresh_all.py --no-fetch   # (défaut) ne rafraîchit pas les decks : voir refresh_decks.py

Choix de conception : les notebooks sont exécutés par `jupyter nbconvert --execute`
(copie exécutée dans logs/executed/, le notebook versionné n'est pas réécrit) plutôt
qu'extraits en scripts. Raison : les notebooks 02/04/05/10 pèsent ~68 000 caractères de
code ; les extraire créerait deux copies qui divergent (c'est déjà arrivé : banlist_features
et boutique_buy_signals ont perdu leur producteur quand le notebook 09 a été remplacé par un
script). Ici le notebook reste LA source ; le coût est un recalcul un peu plus lent et des
notebooks qui doivent rester exécutables de haut en bas (c'est donc aussi un test).
Exception : le notebook 11 (signal précoce) a été extrait dans `scripts/build_early_signals.py` au lot 20
(ticket A1 de l'audit de rigueur) ; il n'écrit plus en base, il n'y a donc qu'une source.

Ordre (dépendances) : fetch_new_cards → 02 → 04 (meta_scores) → banlist_features → 05 (prédictions) →
10 (alertes boutique) → buy_signals → early_signals (signal précoce) → ban_radar → card_impact
→ archetype_profiles (même fenêtre que la tier list, donc après 04) → log_predictions → build_serving_db --check → download_card_images (incrémental).
Un seul écrivain sur yugioh.db : tout est séquentiel, arrêt au premier échec.
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "logs" / "executed"
PY = sys.executable
NB = lambda n: ("nb", f"notebooks/{n}.ipynb")
SC = lambda *a: ("sc", [PY, *a])
STEPS = [
    # Cartes sorties depuis le dernier chargement (TOK-92) : ajoute seulement, ne réécrit rien. Pas
    # `fetch_cards.py` : il n'écrit qu'un JSON ; le rafraîchissement complet est `init_db.py`, qui écrase views_week.
    ("fetch_new_cards", SC("scripts/fetch_new_cards.py")),
    ("02_cooccurrence", NB("02_cooccurrence")),
    ("04_meta_score", NB("04_meta_score")),
    ("banlist_features", SC("scripts/build_banlist_features.py")),
    ("05_meta_prediction", NB("05_meta_prediction")),
    ("10_boutique_alert_score", NB("10_boutique_alert_score")),
    ("buy_signals", SC("scripts/build_buy_signals.py")),
    # TOK-103 : relevé de prix du jour (idempotent, ignoré s'il existe déjà), puis extrait des cartes du signal.
    # Avant, le relevé n'était pris qu'au lancement de Streamlit (run.sh) : d'où les trous de 2026.
    ("snapshot_prices", SC("scripts/snapshot_prices.py")),
    ("boutique_prices", SC("scripts/build_boutique_price_history.py")),
    # Lot 20 (A1) : le calcul du notebook 11 vit dans ce script (banlist à date, référence = dernier deck).
    ("early_signals", SC("scripts/build_early_signals.py")),
    ("ban_radar", SC("scripts/build_ban_radar.py")),
    ("card_impact", SC("scripts/build_card_impact.py")),
    ("archetype_profiles", SC("scripts/build_archetype_profiles.py")),
    ("log_predictions", SC("scripts/log_predictions.py")),
    ("serving_check", SC("scripts/build_serving_db.py", "--check")),
    # Dernier : un échec réseau sur les images ne doit pas bloquer les calculs ci-dessus. Incrémental.
    ("card_images", SC("scripts/download_card_images.py")),
]


def run(name, kind, target) -> bool:
    t0 = time.time()
    if kind == "nb":
        OUT.mkdir(parents=True, exist_ok=True)
        cmd = [PY, "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute", "--ExecutePreprocessor.timeout=1800",
               "--output-dir", str(OUT), target]
        cwd = ROOT / "notebooks"
        cmd[-1] = str(ROOT / target)
    else:
        cmd, cwd = target, ROOT
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    ok = p.returncode == 0
    print(f"[{name}] {'ok' if ok else 'ÉCHEC'} ({time.time() - t0:.0f} s)", flush=True)
    if not ok:
        print((p.stdout + p.stderr)[-1500:])
    return ok


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="start", default=None)
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    steps = STEPS
    if a.start:
        idx = next((i for i, (n, _) in enumerate(STEPS) if n.startswith(a.start)), None)
        if idx is None:
            print("étape inconnue"); return 2
        steps = STEPS[idx:]
    if a.list:
        for n, _ in steps: print(n)
        return 0
    for name, (kind, target) in steps:
        if not run(name, kind, target):
            return 1
    print("Chaîne complète OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
