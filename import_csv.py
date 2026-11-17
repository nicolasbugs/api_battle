"""Insere todos os registros do CSV em lote, sem duplicar player_id."""
import argparse
import csv
from pathlib import Path

from database import connect, initialize, BASE_DIR
from models import Player

COLUMNS = list(Player.model_fields)


def import_players(csv_path: Path) -> tuple[int, int]:
    initialize()
    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames != COLUMNS:
            raise ValueError(f"Colunas inesperadas no CSV: {reader.fieldnames}; esperado: {COLUMNS}")
        players = [Player.model_validate(row) for row in reader]

    placeholders = ", ".join("?" for _ in COLUMNS)
    names = ", ".join(COLUMNS)
    query = f"INSERT OR IGNORE INTO players ({names}) VALUES ({placeholders})"
    with connect() as conn:
        before = conn.execute("SELECT COUNT(*) FROM players").fetchone()[0]
        conn.executemany(query, [tuple(getattr(p, key) for key in COLUMNS) for p in players])
        after = conn.execute("SELECT COUNT(*) FROM players").fetchone()[0]
    return after - before, after


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Importação em lote dos jogadores FIFA")
    parser.add_argument("--csv", type=Path, default=BASE_DIR / "data" / "fifa_player_performance_market_value.csv")
    args = parser.parse_args()
    inserted, total = import_players(args.csv)
    print(f"Inseridos nesta execução: {inserted} | Total no banco: {total}")
