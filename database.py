"""Conexão SQLite e preparação do esquema."""
import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

SCHEMA = """
CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY,
    player_name TEXT NOT NULL,
    age INTEGER NOT NULL,
    nationality TEXT NOT NULL,
    club TEXT NOT NULL,
    position TEXT NOT NULL,
    overall_rating INTEGER NOT NULL,
    potential_rating INTEGER NOT NULL,
    matches_played INTEGER NOT NULL,
    goals INTEGER NOT NULL,
    assists INTEGER NOT NULL,
    minutes_played INTEGER NOT NULL,
    market_value_million_eur REAL NOT NULL,
    contract_years_left INTEGER NOT NULL,
    injury_prone TEXT NOT NULL,
    transfer_risk_level TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_players_nationality ON players(nationality);
"""


def database_path() -> Path:
    return Path(os.getenv("DATABASE_PATH", str(BASE_DIR / "data" / "fifa.db")))


def connect() -> sqlite3.Connection:
    path = database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout=10000")
    return conn


def initialize() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA)
