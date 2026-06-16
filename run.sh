#!/bin/bash

#code pour run le bizbiz  :
#cd ~/code/yugioh-meta-analyzer && bash run.sh


cd "$(dirname "$0")"
source .venv/bin/activate
streamlit run app.py
