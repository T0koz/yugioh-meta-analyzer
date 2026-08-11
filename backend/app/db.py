import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "yugioh.db"


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
