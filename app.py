"""
Yu-Gi-Oh! Meta Analyzer — Dashboard Streamlit v2
Run: streamlit run app.py
"""

import sqlite3, os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="YGO Meta Analyzer",
    page_icon="🃏",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "yugioh.db")

def db():
    return sqlite3.connect(DB_PATH)

# ─── Loaders ──────────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def load_meta_scores():
    df = pd.read_sql_query(
        "SELECT month, archetype, meta_score, share, avg_placement, deck_count FROM meta_scores",
        db(), parse_dates=["month"]
    )
    df["month"] = df["month"].dt.to_period("M")
    return df

@st.cache_data(ttl=300)
def load_tier_list():
    try:
        return pd.read_sql_query(
            "SELECT archetype, tier, deck_count, share_pct FROM meta_tier_list WHERE format='TCG'",
            db()
        )
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_predictions():
    try:
        return pd.read_sql_query(
            "SELECT archetype, data_month, meta_score_current, pred_delta, pred_meta_score, pred_direction "
            "FROM meta_predictions ORDER BY pred_meta_score DESC",
            db()
        )
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_early_signals():
    try:
        return pd.read_sql_query(
            "SELECT card_name, archetype, views_week, signal_views, signal_text, signal_ocg, "
            "early_score_100, best_meta_match FROM early_card_signals ORDER BY early_score_100 DESC",
            db()
        )
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_combos():
    try:
        return pd.read_sql_query(
            "SELECT archetype, card_a, card_b, weight FROM combo_edges_global ORDER BY weight DESC",
            db()
        )
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_banlist_history():
    try:
        return pd.read_sql_query(
            "SELECT list_name, effective_date, end_date, card_name, status FROM banlist_history",
            db(), parse_dates=["effective_date", "end_date"]
        )
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_ban_impact():
    try:
        return pd.read_sql_query("SELECT * FROM ban_impact ORDER BY peak_usage DESC", db())
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_card_impact():
    try:
        return pd.read_sql_query("SELECT * FROM card_impact ORDER BY bridge_score DESC", db())
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_trend():
    try:
        return pd.read_sql_query(
            "SELECT archetype, trend_ratio, trend_label FROM archetype_trend ORDER BY trend_ratio DESC",
            db()
        )
    except Exception:
        return pd.DataFrame(columns=["archetype", "trend_ratio", "trend_label"])

# ─── Sidebar ──────────────────────────────────────────────────────────────────

st.sidebar.title("🃏 YGO Meta Analyzer")
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigation", [
    "📊 Tier List",
    "📈 Évolution",
    "🔮 Prédictions",
    "🚨 Signal précoce",
    "🎮 Combos NLP",
    "📜 Banlist historique",
    "🕸️ Graphe synergies",
    "🚫 Simulateur ban",
])

ms_df    = load_meta_scores()
tier_ytm = load_tier_list()
trend_df = load_trend()

all_months = sorted(ms_df["month"].unique(), reverse=True)
month_str  = [str(m) for m in all_months]

TIER_COLOR = {"T1": "#e74c3c", "T2": "#e67e22", "T3": "#f1c40f", "field": "#95a5a6"}

def assign_tier_local(score):
    if score >= 0.25: return "S"
    if score >= 0.18: return "A"
    if score >= 0.12: return "B"
    if score >= 0.07: return "C"
    return "D"

# ─── Page : Tier List ─────────────────────────────────────────────────────────
if page == "📊 Tier List":
    st.title("📊 Tier List — Meta Score")

    col1, col2 = st.columns([2, 1])
    with col1:
        selected_month_str = st.selectbox("Mois", month_str, index=0)
    with col2:
        min_score = st.slider("Score minimum", 0.0, 0.5, 0.0, 0.01)

    selected_month = pd.Period(selected_month_str, freq="M")
    tier = ms_df[ms_df["month"] == selected_month].copy()
    tier = tier[tier["meta_score"] >= min_score].sort_values("meta_score", ascending=False)

    if not trend_df.empty:
        tier = tier.merge(trend_df[["archetype", "trend_label"]], on="archetype", how="left")
        tier["trend_label"] = tier["trend_label"].fillna("➡️ stable")
    else:
        tier["trend_label"] = "➡️ stable"

    # Badge yugiohmeta.com tier
    if not tier_ytm.empty:
        tier = tier.merge(tier_ytm[["archetype", "tier", "share_pct"]], on="archetype", how="left")
        tier["tier"] = tier["tier"].fillna("—")
    else:
        tier["tier"] = "—"

    tier["Tier"] = tier["meta_score"].apply(assign_tier_local)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Archetypes actifs", len(tier))
    top = tier.iloc[0] if len(tier) else None
    k2.metric("Top meta", top["archetype"] if top is not None else "—",
              f"{top['meta_score']:.3f}" if top is not None else "")
    ytm_t1 = tier[tier["tier"] == "T1"]["archetype"].tolist()
    k3.metric("T1 yugiohmeta", ytm_t1[0] if ytm_t1 else "—")
    rising = tier[tier["trend_label"].isin(["⬆️ émergence", "↗️ montée"])] if "trend_label" in tier.columns else pd.DataFrame()
    k4.metric("En hausse", len(rising))

    st.markdown("---")

    fig = px.bar(
        tier, x="meta_score", y="archetype", orientation="h",
        color="Tier",
        color_discrete_map={"S": "#e74c3c", "A": "#e67e22", "B": "#f1c40f", "C": "#2ecc71", "D": "#95a5a6"},
        text="meta_score",
        hover_data={"share": ":.1%", "avg_placement": ":.1f", "tier": True},
        labels={"meta_score": "Meta Score", "archetype": "Archetype"},
        title=f"Tier List — {selected_month_str}",
        height=max(400, len(tier) * 28),
    )
    fig.update_traces(texttemplate="%{text:.3f}", textposition="outside")
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

    cols = ["Tier", "archetype", "meta_score", "share", "avg_placement", "deck_count", "tier"]
    if "trend_label" in tier.columns:
        cols.append("trend_label")
    display = tier[cols].copy()
    rename = {"Tier": "Tier local", "archetype": "Archetype", "meta_score": "Meta Score",
               "share": "Share", "avg_placement": "Avg Place", "deck_count": "Decks",
               "tier": "YGOMeta tier", "trend_label": "Trend"}
    display.rename(columns=rename, inplace=True)
    display["Meta Score"] = display["Meta Score"].round(4)
    display["Share"] = (display["Share"] * 100).round(1).astype(str) + "%"
    display["Avg Place"] = display["Avg Place"].round(1)
    st.dataframe(display, use_container_width=True, hide_index=True)


# ─── Page : Évolution ─────────────────────────────────────────────────────────
elif page == "📈 Évolution":
    st.title("📈 Évolution du Meta Score")

    all_archetypes = sorted(ms_df["archetype"].unique())
    defaults = ["Kewl Tune", "Branded", "DoomZ", "Elfnote", "Dracotail"]
    defaults = [a for a in defaults if a in all_archetypes] or all_archetypes[:5]

    selected = st.multiselect("Archetypes", all_archetypes, default=defaults)

    if selected:
        sub = ms_df[ms_df["archetype"].isin(selected)].copy()
        sub["month_str"] = sub["month"].astype(str)

        fig = px.line(sub, x="month_str", y="meta_score", color="archetype", markers=True,
                      labels={"month_str": "Mois", "meta_score": "Meta Score"},
                      title="Meta Score dans le temps", height=500)
        fig.update_layout(xaxis_tickangle=-45, hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

        fig2 = px.area(sub, x="month_str", y="share", color="archetype",
                       labels={"month_str": "Mois", "share": "Share tournois"},
                       title="Share des tournois dans le temps", height=400)
        fig2.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Sélectionne au moins un archetype.")


# ─── Page : Prédictions ───────────────────────────────────────────────────────
elif page == "🔮 Prédictions":
    st.title("🔮 Prédictions — Mois prochain")
    st.markdown(
        "Modèle : **Ensemble 70% naïf + 30% Ridge** (walk-forward CV, fenêtre 9 mois).  \n"
        "Métrique validée : **Spearman ρ = +0.317** (vs +0.253 naïf) sur 15 mois de CV.  \n"
        "Features : lags T-1/T-2/T-3, momentum, ban_severity temporelle (19 features)."
    )

    pred_df = load_predictions()

    if pred_df.empty:
        st.error("Table `meta_predictions` absente. Lance le notebook 05.")
    else:
        data_month = pred_df["data_month"].iloc[0] if len(pred_df) else "?"
        st.info(f"Basé sur les données de **{data_month}** — prédiction pour le mois suivant.")

        c1, c2, c3 = st.columns(3)
        c1.metric("Archetypes prédits", len(pred_df))
        c2.metric("En hausse ↑", (pred_df["pred_direction"] == "↑").sum())
        c3.metric("En baisse ↓", (pred_df["pred_direction"] == "↓").sum())

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("⬆️ En hausse prédite")
            rising = pred_df[pred_df["pred_direction"] == "↑"].head(10)
            fig_r = px.bar(
                rising, x="pred_delta", y="archetype", orientation="h",
                color="pred_delta", color_continuous_scale="Greens",
                hover_data={"meta_score_current": ":.4f", "pred_meta_score": ":.4f"},
                labels={"pred_delta": "Δprédit", "archetype": "Archetype"},
                height=400,
            )
            fig_r.update_layout(coloraxis_showscale=False, yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig_r, use_container_width=True)

        with col2:
            st.subheader("⬇️ En baisse prédite")
            falling = pred_df[pred_df["pred_direction"] == "↓"].sort_values("pred_delta").head(10)
            fig_f = px.bar(
                falling, x="pred_delta", y="archetype", orientation="h",
                color="pred_delta", color_continuous_scale="Reds_r",
                hover_data={"meta_score_current": ":.4f", "pred_meta_score": ":.4f"},
                labels={"pred_delta": "Δprédit", "archetype": "Archetype"},
                height=400,
            )
            fig_f.update_layout(coloraxis_showscale=False, yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig_f, use_container_width=True)

        st.subheader("Toutes les prédictions")
        disp = pred_df[["archetype", "meta_score_current", "pred_delta", "pred_meta_score", "pred_direction"]].copy()
        disp.columns = ["Archetype", "Score actuel", "Δprédit", "Score prédit", "Direction"]
        for c in ["Score actuel", "Δprédit", "Score prédit"]:
            disp[c] = disp[c].round(4)
        st.dataframe(disp, use_container_width=True, hide_index=True)


# ─── Page : Signal précoce ────────────────────────────────────────────────────
elif page == "🚨 Signal précoce":
    st.title("🚨 Signal précoce — Nouvelles cartes")
    st.markdown(
        "Détecte les cartes qui vont exploser **avant** les decklists de tournoi.  \n"
        "Score composite : **35% views_week** + **35% text synergy meta** + **30% OCG alert score**."
    )

    sig_df = load_early_signals()

    if sig_df.empty:
        st.error("Table `early_card_signals` absente. Lance le notebook 11.")
    else:
        top_n = st.slider("Top N cartes", 5, 30, 15)
        sig_df_top = sig_df.head(top_n)

        fig = px.bar(
            sig_df_top, x="early_score_100", y="card_name", orientation="h",
            color="signal_ocg",
            color_continuous_scale="Reds",
            text="early_score_100",
            hover_data={"archetype": True, "views_week": True, "signal_text": ":.2f",
                        "best_meta_match": True},
            labels={"early_score_100": "Score /100", "card_name": "Carte", "signal_ocg": "Signal OCG"},
            title=f"Top {top_n} cartes — Score d'alerte précoce",
            height=max(400, top_n * 32),
        )
        fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

        # Scatter views vs text synergy
        st.subheader("Views vs Synérgie textuelle")
        fig2 = px.scatter(
            sig_df.head(50), x="signal_views", y="signal_text",
            size="early_score_100", color="signal_ocg",
            color_continuous_scale="Reds",
            text="card_name",
            hover_data={"archetype": True, "views_week": True, "early_score_100": True},
            labels={"signal_views": "Signal views", "signal_text": "Signal texte", "signal_ocg": "OCG"},
            height=500,
        )
        fig2.update_traces(textposition="top center")
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Tableau complet")
        disp = sig_df_top[["card_name", "archetype", "views_week", "signal_views",
                             "signal_text", "signal_ocg", "early_score_100", "best_meta_match"]].copy()
        disp.columns = ["Carte", "Archetype", "Views/sem", "Sig. Views",
                        "Sig. Texte", "Sig. OCG", "Score /100", "Meilleur match méta"]
        for c in ["Sig. Views", "Sig. Texte", "Sig. OCG"]:
            disp[c] = disp[c].round(3)
        st.dataframe(disp, use_container_width=True, hide_index=True)


# ─── Page : Combos NLP ────────────────────────────────────────────────────────
elif page == "🎮 Combos NLP":
    st.title("🎮 Combos NLP — Extraits YouTube")
    st.markdown(
        "Combos extraits automatiquement depuis les transcripts YouTube (ASR + regex).  \n"
        "Chaque arête = co-mention dans un guide combo. Poids = fréquence normalisée."
    )

    combo_df = load_combos()

    if combo_df.empty:
        st.error("Table `combo_edges_global` absente. Lance le notebook 08.")
    else:
        archetypes_combo = sorted(combo_df["archetype"].dropna().unique())
        selected_arch = st.selectbox("Archetype", archetypes_combo,
                                     index=archetypes_combo.index("Kewl Tune") if "Kewl Tune" in archetypes_combo else 0)

        sub = combo_df[combo_df["archetype"] == selected_arch].sort_values("weight", ascending=False)

        col1, col2 = st.columns([2, 1])

        with col1:
            top_n = st.slider("Top N combos", 5, 50, 20)
            sub_top = sub.head(top_n)

            fig = px.bar(
                sub_top,
                x="weight",
                y=sub_top["card_a"] + " → " + sub_top["card_b"],
                orientation="h",
                color="weight",
                color_continuous_scale="Viridis",
                labels={"weight": "Poids", "y": "Combo"},
                title=f"Top {top_n} combos — {selected_arch}",
                height=max(400, top_n * 28),
            )
            fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Stats")
            st.metric("Combos uniques", len(sub))
            st.metric("Cartes impliquées",
                      pd.concat([sub["card_a"], sub["card_b"]]).nunique())
            st.metric("Combo le plus fréquent", f"{sub.iloc[0]['card_a']} → {sub.iloc[0]['card_b']}" if len(sub) else "—")

            st.subheader("Tableau")
            disp = sub_top[["card_a", "card_b", "weight"]].copy()
            disp.columns = ["Carte A", "Carte B", "Poids"]
            disp["Poids"] = disp["Poids"].round(4)
            st.dataframe(disp, use_container_width=True, hide_index=True)


# ─── Page : Banlist historique ────────────────────────────────────────────────
elif page == "📜 Banlist historique":
    st.title("📜 Banlist historique TCG (2002 → 2026)")
    st.markdown("Historique complet des 81 banlists TCG Advanced Format scrapées depuis Yugipedia.")

    bl_df = load_banlist_history()

    if bl_df.empty:
        st.error("Table `banlist_history` absente. Lance le notebook 09.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            # Recherche par carte
            st.subheader("🔍 Historique d'une carte")
            all_cards = sorted(bl_df["card_name"].unique())
            selected_card = st.selectbox("Carte", all_cards,
                                         index=all_cards.index("Maxx \"C\"") if "Maxx \"C\"" in all_cards else 0)

            card_hist = bl_df[bl_df["card_name"] == selected_card].sort_values("effective_date")
            if not card_hist.empty:
                status_colors = {"Forbidden": "#e74c3c", "Limited": "#e67e22", "Semi-Limited": "#f1c40f"}
                fig = px.scatter(
                    card_hist, x="effective_date", y="status",
                    color="status",
                    color_discrete_map=status_colors,
                    size=[10] * len(card_hist),
                    hover_data={"list_name": True, "end_date": True},
                    title=f"Historique banlist — {selected_card}",
                    height=300,
                )
                fig.update_layout(yaxis_title="Statut", xaxis_title="Date")
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(
                    card_hist[["effective_date", "end_date", "status", "list_name"]].rename(
                        columns={"effective_date": "Début", "end_date": "Fin",
                                 "status": "Statut", "list_name": "Banlist"}
                    ),
                    use_container_width=True, hide_index=True
                )

        with col2:
            # Cartes les plus souvent bannies
            st.subheader("🏆 Cartes les + longtemps Forbidden")
            forever = (bl_df[bl_df["status"] == "Forbidden"]
                       .groupby("card_name").size()
                       .reset_index(name="n_banlists")
                       .sort_values("n_banlists", ascending=False)
                       .head(15))
            fig2 = px.bar(
                forever, x="n_banlists", y="card_name", orientation="h",
                color="n_banlists", color_continuous_scale="Reds",
                labels={"n_banlists": "Nb banlists Forbidden", "card_name": "Carte"},
                title="Top 15 cartes Forbidden (historique)",
                height=450,
            )
            fig2.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
            st.plotly_chart(fig2, use_container_width=True)

        st.subheader("📅 Dernière banlist (May 2026)")
        latest_date = bl_df["effective_date"].max()
        latest = bl_df[bl_df["effective_date"] == latest_date].sort_values("status")
        st.info(f"Banlist active depuis **{latest_date.date()}** — {len(latest)} cartes restreintes")

        c1, c2, c3 = st.columns(3)
        for col, status in zip([c1, c2, c3], ["Forbidden", "Limited", "Semi-Limited"]):
            sub = latest[latest["status"] == status]["card_name"].tolist()
            col.markdown(f"**{status}** ({len(sub)})")
            col.markdown("\n".join(f"- {c}" for c in sub[:20]))
            if len(sub) > 20:
                col.caption(f"... et {len(sub)-20} autres")


# ─── Page : Graphe synergies ──────────────────────────────────────────────────
elif page == "🕸️ Graphe synergies":
    st.title("🕸️ Graphe de co-occurrence")
    st.markdown("Cartes qui apparaissent ensemble dans les decks gagnants. Arête = Jaccard pondéré.")

    graph_dir = os.path.join(os.path.dirname(__file__), "data")
    graph_files = {
        os.path.splitext(f)[0].replace("graph_", "").replace("_", " ").title(): os.path.join(graph_dir, f)
        for f in sorted(os.listdir(graph_dir)) if f.startswith("graph_") and f.endswith(".html")
    }

    if graph_files:
        selected_graph = st.selectbox("Archetype", list(graph_files.keys()))
        with open(graph_files[selected_graph], "r", encoding="utf-8") as fh:
            html_content = fh.read()
        st.components.v1.html(html_content, height=700, scrolling=False)
    else:
        st.warning("Aucun graphe HTML trouvé dans data/. Lance le notebook 03.")


# ─── Page : Simulateur ban ────────────────────────────────────────────────────
elif page == "🚫 Simulateur ban":
    st.title("🚫 Simulateur de ban")
    st.markdown("Estime l'impact d'un ban sur le `meta_score` des archetypes affectés.")

    ban_df = load_ban_impact()

    if ban_df.empty:
        st.error("Table `ban_impact` absente. Lance le notebook 06.")
    else:
        cards_w = ban_df.dropna(subset=["delta_meta_score"]).sort_values("peak_usage", ascending=False)
        selected_card = st.selectbox("Carte", cards_w["card"].tolist())
        row = cards_w[cards_w["card"] == selected_card].iloc[0]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Statut", row["ban_status"])
        c2.metric("Mois de ban", row["ban_month_inferred"])
        c3.metric("Peak usage", int(row["peak_usage"]))
        delta = row["delta_meta_score"]
        c4.metric("Δmeta_score", f"{delta:+.4f}", delta_color="normal" if delta >= 0 else "inverse")

        st.markdown(f"**Archetype principal :** {row['top_archetype']}  \n"
                    + ("Déclin post-ban ⬇️" if delta < 0 else "Résistance ou bénéfice ↗️"))

        st.markdown("---")
        st.subheader("Top bans les plus impactants")
        worst = ban_df.dropna(subset=["delta_meta_score"]).sort_values("delta_meta_score").head(10)
        fig = px.bar(
            worst, x="delta_meta_score", y="card", orientation="h",
            color="delta_meta_score",
            color_continuous_scale=["#e74c3c", "#e67e22", "#f1c40f"],
            labels={"delta_meta_score": "Δmeta_score", "card": "Carte"},
            title="Impact des bans (Δmeta_score le plus négatif)",
            height=400,
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
