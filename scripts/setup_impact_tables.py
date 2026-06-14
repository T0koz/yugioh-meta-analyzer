"""
Génère les tables card_impact et ban_impact dans yugioh.db.
Run: python scripts/setup_impact_tables.py
"""

import sqlite3
import os
import sys
import pandas as pd
import numpy as np

DB = os.path.join(os.path.dirname(__file__), "..", "data", "yugioh.db")
conn = sqlite3.connect(DB)

ms = pd.read_sql_query(
    "SELECT month, archetype, meta_score FROM meta_scores",
    conn, parse_dates=["month"]
)
ms["month"] = ms["month"].dt.to_period("M")
print(f"meta_scores chargé : {len(ms)} lignes")


def card_monthly_usage(card_name):
    q = """SELECT strftime('%Y-%m', td.created) as month, td.archetype, COUNT(*) as deck_count
           FROM deck_cards dc JOIN tournament_decks td ON td.id = dc.deck_id
           WHERE dc.card_name = ? AND td.ocg = 0
           GROUP BY month, td.archetype ORDER BY month, deck_count DESC"""
    df = pd.read_sql_query(q, conn, params=(card_name,))
    df["month"] = pd.to_datetime(df["month"]).dt.to_period("M")
    return df


def card_total_monthly(card_name):
    return card_monthly_usage(card_name).groupby("month")["deck_count"].sum().sort_index()


def delta_meta_score(archetypes, date_event, window_months=3):
    rows = []
    for arch in archetypes:
        pre  = ms[(ms["archetype"] == arch) & (ms["month"] < date_event) & (ms["month"] >= date_event - window_months)]
        post = ms[(ms["archetype"] == arch) & (ms["month"] >= date_event) & (ms["month"] < date_event + window_months)]
        pre_s  = pre["meta_score"].mean()  if len(pre)  else float("nan")
        post_s = post["meta_score"].mean() if len(post) else float("nan")
        delta  = post_s - pre_s if (pre_s == pre_s and post_s == post_s) else float("nan")
        rows.append({"archetype": arch, "pre_score": pre_s, "post_score": post_s, "delta": delta})
    df = pd.DataFrame(rows)
    return df[df["delta"].notna()].sort_values("delta", ascending=False) if not df.empty else df


def infer_ban_date(card_name, min_peak_decks=10):
    usage = card_total_monthly(card_name)
    if len(usage) < 3:
        return None
    post_peak = usage[usage.index >= usage.idxmax()]
    if post_peak.max() < min_peak_decks:
        return None
    mom = post_peak.pct_change()
    worst = mom.idxmin()
    return worst if mom[worst] < -0.4 else None


# ── ban_impact ─────────────────────────────────────────────────────────────────
print("\nConstruction de ban_impact...")
q = """SELECT c.name, c.ban_tcg, c.tcg_date, COUNT(dc.id) as n
       FROM cards c JOIN deck_cards dc ON dc.card_name = c.name
       WHERE c.ban_tcg IN ('Forbidden', 'Limited') AND c.tcg_date >= '2022-01-01'
       GROUP BY c.name HAVING n >= 50 ORDER BY n DESC"""
restricted = pd.read_sql_query(q, conn)

scan_rows = []
for i, (_, row) in enumerate(restricted.iterrows()):
    print(f"  {i+1}/{len(restricted)} {row['name']}", end="\r")
    total = card_total_monthly(row["name"])
    if len(total) < 3:
        continue
    db = infer_ban_date(row["name"])
    if db is None:
        continue
    usage = card_monthly_usage(row["name"])
    pre = usage[(usage["month"] < db) & (usage["month"] >= db - 3)]
    archs = pre.groupby("archetype")["deck_count"].sum()
    top_a = archs.idxmax() if len(archs) else "Unknown"
    d = delta_meta_score([top_a], db)
    dv = float(d.iloc[0]["delta"]) if len(d) else float("nan")
    scan_rows.append({
        "card": row["name"], "ban_status": row["ban_tcg"],
        "ban_month_inferred": str(db), "peak_usage": int(total.max()),
        "drop_ratio": round(float(total.pct_change().min()), 3),
        "top_archetype": top_a,
        "delta_meta_score": round(dv, 4) if dv == dv else None,
        "n_archetypes_affected": len(archs),
        "total_appearances": int(row["n"])
    })

ban_df = pd.DataFrame(scan_rows)
ban_df.to_sql("ban_impact", conn, if_exists="replace", index=False)
print(f"\n✓ ban_impact : {len(ban_df)} lignes")

# ── card_impact ────────────────────────────────────────────────────────────────
print("\nConstruction de card_impact...")
q2 = """SELECT c.name, c.ban_tcg, c.tcg_date, COUNT(dc.id) as n
        FROM cards c JOIN deck_cards dc ON dc.card_name = c.name
        WHERE c.tcg_date >= '2023-06-01'
        GROUP BY c.name HAVING n >= 100 ORDER BY n DESC LIMIT 35"""
new_cards = pd.read_sql_query(q2, conn)

imp_rows = []
for i, (_, row) in enumerate(new_cards.iterrows()):
    print(f"  {i+1}/{len(new_cards)} {row['name']}", end="\r")
    card  = row["name"]
    rel_m = pd.Period(pd.to_datetime(row["tcg_date"]), freq="M")
    usage = card_monthly_usage(card)
    p90   = usage[(usage["month"] >= rel_m) & (usage["month"] < rel_m + 3)]
    n_a   = p90["archetype"].nunique()
    tot   = p90["deck_count"].sum()
    bs    = round(n_a * np.log1p(tot), 3) if tot > 0 else 0
    top_a = p90.groupby("archetype")["deck_count"].sum().idxmax() if tot > 0 else None
    d     = delta_meta_score([top_a], rel_m) if top_a else pd.DataFrame()
    dv    = float(d.iloc[0]["delta"]) if len(d) else None
    imp_rows.append({
        "card_name": card, "release_month": str(rel_m),
        "n_archetypes_3m": n_a, "total_decks_3m": int(tot),
        "bridge_score": bs, "top_archetype": top_a,
        "delta_meta_score_top_arch": round(dv, 4) if dv is not None else None
    })

card_df = pd.DataFrame(imp_rows).sort_values("bridge_score", ascending=False)
card_df.to_sql("card_impact", conn, if_exists="replace", index=False)
print(f"\n✓ card_impact : {len(card_df)} lignes")

conn.commit()
conn.close()
print("\n✅ Tables ban_impact et card_impact créées dans data/yugioh.db")
print("   Relance streamlit run app.py")
