"""
TOK-77 — Part du format Genesys dans les decklists et effet sur le méta (lecture seule).

    python scripts/analyze_genesys.py

Genesys = `tournament_type = 'Genesys Format'` (légalité par points) ; `deck_legality.legal` y vaut NULL.
Mesure, par mois et par région :
  - la part des decks Genesys dans toutes les decks ; dans les decks jugés légaux par l'API (illegal=0),
    c'est-à-dire ce que l'ancien pipeline consommait ;
  - l'effet sur le classement d'archétypes : méta calculé AVEC puis SANS Genesys (même formule que
    le notebook 04 : sqrt(share × placement_score_norm), mois = date d'upload) ; corrélation de rang
    de Spearman et archétypes dont la part se déplace le plus.
Le pipeline actuel (legal = 1) EXCLUT déjà Genesys : ce script mesure ce qu'on évite et ce que
l'ancien filtre `illegal = 0` laissait entrer.
"""
import sqlite3
import numpy as np, pandas as pd

con = sqlite3.connect("file:data/yugioh.db?mode=ro", uri=True)
d = pd.read_sql("""select td.id, td.archetype, td.placement, td.uploaded, td.created, td.ocg, td.illegal,
                          td.tournament_type = 'Genesys Format' as gen, dl.legal
                   from tournament_decks td join deck_legality dl on dl.deck_id = td.id""", con)
d["m"] = d.created.str[:7]
d["reg"] = np.where(d.ocg == 1, "OCG", "TCG")
print("Genesys par région :", d.groupby("reg").gen.agg(["sum", "count"]).assign(pct=lambda x: (x["sum"] / x["count"] * 100).round(1)).to_string(), sep="\n")
t = d[d.m >= "2025-10"].groupby(["reg", "m"]).agg(decks=("id", "size"), genesys=("gen", "sum"))
t["% de tous les decks"] = (t.genesys / t.decks * 100).round(1)
api = d[d.illegal == 0].groupby(["reg", "m"]).agg(api_legaux=("id", "size"), genesys_dans_api_legaux=("gen", "sum"))
api["% des decks « légaux » API"] = (api.genesys_dans_api_legaux / api.api_legaux * 100).round(1)
print("\nPar mois depuis 2025-10 :\n", t.join(api).to_string())


def meta(x, key="m"):
    x = x.dropna(subset=["archetype", "placement"])
    g = x.groupby([key, "archetype"]).agg(n=("id", "size"), pl=("placement", "mean")).reset_index()
    g["share"] = g.n / g.groupby(key).n.transform("sum")
    g["pn"] = (1 / g.pl) / (1 / g.pl).groupby(g[key]).transform("max")
    g["score"] = np.sqrt(g.share * g.pn)
    return g


print("\nEffet sur le méta TCG (decks de tournoi, mois de création, sans filtre de légalité)")
x = d[d.reg == "TCG"]
rows = []
for m in sorted(x[x.gen == 1].m.unique()):
    sub = x[x.m == m]
    w, wo = meta(sub[sub.m == m]), meta(sub[sub.gen == 0])
    j = w.merge(wo, on=["m", "archetype"], how="outer", suffixes=("_avec", "_sans")).fillna(0)
    rho = j.score_avec.rank().corr(j.score_sans.rank())
    j["d"] = j.share_avec - j.share_sans
    top = j.sort_values("d", ascending=False).iloc[0]
    top5_a = set(w.nlargest(5, "score").archetype); top5_s = set(wo.nlargest(5, "score").archetype)
    rows.append((m, int(sub.gen.sum()), len(sub), round(rho, 3), len(top5_a & top5_s), top.archetype, round(top.d * 100, 1)))
print(pd.DataFrame(rows, columns=["mois", "decks Genesys", "decks", "Spearman rang avec/sans", "top5 commun /5", "archétype le plus gonflé", "gain de part (pts)"]).to_string(index=False))
