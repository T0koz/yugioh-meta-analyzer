import os
import sqlite3
from pathlib import Path

# En production on sert `data/serving.db` (~9 Mo, les 12 tables interrogées par
# l'API) au lieu de `yugioh.db` (~170 Mo, dont 74% de decklists jamais lues en
# ligne) : YGO_DB_PATH=/app/data/serving.db.
# Voir scripts/build_serving_db.py.
DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "yugioh.db"
# Sur Vercel (variable système VERCEL), la base de service est embarquée à côté du code
# (backend/data/serving.db, voir vercel.json et docs/deploiement.md) : pas de chemin absolu à deviner.
BUNDLED_DB_PATH = Path(__file__).resolve().parents[1] / "data" / "serving.db"
DB_PATH = Path(
    os.environ.get("YGO_DB_PATH")
    or (BUNDLED_DB_PATH if os.environ.get("VERCEL") else DEFAULT_DB_PATH)
)


def get_db():
    # check_same_thread=False : FastAPI exécute les endpoints sync (def, pas async def)
    # dans un threadpool (anyio.to_thread), potentiellement sur un thread différent de
    # celui qui a résolu cette dépendance. Sans ce flag, sqlite3 lève une
    # ProgrammingError par intermittence. Sûr ici car chaque requête a sa propre
    # connexion, jamais partagée entre threads concurrents.
    # Lecture seule (TOK-35) : l'API ne modifie jamais la base, et sur Vercel le système de
    # fichiers de la fonction est de toute façon en lecture seule.
    con = sqlite3.connect(f"{DB_PATH.resolve().as_uri()}?mode=ro", uri=True, check_same_thread=False)
    con.row_factory = sqlite3.Row
    try:
        yield con
    finally:
        con.close()
