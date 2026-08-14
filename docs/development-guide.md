# Development Guide — Yu-Gi-Oh! Meta Analyzer

## Prerequisites

- **Python 3.13** (Homebrew: `brew install python@3.13`)
- **Node.js** (for BMad tooling only)
- **Git**
- ~2 GB disk space (venv + SQLite + raw data)

---

## Initial Setup

```bash
# 1. Clone
git clone https://github.com/thomascozian/yugioh-meta-analyzer.git
cd yugioh-meta-analyzer

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install pandas numpy jupyter ipykernel networkx pyvis scikit-learn \
            streamlit plotly statsmodels youtube-transcript-api requests scipy
```

---

## Rebuild Database from Scratch

Run in this exact order:

```bash
source .venv/bin/activate

# Step 1: Fetch all cards from YGOPRODeck API
python scripts/fetch_cards.py
# → data/raw/cards.json (13,797 cards, ~31 MB)

# Step 2: Initialize SQLite database
python scripts/init_db.py
# → data/yugioh.db (tables: cards, card_sets, card_prices)

# Step 3: Fetch TCG tournament decklists
python scripts/fetch_tournament_decks.py
# → ~9,330 decklists (takes ~10 min, paginates 100/page)

# Step 4: Fetch OCG decklists
python scripts/fetch_ocg_decks.py
# → ~10,558 decklists (takes ~10 min)

# Step 5: Set up impact tables
python scripts/setup_impact_tables.py

# Step 6: Initial price snapshot
python scripts/snapshot_prices.py
# → ~13,753 price rows in card_price_history

# Step 7: Run notebooks in order
jupyter notebook
# Execute: 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09_banlist → 10_archetypes → 10_boutique → 11 → 12
```

**Note:** Notebooks 01 and 09_ocg_tcg_correlation are read-only (no DB writes needed for the pipeline).

---

## Launch the Dashboard

```bash
# Option A: Direct
source .venv/bin/activate
streamlit run app.py
# → http://localhost:8501

# Option B: Via run.sh
bash run.sh
```

---

## Daily Price Snapshot (Cron)

Automatically scheduled via Claude Scheduled Tasks at 09:00 daily:

```bash
cd /Users/thomascozian/code/yugioh-meta-analyzer && source .venv/bin/activate && python scripts/snapshot_prices.py
```

Manual trigger: `python scripts/snapshot_prices.py`

The script is idempotent — if today's snapshot already exists, it exits early.

---

## Refresh Meta Data (Weekly)

```bash
source .venv/bin/activate

# Re-fetch tournament decklists (new tournaments since last run)
python scripts/fetch_tournament_decks.py
python scripts/fetch_ocg_decks.py

# Re-run the analysis notebooks in order
# (or just the ones whose outputs you need)
```

---

## Key Files to Read Before Coding

| File | Why |
|------|-----|
| `context.md` | Full technical context — algorithms, design decisions, pitfalls |
| `docs/architecture.md` | System architecture + layer descriptions |
| `docs/data-models.md` | Complete SQLite schema |
| `BACKLOG.md` | What's done and what's next |

---

## Common Development Tasks

### Add a new Streamlit page

1. Add page name to `st.sidebar.radio(...)` list in `app.py`
2. Add `elif page == "🆕 New Page":` section
3. Use `@st.cache_data(ttl=300)` for any DB queries

### Add a new DB table from a notebook

1. Compute DataFrame in notebook
2. Write with:
   ```python
   df.to_sql('new_table_name', con, if_exists='replace', index=False)
   ```
3. Add table documentation to `docs/data-models.md`

### Add a new feature to the boutique signal

1. Compute new feature in `10_boutique_alert_score.ipynb`
2. Update `boutique_alerts` or `boutique_buy_signals` schema
3. Update `app.py` Signal boutique page to display it

### Extend the prediction model

Edit `notebooks/05_meta_prediction.ipynb`:
- Add feature to `FEATURE_COLS` list (currently 20 features)
- Retrain and re-evaluate walk-forward CV
- Update `meta_predictions` table with new predictions

---

## Environment Variables

No `.env` file needed. The only sensitive config is:
- `~/.claude/settings.json` — Linear API key (never paste in chat)

---

## Pitfalls & Known Issues

| Issue | Solution |
|-------|---------|
| `ban_tcg IS NULL` means LEGAL | Don't use `!= 'Forbidden'` to check legality — use `IS NULL OR ban_tcg != 'Forbidden'` |
| Notebook cells stored as `markdown` type | Fixed in 05_meta_prediction.ipynb — if re-occurs, edit JSON directly to set `cell_type: "code"` |
| `tournament_location` is NULL everywhere | Use `ocg` flag (0=TCG, 1=OCG) for regional segmentation instead |
| `amount` in extra deck can be 1, 2, or 3 | Normalize to 1 for Jaccard (each extra deck card is used at most once at a time) |
| OCG archetype names differ from TCG | Use `archetype_mapping` table for cross-format lookups |
| YouTube ASR transcribes "Kewl Tune" as "Cool Tune" | Fixed in `ASR_CORRECTIONS` dict in notebook 08 |

---

## Git Conventions

```
feat: short description of new feature
fix: short description of bug fix
docs: documentation update
refactor: code improvement without behavior change
```

Co-author all commits with Claude:
```
Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

---

## Phase 5 Setup (Coming Soon)

When building the React + FastAPI frontend:

```bash
# Backend (FastAPI)
pip install fastapi uvicorn

# Frontend: Next.js 16 (already scaffolded in frontend/)
cd frontend && npm run dev

# Deployment (TOK-35)
# Build the served DB first: python scripts/build_serving_db.py
# Backend reads YGO_DB_PATH=/app/data/serving.db (~9 MB, read-only)
# Frontend: Vercel. Backend host still to be decided — at this size a
# dedicated service may be unnecessary.
```
