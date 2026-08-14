# Project Overview — Yu-Gi-Oh! Meta Analyzer

## Executive Summary

A full-stack data science and analytics platform for competitive Yu-Gi-Oh! TCG meta analysis, prediction, and shop intelligence. The system collects tournament decklists, computes synergy graphs, trains predictive models, and surfaces actionable signals for both players and card shops.

**Business value:** A validated OCG→TCG lag signal (r=0.771, p<0.0001, 4-month lead time) enables card shops to stock inventory before meta explosions — a B2B product valued at ~150€/month per shop.

---

## Project Identity

| Field | Value |
|-------|-------|
| **Name** | yugioh-meta-analyzer |
| **Type** | Data / ML monolith + Streamlit dashboard |
| **Language** | Python 3.13 |
| **Database** | SQLite (`data/yugioh.db`, ~236 MB) + generated `serving.db` (~9 MB) |
| **Dashboard** | Streamlit (`app.py`, 9 pages) |
| **Owner** | Thomas Cozian (Tokoz) |
| **Target completion** | Before Le Wagon Data Science (Oct 12, 2026) |

---

## Technology Stack

| Category | Technology | Version |
|----------|------------|---------|
| Language | Python | 3.13 (Homebrew) |
| Data manipulation | pandas | 3.0.3 |
| Numerical computing | numpy | 2.4.6 |
| Machine learning | scikit-learn | 1.9.0 |
| Time-series | statsmodels | 0.14.6 |
| Statistical analysis | scipy | 1.17.1 |
| Graph analysis | networkx | 3.6.1 |
| Graph visualization | pyvis | 0.3.2 |
| Dashboard | streamlit | 1.58.0 |
| Charts | plotly | 6.8.0 |
| HTTP client | requests | 2.34.2 |
| NLP (YouTube) | youtube-transcript-api | 1.2.4 |
| Database | SQLite (stdlib) | — |
| Notebook environment | Jupyter | — |

---

## Architecture Overview

The project follows a **pipeline architecture** organized in numbered phases:

```
External APIs → Scripts (ETL) → SQLite DB → Notebooks (Analysis) → Streamlit (Dashboard)
```

1. **Data ingestion** (scripts): fetch from YGOPRODeck API + yugiohmeta.com
2. **Storage** (SQLite): 36 tables covering raw data, co-occurrence, graph metrics, ML outputs
3. **Analysis** (notebooks 01-12): computation pipeline executed in order
4. **Serving** (app.py): Streamlit dashboard with 9 interactive pages
5. **Scheduling** (cron): daily price snapshot at 09:00 via Claude Scheduled Tasks

---

## Core Metrics & Validated Findings

| Metric | Value |
|--------|-------|
| Tournament decklists | 19,888 (TCG + OCG, 2024–2026) |
| Cards in database | 13,797 |
| Co-occurrence pairs | 44,255 total (6 variant tables) |
| Graph nodes / communities | ~660 nodes / 63 communities |
| OCG→TCG lag correlation | r = 0.771, p < 0.0001, lag = 4 months |
| Prediction accuracy | Spearman ρ ≈ +0.65 (walk-forward CV, 9-month window) |
| DB size | ~236 MB (served subset: ~9 MB) |

---

## Roadmap Status

| Phase | Status | Description |
|-------|--------|-------------|
| 1 — Data ingestion | ✅ Done | YGOPRODeck API, SQLite, images, price history |
| 2 — Co-occurrence + graph | ✅ Done | 6 co-occurrence variants, graph centrality, communities |
| 3 — Meta score + prediction | ✅ Done | Ridge + AR(1) + Naïf ensemble, banlist features |
| 4 — Dashboard + NLP | ✅ Done | 9-page Streamlit, YouTube NLP combos |
| Signal boutiques | ✅ Done | OCG alert score, TCG banlist compatibility filter |
| 5 — Front-end & API | 🔜 Next | React + FastAPI + deployment |
