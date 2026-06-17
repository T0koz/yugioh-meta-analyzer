#!/bin/bash

#code pour run le bizbiz  :
#cd ~/code/yugioh-meta-analyzer && bash run.sh


cd "$(dirname "$0")"
source .venv/bin/activate

# Snapshot quotidien des prix boutique (idempotent — skip si déjà fait aujourd'hui)
python scripts/snapshot_prices.py

streamlit run app.py
