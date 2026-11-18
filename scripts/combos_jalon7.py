"""Jalon n°7 (TOK-144) : le moteur joue l'échantillon J1 de l'oracle et compte selon la règle figée.

Sortie : une ligne par situation (accord / désaccord / non tranché), le statut des 20 effets tirés, les deux taux
(principal et pessimiste) avec l'intervalle de Wilson à 95 % et l'estimation pondérée par strate.
Second compte (30 situations J1, moteur du lot C2 et moteur actuel) et cartes qui remplissent la règle `verifiee`.
`--json <fichier>` écrit les relevés. Sans `--ecrire-statuts`, lecture seule. `--ecrire-statuts` passe en `verifiee`
(`verified_by = oracle`) les cartes qui remplissent la règle, dans `data/combos.db` du checkout (après
`python scripts/combos_harnais.py`, qui calcule `formalisee`) : sauvegarde à côté, une seule transaction, jamais
`yugioh.db` ni `serving.db`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))

from moteur_combos import chemins  # noqa: E402
from moteur_combos.base import ouvrir_reference  # noqa: E402
from moteur_combos.cartes import FORMALISATIONS  # noqa: E402
from moteur_combos.catalogue import construire_catalogue  # noqa: E402
from moteur_combos.deck import charger_deck, lire_textes, tous_les_noms  # noqa: E402
from moteur_combos import regles  # noqa: E402
from moteur_combos.echantillon_oracle import (  # noqa: E402
    RESERVES_HORS_REGLE, comparer_tout, compter, second_compte, situations_des_lots_precedents, statuts_verifiee,
)
from moteur_combos.harnais import couverture  # noqa: E402


def catalogue_et_deck():
    deck = charger_deck(chemins.DECK_SOURCE)
    con = ouvrir_reference(chemins.base_de_reference())
    try:
        cat = construire_catalogue(deck, lire_textes(con, [c.card_id for c in deck.cartes]), tous_les_noms(con),
                                   FORMALISATIONS)
    finally:
        con.close()
    return cat, deck


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", type=Path)
    ap.add_argument("--ecrire-statuts", action="store_true")
    args = ap.parse_args(argv)
    cat, deck = catalogue_et_deck()
    comps = comparer_tout(cat, deck)
    for c in comps:
        print(f"{c.id:<5} {'/'.join(c.effets):<12} {c.issue:<11} {' ; '.join(c.ecarts)}")
    r = compter(comps)
    print("\nEffets tirés :")
    for e, s in r["statut"].items():
        print(f"  {e:<12} {s}")
    for nom in ("principal", "pessimiste"):
        k, n = r[nom]
        lo, hi = r[f"{nom}_wilson"]
        (ea, na), (eb, nb) = r[f"{nom}_strates"]
        print(f"\n{nom} : {k}/{n} effets en erreur ({k / n:.1%}), Wilson 95 % [{lo:.1%} ; {hi:.1%}] ; "
              f"strate a {ea}/{na}, strate b {eb}/{nb}, pondéré {r[f'{nom}_pondere']:.1%}")
    print(f"\nCritère J1 appliqué au moteur courant (borne haute ≤ 20 %) : principal "
          f"{'rempli' if r['j1_atteint'] else 'non rempli'}, pessimiste "
          f"{'rempli' if r['j1_atteint_pessimiste'] else 'non rempli'}. Le taux de J1 est celui du moteur mesuré "
          "(commit 2902df8, j1-rapport.md § 9) ; sur un moteur corrigé en voyant ces situations, ce chiffre n'est "
          "pas une mesure.")
    print(f"Situations : {sum(c.issue == 'accord' for c in comps)} accords, "
          f"{sum(c.issue == 'desaccord' for c in comps)} désaccords, "
          f"{sum(c.issue == 'non_tranche' for c in comps)} non tranchées, sur {len(comps)}")
    lots = situations_des_lots_precedents(cat, deck)
    sc = second_compte(lots)
    print("\nSecond compte (30 situations J1, effets exercés) :")
    for nom in ("lot_C2", "actuel"):
        k, n = sc[nom]["principal"]
        kp, np_ = sc[nom]["pessimiste"]
        lo, hi = sc[nom]["wilson"]
        err = sorted(f"{a.split(',')[0]} {b}" for (a, b), s in sc[nom]["statut"].items() if s == "erreur")
        print(f"  moteur {nom} : {k}/{n} en erreur, Wilson [{lo:.1%} ; {hi:.1%}] ; pessimiste {kp}/{np_} ; "
              f"erreurs : {', '.join(err) or 'aucune'}")
    regles.EXERCES.clear()
    for c in comps:
        regles.EXERCES.update(c.exerces)
    for _, _, ex in lots:
        regles.EXERCES.update(ex)
    couv = couverture(cat)
    st = statuts_verifiee(cat, comps, lots, couv)
    ok = [n for n, (v, _) in st.items() if v]
    print(f"\nCartes qui remplissent la règle `verifiee` : {len(ok)} sur {len(st)}")
    for n, (v, raisons) in st.items():
        print(f"  {'✓' if v else '✗'} {n}" + ("" if v else " — " + " ; ".join(raisons)))
    a_ecrire = [n for n in ok if n not in RESERVES_HORS_REGLE]
    for n in ok:
        if n in RESERVES_HORS_REGLE:
            print(f"  réserve déclarée, non passée : {n} — {RESERVES_HORS_REGLE[n]}")
    print(f"Cartes à passer en `verifiee` (règle figée moins les réserves déclarées) : {len(a_ecrire)}")
    if args.ecrire_statuts:
        ecrire_statuts(a_ecrire)
    if args.json:
        args.json.write_text(json.dumps([{"id": c.id, "effets": c.effets, "issue": c.issue, "ecarts": c.ecarts,
                                          "releve": {k: sorted(v) if isinstance(v, set) else v
                                                     for k, v in c.releve.items()},
                                          "exerces": sorted(map(list, c.exerces)), "conventions": c.conventions}
                                         for c in comps], ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


def ecrire_statuts(noms: list[str]) -> None:
    import shutil
    import sqlite3
    from datetime import datetime, timezone

    base = chemins.COMBOS_DB
    if not base.exists():
        raise SystemExit(f"{base} absente : lancer d'abord python scripts/combos_harnais.py")
    horodatage = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    sauvegarde = base.with_name(f"combos_avant_jalon7_{horodatage}.db")
    shutil.copy2(base, sauvegarde)
    con = sqlite3.connect(base, isolation_level=None)
    try:
        con.execute("BEGIN IMMEDIATE")
        avant = dict(con.execute("SELECT name, status FROM cb_card").fetchall())
        pas_formalisees = [n for n in noms if avant.get(n) not in ("formalisee", "verifiee")]
        if pas_formalisees:
            raise RuntimeError(f"cartes non `formalisee` dans la base : {pas_formalisees}")
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        for n in noms:
            con.execute("UPDATE cb_card SET status = 'verifiee', verified_by = 'oracle', status_reason = ?, "
                        "updated_at = ? WHERE name = ?",
                        ("jalon n°7 (TOK-144) : chaque effet du pilote en accord avec l'oracle, aucun désaccord", now, n))
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        raise
    finally:
        con.close()
    print(f"\n{len(noms)} cartes passées en `verifiee` dans {base} (sauvegarde : {sauvegarde.name})")


if __name__ == "__main__":
    raise SystemExit(main())
