import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from database import initialize
from import_csv import import_players
from main import app


@pytest.fixture
def client(monkeypatch):
    with tempfile.TemporaryDirectory() as temp:
        monkeypatch.setenv("DATABASE_PATH", str(Path(temp) / "test.db"))
        monkeypatch.setenv("API_KEY", "chave-secreta-de-teste")
        initialize()
        inserted, total = import_players(Path(__file__).resolve().parents[1] / "data" / "fifa_player_performance_market_value.csv")
        assert inserted == 2800 and total == 2800
        with TestClient(app) as test_client:
            yield test_client


def test_consultas(client):
    assert client.get("/fifa/count").json() == {"total": 2800}
    assert len(client.get("/fifa").json()) == 2800
    assert client.get("/fifa/id/1").json()["player_name"] == "Player_1"
    brazil = client.get("/fifa/nat/Brazil").json()
    assert len(brazil) == 380
    assert all(p["nationality"] == "Brazil" for p in brazil)
    assert client.get("/fifa/id/9999999").status_code == 404


def test_post_protegido_e_duplicacao(client):
    player = client.get("/fifa/id/1").json()
    player["player_id"] = 50000
    assert client.post("/fifa", json=player).status_code == 401
    headers = {"X-API-Key": "chave-secreta-de-teste"}
    assert client.post("/fifa", json=player, headers=headers).status_code == 201
    assert client.post("/fifa", json=player, headers=headers).status_code == 409
    assert client.get("/fifa/count").json() == {"total": 2801}
    player["age"] = -1
    player["player_id"] = 50001
    assert client.post("/fifa", json=player, headers=headers).status_code == 422
