# Project Documentation Index — Yu-Gi-Oh! Meta Analyzer

**Generated:** 2026-06-19 | **Updated:** 2026-08-01 | **Type:** Data/ML Monolith + Streamlit + Next.js (Phase 5)

---

## Project Overview

- **Type:** Python monolith (data pipeline + ML) + Next.js public frontend
- **Languages:** Python 3.13 (backend/analysis) + TypeScript (frontend)
- **Architecture:** ETL pipeline → SQLite → Notebooks → Streamlit (Phases 1–4) | Next.js → FastAPI → SQLite (Phase 5)
- **Database:** SQLite, ~236 MB, 36 tables (+ `serving.db`, ~9 MB, the API-served subset)
- **Dashboard:** Streamlit 9 pages (`app.py`) + Next.js 8 pages (`frontend/`)
- **Status:** Phases 1–4 done. Phase 5: FastAPI (TOK-31) and frontend live on real data. Ban Radar (TOK-53) shipped. Deploy (TOK-35) is the remaining blocker.

---

## Quick Reference

| What | Where | Command |
|------|-------|---------|
| Launch Streamlit dashboard | `app.py` | `bash run.sh` |
| Launch Next.js frontend | `frontend/` | `cd frontend && npm run dev` |
| Daily price cron | `scripts/snapshot_prices.py` | Scheduled 09:00 |
| Full context | `context.md` | Read first |
| Rebuild DB | See development guide | Notebooks 01→12 |
| Launch FastAPI | `backend/` | `.venv/bin/uvicorn app.main:app --reload --port 8000` |
| Build ban radar | `scripts/build_ban_radar.py` | `--backtest` to validate scoring |
| Build serving DB | `scripts/build_serving_db.py` | Before every deploy |
| Backlog | `BACKLOG.md` | Linear: linear.app/tokoz |

---

## Generated Documentation

- [Project Overview](./project-overview.md) — Executive summary, tech stack, validated metrics
- [Architecture](./architecture.md) — Pipeline layers, algorithms, planned Phase 5
- [Data Models](./data-models.md) — Complete SQLite schema (36 tables, all columns documented)
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
- Read `docs/api-contracts.md` for endpoint specifications
- The API is read-only and serves only precomputed tables — see `build_serving_db.py`
- Target deployment: Vercel (frontend). The backend fits in ~9 MB read-only, so a
  separate Railway service may not be needed — to be decided (TOK-35).

### Key pitfalls (from context.md)
- `ban_tcg IS NULL` = **legal** card (don't use `!= 'Forbidden'` alone)
- `tournament_location` is NULL everywhere — use `ocg` flag for regional split
- Notebook cells can accidentally be stored as `markdown` type in .ipynb JSON — check `cell_type` field
- Extra deck `amount` should be normalized to 1 for Jaccard (not 3)
- `banlist_history`: filter on the `format` column, never `list_name LIKE '%TCG%'`
- `deck_cards` ingestion must purge a deck's rows before reinserting (unique index enforces it)

---

## TOK Roadmap Summary

| Phase | TOKs | Status |
|-------|------|--------|
| Data ingestion | TOK-5, 6, 7, 8, 9, 10 | ✅ All done |
| Co-occurrence + graph | TOK-11 to 20 | ✅ All done |
| Meta + prediction | TOK-21 to 25 | ✅ All done |
| NLP + boutique | TOK-26 to 30, 45 | ✅ All done |
| Phase 5 front-end | TOK-32 ✅, TOK-33 ✅, TOK-34 🟡 partiel | 🏗️ En cours |
| Phase 5 backend | TOK-31 ✅ | ✅ Done |
| Deploy | TOK-35 — serving DB ready, hosting to decide | 🔜 Next |
| UX foundations | TOK-48 to 51 ✅, TOK-52 🔜 | 🏗️ En cours |
| Ban Radar | TOK-53 ✅ · TOK-55 unblocked (2 backtest points) | 🏗️ En cours |
| Ideas | TOK-36, 37 | 🔜 Backlog |
