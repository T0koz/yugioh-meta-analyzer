"""
Reconstruit `boutique_buy_signals` (TOK-69) à partir de `boutique_alerts`,
`boutique_card_alerts` et du dernier prix de `card_price_history`.

Comme `banlist_features`, cette table n'avait plus de producteur dans le dépôt (elle date
du 2026-06-17, générée hors notebook). Formule rétro-ingéniérée sur les 137 lignes
historiques, puis reproduite à l'identique pour la continuité :
  alert_norm   = alert_score(archétype) / max(alert_score) × 100
  price_opp    = 1 − rang_percentile(cm_price)           (carte pas chère → proche de 1)
  buy_score    = 0,7·alert_norm + 0,3·(100·price_opp)    (v2, TOK-81 : prix remis sur 0-100)
  buy_score_100= buy_score / max(buy_score) × 100
  label        = Fort ≥ 80 ; Modéré ≥ 50 ; sinon Faible

Correction TOK-81 (2026-11-16) : jusqu'à la v1, `price_opp` (0-1) était ajouté tel quel à `alert_norm`
(0-100) : le prix pesait au plus 0,3 point sur 100, le « buy score » n'était que l'alerte OCG de
l'archétype. On garde les poids 70/30 réellement appliqués par la v1 mais le prix est remis sur
0-100 (PRICE_SCALE). Conséquence : à archétype égal, une carte bon marché passe devant une carte
chère. Non validé sur ventes : même caveat que TOK-74.

Signal v3 (2026-11-16) : `boutique_alerts` ne contient plus que les archétypes forts en OCG et pas
encore sortis en TCG (notebook 10). La fausse date `tcg_entry_estimated` (date du jour + 4 mois,
identique partout) est remplacée par la fenêtre `tcg_window_start` / `tcg_window_end` de l'archétype
(intervalle à 80 %). `ban_tcg` vient de la banlist TCG en vigueur (`banlist_history`) et non de
`cards.ban_tcg`, figé au dernier `fetch_cards.py` (4 cartes interdites étaient encore proposées).
Seules les cartes déjà cotées sur Cardmarket ressortent : on surveille les cartes disponibles que le
futur deck jouera, pas les cartes inédites.
⚠ `alert_norm` et `buy_score_100` sont relatifs au maximum du lot : il y a toujours une carte à 100,
même quand le signal est faible dans l'absolu. Les libellés Fort / Modéré / Faible classent les
cartes entre elles, ils ne mesurent pas une force de signal.

    python scripts/build_buy_signals.py [--dry-run]
"""
import argparse
import sqlite3
from datetime import date
from pathlib import Path

import pandas as pd

PRICE_SCALE = 100  # v1 : 1 (défaut d'échelle) ; v2 : price_opp remis sur 0-100
DB = Path(__file__).resolve().parents[1] / "data" / "yugioh.db"


def build(con) -> pd.DataFrame:
    alerts = pd.read_sql("SELECT archetype, alert_score, tcg_window_start, tcg_window_end FROM boutique_alerts", con)
    cards = pd.read_sql("SELECT archetype, card_name, card_alert_score FROM boutique_card_alerts", con)
    # ban_tcg : statut dans la banlist TCG en vigueur (NULL = non limitée).
    ban = pd.read_sql(
        "SELECT card_name, status AS ban_tcg FROM banlist_history WHERE format = 'TCG' "
        "AND effective_date = (SELECT MAX(effective_date) FROM banlist_history WHERE format = 'TCG')", con)
    cards = cards.merge(ban.drop_duplicates("card_name"), on="card_name", how="left")
    cards = cards[cards.ban_tcg != "Forbidden"]   # signal d'achat : on exclut les cartes bannies en TCG
    last = pd.read_sql("SELECT MAX(snapshot_date) d FROM card_price_history", con).d[0]
    px = pd.read_sql("SELECT card_name, cardmarket_price AS cm_price, tcgplayer_price AS tcp_price FROM card_price_history WHERE snapshot_date=?",
                     con, params=(last,))
    d = cards.merge(alerts, on="archetype").merge(px, on="card_name")
    d = d[d.cm_price.notna() & (d.cm_price > 0)].copy()
    if d.empty:   # aucun archétype retenu, ou aucune carte cotée : table vide, mêmes colonnes
        return pd.DataFrame(columns=COLS)
    d["archetype_alert"] = d.alert_score
    d["alert_norm"] = (d.alert_score / alerts.alert_score.max() * 100).round(2)
    d["price_opp"] = 1 - d.cm_price.rank(method="min") / len(d)
    d["buy_score"] = (0.7 * d.alert_norm + 0.3 * PRICE_SCALE * d.price_opp).round(2)
    d["buy_score_100"] = (d.buy_score / d.buy_score.max() * 100).round(1)
    d["buy_label"] = pd.cut(d.buy_score_100, [-1, 49.999, 79.999, 1000], labels=["Faible", "Modéré", "Fort"]).astype(str)
    d["computed_at"] = date.today().isoformat()
    return d[COLS].sort_values("buy_score_100", ascending=False).reset_index(drop=True)


COLS = ["archetype", "card_name", "archetype_alert", "card_alert_score", "cm_price", "tcp_price", "alert_norm",
        "price_opp", "buy_score", "buy_score_100", "buy_label", "tcg_window_start", "tcg_window_end", "computed_at", "ban_tcg"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    con = sqlite3.connect(DB, timeout=60)
    d = build(con)
    print(f"[buy_signals] {len(d)} lignes, {d.archetype.nunique()} archétypes, labels: {d.buy_label.value_counts().to_dict()}")
    if not a.dry_run:
        d.to_sql("boutique_buy_signals", con, if_exists="replace", index=False)
        print("[buy_signals] écrite.")
    con.close()


if __name__ == "__main__":
    main()
