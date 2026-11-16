"""
TOK-74 — Le signal d'achat de juin 2026 s'est-il réalisé ? (lecture seule)

    python scripts/analyze_signal_outcome.py [--backup data/backup_avant_nettoyage_20261116.db]

1. Part de Kewl Tune dans les decks légaux (deck_legality.legal = 1), TCG et OCG, par mois.
2. Variation Cardmarket entre 2026-06-19 et 2026-11-16 des cartes du signal du 2026-06-17
   (boutique_buy_signals de la sauvegarde — la table a été recalculée depuis), face au marché
   (toutes cartes à ≥ 1 € au départ). IC bootstrap sur les cartes.
Limites : une seule date de signal ; 34 cartes à ≥ 1 € regroupées en 10 archétypes ; les prix sont
des snapshots Cardmarket ponctuels ; aucune notion de ventes réelles.
"""
import argparse, sqlite3
import numpy as np, pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("--backup", default="data/backup_avant_nettoyage_20261116.db")
ap.add_argument("--d0", default="2026-06-19"); ap.add_argument("--d1", default="2026-11-16")
a = ap.parse_args()
con = sqlite3.connect("file:data/yugioh.db?mode=ro", uri=True)
con.execute(f"attach '{a.backup}' as bk")

d = pd.read_sql("select td.created,td.ocg,td.archetype from tournament_decks td join deck_legality dl on dl.deck_id=td.id where dl.legal=1", con)
d["m"] = d.created.str[:7]
for ocg, name in [(0, "TCG"), (1, "OCG")]:
    x = d[(d.ocg == ocg) & (d.m >= "2026-05")]
    t = x.groupby("m").size(); k = x[x.archetype == "Kewl Tune"].groupby("m").size().reindex(t.index, fill_value=0)
    h = x[x.archetype.str.contains("Kewl Tune", na=False)].groupby("m").size().reindex(t.index, fill_value=0)
    print(name, "\n", pd.DataFrame({"decks": t, "Kewl Tune": k, "% pur": (k / t * 100).round(1), "% avec hybrides": (h / t * 100).round(1)}))

sig = pd.read_sql("select archetype,card_name from bk.boutique_buy_signals", con)
px = pd.read_sql("select card_id,card_name,snapshot_date,cardmarket_price p from card_price_history where snapshot_date in (?,?)", con, params=(a.d0, a.d1))
p0 = px[px.snapshot_date == a.d0].set_index("card_id").p; p1 = px[px.snapshot_date == a.d1].set_index("card_id").p
nm = px.drop_duplicates("card_id").set_index("card_id").card_name
m = pd.DataFrame({"p0": p0, "p1": p1, "name": nm}).dropna(subset=["p0", "p1"]); m = m[m.p0 >= 1]; m["chg"] = m.p1 / m.p0 - 1
c = sig.merge(m, left_on="card_name", right_on="name").drop_duplicates("card_name")
rng = np.random.default_rng(0)
bs = [np.median(rng.choice(c.chg, len(c))) - np.median(rng.choice(m.chg, len(m))) for _ in range(3000)]
print(f"\nMarché ≥1 € : n={len(m)}, variation médiane {m.chg.median():+.1%}")
print(f"Signal : {len(c)} cartes distinctes (≥1 € au départ), médiane {c.chg.median():+.1%}, "
      f"écart vs marché IC95 [{np.percentile(bs,2.5):+.1%}, {np.percentile(bs,97.5):+.1%}]")
print("Médiane par archétype :\n", c.merge(sig, on="card_name").groupby("archetype_y").chg.median().round(3).to_string())
