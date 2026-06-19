# Project Documentation Index — Yu-Gi-Oh! Meta Analyzer

**Generated:** 2026-06-19 | **Scan level:** Exhaustive | **Type:** Data/ML Monolith + Streamlit

---

## Project Overview

- **Type:** Python monolith (data pipeline + ML + dashboard)
- **Primary language:** Python 3.13
- **Architecture:** ETL pipeline → SQLite → Notebooks → Streamlit
- **Database:** SQLite, ~150 MB, 35+ tables
- **Dashboard:** Streamlit, 9 pages (`app.py`)
- **Status:** Phases 1–4 + boutique signal complete. Phase 5 (React + FastAPI) next.

---

## Quick Reference

| What | Where | Command |
|------|-------|---------|
| Launch dashboard | `app.py` | `bash run.sh` |
| Daily price cron | `scripts/snapshot_prices.py` | Scheduled 09:00 |
| Full context | `context.md` | Read first |
| Rebuild DB | See development guide | Notebooks 01→12 |
| Backlog | `BACKLOG.md` | Linear: linear.app/tokoz |

---

## Generated Documentation

- [Project Overview](./project-overview.md) — Executive summary, tech stack, validated metrics
- [Architecture](./architecture.md) — Pipeline layers, algorithms, planned Phase 5
- [Data Models](./data-models.md) — Complete SQLite schema (35+ tables, all columns documented)
- [Source Tree Analysis](./source-tree-analysis.md) — Annotated file tree + data flow diagram
- [Development Guide](./development-guide.md) — Setup, rebuild, run, pitfalls
- [API Contracts](./api-contracts.md) — Current consumed APIs + planned FastAPI endpoints

---

## Existing Project Documentation

- [context.md](../context.md) — Full technical context (read before coding)
- [README.md](../README.md) — High-level project overview
- [BACKLOG.md](../BACKLOG.md) — Feature backlog with TOK status
- [data/SOURCES.md](../data/SOURCES.md) — Data source documentation

---

## Key Metrics (as of 2026-06-19)

| Metric | Value |
|--------|-------|
| Tournament decklists | 19,888 (TCG + OCG) |
| Cards | 13,797 with images + daily price tracking |
| Co-occurrence pairs | 44,255 across 6 variant tables |
| OCG→TCG correlation | r = 0.771, p < 0.0001, lag = 4 months |
| Prediction accuracy | Spearman ρ ≈ +0.65 |
| Graph communities | 63 (Louvain) |
| Boutique archetypes | 69 scored, TCG banlist-adjusted |

---

## Getting Started (for AI agents)

1. Read `context.md` — contains all design decisions and pitfalls
2. Read `docs/architecture.md` — understand the pipeline structure
3. Read `docs/data-models.md` — understand the database schema before writing any SQL
4. Check `BACKLOG.md` for current TOK status

### For Phase 5 (React + FastAPI)
- Read `docs/api-contracts.md` for planned endpoint specifications
- Current Streamlit loaders in `app.py` map directly to the planned FastAPI endpoints
- Target deployment: Vercel (frontend) + Railway (backend)

### Key pitfalls (from context.md)
- `ban_tcg IS NULL` = **legal** card (don't use `!= 'Forbidden'` alone)
- `tournament_location` is NULL everywhere — use `ocg` flag for regional split
- Notebook cells can accidentally be stored as `markdown` type in .ipynb JSON — check `cell_type` field
- Extra deck `amount` should be normalized to 1 for Jaccard (not 3)

---

## TOK Roadmap Summary

| Phase | TOKs | Status |
|-------|------|--------|
| Data ingestion | TOK-5, 6, 7, 8, 9, 10 | ✅ All done |
| Co-occurrence + graph | TOK-11 to 20 | ✅ All done |
| Meta + prediction | TOK-21 to 25 | ✅ All done |
| NLP + boutique | TOK-26 to 30, 45 | ✅ All done |
| Phase 5 front-end | TOK-31 to 35 | 🔜 Next |
| Ideas | TOK-36, 37 | 🔜 Backlog |
