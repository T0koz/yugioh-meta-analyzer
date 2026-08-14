import os
import sqlite3
from pathlib import Path

# En production on sert `data/serving.db` (~9 Mo, les 12 tables interrogées par
# l'API) au lieu de `yugioh.db` (~170 Mo, dont 74% de decklists jamais lues en
# ligne) : YGO_DB_PATH=/app/data/serving.db.
# Voir scripts/build_serving_db.py.
DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "yugioh.db"
DB_PATH = Path(os.environ.get("YGO_DB_PATH") or DEFAULT_DB_PATH)


def get_db():
    # check_same_thread=False : FastAPI exécute les endpoints sync (def, pas async def)
    # dans un threadpool (anyio.to_thread), potentiellement sur un thread différent de
    # celui qui a résolu cette dépendance. Sans ce flag, sqlite3 lève une
    # ProgrammingError par intermittence. Sûr ici car chaque requête a sa propre
    # connexion, jamais partagée entre threads concurrents.
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    try:
        yield con
    finally:
        con.close()
