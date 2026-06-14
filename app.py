"""
Yu-Gi-Oh! Meta Analyzer — Dashboard Streamlit
Run: streamlit run app.py
"""

import sqlite3
import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ─── Config ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="YGO Meta Analyzer",
    page_icon="🃏",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "yugioh.db")

TREND_COLORS = {
    "⬆️ émergence": "#2ecc71",
    "↗️ montée":     "#27ae60",
    "➡️ stable":     "#95a5a6",
    "↘️ déclin":     "#e67e22",
    "⬇️ chute forte": "#e74c3c",
}

# ─── Data loading ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_meta_scores():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT month, archetype, meta_score, share, avg_placement, deck_count FROM meta_scores",
        conn, parse_dates=["month"]
    )
    conn.close()
    df["month"] = df["month"].dt.to_period("M")
    return df

@st.cache_data(ttl=300)
def load_trend():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT archetype, trend_ratio, trend_label FROM archetype_trend ORDER BY trend_ratio DESC",
        conn
    )
    conn.close()
    return df

@st.cache_data(ttl=300)
def load_ban_impact():
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query("SELECT * FROM ban_impact ORDER BY peak_usage DESC", conn)
    except Exception:
        df = pd.DataFrame()
    conn.close()
    return df

@st.cache_data(ttl=300)
def load_card_impact():
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query("SELECT * FROM card_impact ORDER BY bridge_score DESC", conn)
    except Exception:
        df = pd.DataFrame()
    conn.close()
    return df

@st.cache_data(ttl=300)
def load_predictions():
    """Prédictions next-month via Random Forest (notebook 05)."""
    conn = sqlite3.connect(DB_PATH)
    ms = pd.read_sql_query(
        "SELECT month, archetype, meta_score, share, avg_placement FROM meta_scores",
        conn, parse_dates=["month"]
    )
    conn.close()
    ms["month"] = ms["month"].dt.to_period("M")

    try:
        from sklearn.ensemble import RandomForestRegressor

        # Features T → T+1 (simplifié sans features externes)
        ms_sorted = ms.sort_values(["archetype", "month"])
        ms_sorted["next_score"] = ms_sorted.groupby("archetype")["meta_score"].shift(-1)
        dataset = ms_sorted.dropna(subset=["next_score"])

        features = ["meta_score", "share", "avg_placement"]
        X = dataset[features]
        y = dataset["next_score"]

        # Train sur tout sauf dernier mois
        last_month = ms["month"].max()
        train_mask = dataset["month"] < last_month
        X_train, y_train = X[train_mask], y[train_mask]

        if len(X_train) < 10:
            return pd.DataFrame()

        rf = RandomForestRegressor(n_estimators=200, max_depth=5, random_state=42)
        rf.fit(X_train, y_train)

        # Prédiction du mois prochain
        current = ms[ms["month"] == last_month].copy()
        X_pred = current[features]
        current = current.copy()
        current["predicted_next"] = rf.predict(X_pred)
        current["delta_predicted"] = current["predicted_next"] - current["meta_score"]

        return current[["archetype", "meta_score", "predicted_next", "delta_predicted"]].sort_values(
            "delta_predicted", ascending=False
        )
    except ImportError:
        return pd.DataFrame()


# ─── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.image(
    "https://ygoprodeck.com/images/logo.png",
    use_column_width=True,
)
st.sidebar.title("🃏 YGO Meta Analyzer")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["📊 Tier List", "📈 Évolution", "🕸️ Graphe synergies", "🚫 Simulateur ban", "🌉 Cartes bridge", "🔮 Prédictions"],
)

ms_df   = load_meta_scores()
trend_df = load_trend()
ban_df   = load_ban_impact()
card_df  = load_card_impact()

all_months = sorted(ms_df["month"].unique(), reverse=True)
month_str  = [str(m) for m in all_months]

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

    # Ajouter trend
    tier = tier.merge(trend_df[["archetype", "trend_ratio", "trend_label"]], on="archetype", how="left")
    tier["trend_label"] = tier["trend_label"].fillna("➡️ stable")

    # Tier labels
    def assign_tier(score):
        if score >= 0.25: return "S"
        if score >= 0.18: return "A"
        if score >= 0.12: return "B"
        if score >= 0.07: return "C"
        return "D"

    tier["Tier"] = tier["meta_score"].apply(assign_tier)

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Archetypes actifs", len(tier))
    top = tier.iloc[0] if len(tier) else None
    k2.metric("Top meta", top["archetype"] if top is not None else "—",
              f"{top['meta_score']:.3f}" if top is not None else "")
    emerging = tier[tier["trend_label"] == "⬆️ émergence"]
    k3.metric("En émergence", len(emerging))
    declining = tier[tier["trend_label"] == "⬇️ chute forte"]
    k4.metric("En chute", len(declining))

    st.markdown("---")

    # Graphe barres
    fig = px.bar(
        tier,
        x="meta_score", y="archetype",
        orientation="h",
        color="Tier",
        color_discrete_map={"S": "#e74c3c", "A": "#e67e22", "B": "#f1c40f", "C": "#2ecc71", "D": "#95a5a6"},
        text="meta_score",
        hover_data={"share": ":.1%", "avg_placement": ":.1f", "trend_label": True},
        labels={"meta_score": "Meta Score", "archetype": "Archetype"},
        title=f"Tier List — {selected_month_str}",
        height=max(400, len(tier) * 28),
    )
    fig.update_traces(texttemplate="%{text:.3f}", textposition="outside")
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

    # Table détaillée
    st.subheader("Détail")
    display = tier[["Tier", "archetype", "meta_score", "share", "avg_placement", "deck_count", "trend_label", "trend_ratio"]].copy()
    display.columns = ["Tier", "Archetype", "Meta Score", "Share", "Avg Placement", "Decks", "Trend", "Trend Ratio"]
    display["Meta Score"] = display["Meta Score"].round(4)
    display["Share"] = (display["Share"] * 100).round(1).astype(str) + "%"
    display["Avg Placement"] = display["Avg Placement"].round(1)
    display["Trend Ratio"] = display["Trend Ratio"].round(2)
    st.dataframe(display, use_container_width=True, hide_index=True)


# ─── Page : Évolution temporelle ──────────────────────────────────────────────
elif page == "📈 Évolution":
    st.title("📈 Évolution du Meta Score")

    all_archetypes = sorted(ms_df["archetype"].unique())
    default_archetypes = ["Ryzeal", "DoomZ", "Branded", "Dracotail", "Yummy"] if all(
        a in all_archetypes for a in ["Ryzeal", "DoomZ", "Branded"]
    ) else all_archetypes[:5]

    selected_archetypes = st.multiselect(
        "Archetypes à comparer",
        all_archetypes,
        default=default_archetypes,
    )

    if selected_archetypes:
        subset = ms_df[ms_df["archetype"].isin(selected_archetypes)].copy()
        subset["month_str"] = subset["month"].astype(str)

        fig = px.line(
            subset,
            x="month_str", y="meta_score",
            color="archetype",
            markers=True,
            labels={"month_str": "Mois", "meta_score": "Meta Score", "archetype": "Archetype"},
            title="Meta Score dans le temps",
            height=500,
        )
        fig.update_layout(xaxis_tickangle=-45, hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

        # Share dans le temps
        fig2 = px.area(
            subset,
            x="month_str", y="share",
            color="archetype",
            labels={"month_str": "Mois", "share": "Share tournois", "archetype": "Archetype"},
            title="Share des tournois dans le temps",
            height=400,
        )
        fig2.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Sélectionne au moins un archetype.")


# ─── Page : Graphe synergies ──────────────────────────────────────────────────
elif page == "🕸️ Graphe synergies":
    st.title("🕸️ Graphe de co-occurrence")
    st.markdown(
        "Visualise les cartes qui apparaissent ensemble dans les decks gagnants. "
        "Chaque arête = Jaccard pondéré > seuil."
    )

    graph_dir = os.path.join(os.path.dirname(__file__), "data")
    graph_files = {
        os.path.splitext(f)[0].replace("graph_", "").capitalize(): os.path.join(graph_dir, f)
        for f in os.listdir(graph_dir) if f.startswith("graph_") and f.endswith(".html")
    }

    if graph_files:
        selected_graph = st.selectbox("Archetype", list(graph_files.keys()))
        with open(graph_files[selected_graph], "r", encoding="utf-8") as fh:
            html_content = fh.read()
        st.components.v1.html(html_content, height=700, scrolling=False)
    else:
        st.warning("Aucun graphe HTML trouvé dans data/. Lance le notebook 03 pour les générer.")


# ─── Page : Simulateur ban ────────────────────────────────────────────────────
elif page == "🚫 Simulateur ban":
    st.title("🚫 Simulateur de ban")
    st.markdown(
        "Sélectionne une carte bannie/limitée pour voir l'impact estimé "
        "sur le `meta_score` des archetypes affectés."
    )

    if ban_df.empty:
        st.error("Table `ban_impact` absente. Lance le notebook 06.")
    else:
        cards_with_impact = ban_df.dropna(subset=["delta_meta_score"]).sort_values(
            "peak_usage", ascending=False
        )

        col1, col2 = st.columns(2)
        with col1:
            selected_card = st.selectbox(
                "Carte bannie/limitée",
                cards_with_impact["card"].tolist(),
            )

        row = cards_with_impact[cards_with_impact["card"] == selected_card].iloc[0]

        with col2:
            st.metric("Statut", row["ban_status"])

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Mois de ban inféré", row["ban_month_inferred"])
        c2.metric("Peak usage", int(row["peak_usage"]), help="Nb max de decks utilisant la carte en un mois")
        c3.metric("Archetype principal", row["top_archetype"])
        delta = row["delta_meta_score"]
        c4.metric("Δmeta_score", f"{delta:+.4f}", delta_color="normal" if delta >= 0 else "inverse")

        st.markdown("---")
        st.markdown(f"**Interprétation :** Le ban de **{selected_card}** est associé à un Δmeta_score de `{delta:+.4f}` "
                    f"sur l'archetype **{row['top_archetype']}**. "
                    + ("L'archetype a décliné après le ban. ⬇️" if delta < 0 else "L'archetype a résisté ou profité du contexte. ↗️"))

        # Top 10 bans par impact négatif
        st.subheader("Top bans les plus impactants (Δmeta_score le plus négatif)")
        worst = ban_df.dropna(subset=["delta_meta_score"]).sort_values("delta_meta_score").head(10)
        fig = px.bar(
            worst, x="delta_meta_score", y="card", orientation="h",
            color="delta_meta_score",
            color_continuous_scale=["#e74c3c", "#e67e22", "#f1c40f"],
            labels={"delta_meta_score": "Δmeta_score", "card": "Carte"},
            title="Impact des bans sur le meta_score de l'archetype principal",
            height=400,
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)


# ─── Page : Cartes bridge ─────────────────────────────────────────────────────
elif page == "🌉 Cartes bridge":
    st.title("🌉 Cartes bridge")
    st.markdown(
        "Une carte bridge est une carte qui s'insère dans **plusieurs archetypes distincts** "
        "peu après sa release. `Bridge Score = n_archetypes × log(total_decks_3m)`."
    )

    if card_df.empty:
        st.error("Table `card_impact` absente. Lance le notebook 06.")
    else:
        top_n = st.slider("Top N cartes", 5, 35, 15)
        top = card_df.head(top_n)

        fig = px.bar(
            top, x="bridge_score", y="card_name", orientation="h",
            color="n_archetypes_3m",
            color_continuous_scale="Blues",
            labels={"bridge_score": "Bridge Score", "card_name": "Carte", "n_archetypes_3m": "Nb archetypes"},
            hover_data={"release_month": True, "top_archetype": True, "total_decks_3m": True},
            title=f"Top {top_n} cartes bridge (90j post-release)",
            height=max(400, top_n * 30),
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            top[["card_name", "release_month", "n_archetypes_3m", "total_decks_3m", "bridge_score", "top_archetype"]].rename(
                columns={"card_name": "Carte", "release_month": "Release", "n_archetypes_3m": "Archetypes (3m)",
                         "total_decks_3m": "Decks (3m)", "bridge_score": "Bridge Score", "top_archetype": "Archetype principal"}
            ),
            use_container_width=True, hide_index=True
        )


# ─── Page : Prédictions ───────────────────────────────────────────────────────
elif page == "🔮 Prédictions":
    st.title("🔮 Prédictions — Mois prochain")
    st.markdown(
        "Prédictions `meta_score` du mois prochain via **Random Forest** (notebook 05). "
        "⚠️ R² négatif sur le test set — à interpréter comme signal relatif, pas valeur absolue."
    )

    with st.spinner("Calcul des prédictions…"):
        pred_df = load_predictions()

    if pred_df.empty:
        st.error("scikit-learn non disponible ou données insuffisantes.")
    else:
        last_month = ms_df["month"].max()
        st.info(f"Prédiction pour le mois suivant : **{last_month + 1}** (basé sur les données de {last_month})")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("⬆️ Archetypes en hausse prédite")
            rising = pred_df[pred_df["delta_predicted"] > 0].head(8)
            fig_r = px.bar(
                rising, x="delta_predicted", y="archetype", orientation="h",
                color="delta_predicted", color_continuous_scale="Greens",
                labels={"delta_predicted": "Δprédit", "archetype": "Archetype"},
                height=350,
            )
            fig_r.update_layout(coloraxis_showscale=False,
                                yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig_r, use_container_width=True)

        with col2:
            st.subheader("⬇️ Archetypes en baisse prédite")
            falling = pred_df[pred_df["delta_predicted"] < 0].tail(8).sort_values("delta_predicted")
            fig_f = px.bar(
                falling, x="delta_predicted", y="archetype", orientation="h",
                color="delta_predicted", color_continuous_scale="Reds_r",
                labels={"delta_predicted": "Δprédit", "archetype": "Archetype"},
                height=350,
            )
            fig_f.update_layout(coloraxis_showscale=False,
                                yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig_f, use_container_width=True)

        st.subheader("Toutes les prédictions")
        pred_display = pred_df.copy()
        pred_display["meta_score"] = pred_display["meta_score"].round(4)
        pred_display["predicted_next"] = pred_display["predicted_next"].round(4)
        pred_display["delta_predicted"] = pred_display["delta_predicted"].round(4)
        pred_display.columns = ["Archetype", "Score actuel", "Score prédit", "Δprédit"]
        st.dataframe(pred_display, use_container_width=True, hide_index=True)

        st.caption(
            "Modèle : RandomForest (n_estimators=200, max_depth=5). "
            "Features : meta_score, share, avg_placement. "
            "Limitation : R²≈-37 sur test 2026 (distribution shift 2024→2026)."
        )
