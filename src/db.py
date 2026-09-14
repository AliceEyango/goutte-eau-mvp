"""
Acces a la base de donnees SQLite du MVP.

La base ne stocke que les champs necessaires a l'entrainement et a la
restitution : pas de champ brut inutile (cf. exigence C12 du bloc 2).
"""
import sqlite3
from contextlib import contextmanager

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS mesures_journalieres (
    date TEXT PRIMARY KEY,          -- format AAAA-MM-JJ
    station_id TEXT NOT NULL,
    precipitations_mm REAL NOT NULL,   -- cumul de precipitations sur 24h
    pluie_observee INTEGER NOT NULL,   -- 1 si precipitations_mm >= seuil, sinon 0
    temperature_moy_c REAL,            -- donnee de contexte, optionnelle
    source TEXT NOT NULL               -- 'synop', 'infoclimat' ou 'synthetique_demo'
);

CREATE INDEX IF NOT EXISTS idx_mesures_station ON mesures_journalieres(station_id);
"""


@contextmanager
def get_connection():
    os.makedirs(config.DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_connection() as conn:
        conn.executescript(SCHEMA)


def upsert_mesures(rows):
    """
    Insere ou met a jour un lot de mesures journalieres.
    rows : iterable de dicts avec les cles du schema mesures_journalieres.
    """
    with get_connection() as conn:
        conn.executemany(
            """
            INSERT INTO mesures_journalieres
                (date, station_id, precipitations_mm, pluie_observee, temperature_moy_c, source)
            VALUES (:date, :station_id, :precipitations_mm, :pluie_observee, :temperature_moy_c, :source)
            ON CONFLICT(date) DO UPDATE SET
                precipitations_mm = excluded.precipitations_mm,
                pluie_observee = excluded.pluie_observee,
                temperature_moy_c = excluded.temperature_moy_c,
                source = excluded.source
            """,
            rows,
        )


def fetch_all_mesures():
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT date, station_id, precipitations_mm, pluie_observee, temperature_moy_c, source "
            "FROM mesures_journalieres ORDER BY date"
        )
        return [dict(r) for r in cur.fetchall()]


def count_mesures():
    with get_connection() as conn:
        cur = conn.execute("SELECT COUNT(*) AS n FROM mesures_journalieres")
        return cur.fetchone()["n"]
