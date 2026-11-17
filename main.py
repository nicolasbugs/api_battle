"""API BATTLE - Univates 2026/B."""
import os
import secrets
import sqlite3
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException, Path, status

from database import connect, initialize
from models import Player


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize()
    yield


app = FastAPI(
    title="API BATTLE — FIFA",
    version="1.0.0",
    description=(
        "API REST da atividade API BATTLE (Univates 2026/B). "
        "GETs públicos para validação entre grupos; POST exige X-API-Key. "
        "Dados conforme arquivo CSV fornecido na atividade."
    ),
    lifespan=lifespan,
)


def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> None:
    configured = os.getenv("API_KEY")
    if not configured:
        raise HTTPException(status_code=503, detail="API_KEY não configurada no servidor")
    if not x_api_key or not secrets.compare_digest(x_api_key, configured):
        raise HTTPException(status_code=401, detail="Chave de API ausente ou inválida")


@app.post(
    "/fifa", tags=["Jogadores"], status_code=status.HTTP_201_CREATED,
    response_model=Player, summary="Cadastrar jogador (exige X-API-Key)",
    responses={401: {"description": "Chave ausente ou inválida"}, 409: {"description": "ID já cadastrado"}},
)
def create_player(player: Player, _: None = Depends(require_api_key)):
    """Cadastra um jogador com as mesmas 16 colunas do CSV. Não substitui IDs existentes."""
    fields = list(Player.model_fields)
    sql = f"INSERT INTO players ({', '.join(fields)}) VALUES ({', '.join('?' for _ in fields)})"
    try:
        with connect() as conn:
            conn.execute(sql, tuple(getattr(player, key) for key in fields))
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="player_id já cadastrado")
    return player


@app.get("/fifa/count", tags=["Jogadores"], summary="Contar jogadores")
def count_players():
    """Retorna a quantidade total de jogadores presentes no banco."""
    with connect() as conn:
        count = conn.execute("SELECT COUNT(*) FROM players").fetchone()[0]
    return {"total": count}


@app.get("/fifa", tags=["Jogadores"], response_model=list[Player], summary="Listar todos os jogadores")
def list_players():
    """Retorna todos os registros em ordem crescente de player_id (sem paginação, conforme roteiro)."""
    with connect() as conn:
        records = conn.execute("SELECT * FROM players ORDER BY player_id").fetchall()
    return [dict(row) for row in records]


@app.get("/fifa/id/{id}", tags=["Jogadores"], response_model=Player, summary="Buscar jogador por ID")
def player_by_id(id: int = Path(gt=0, description="Valor da coluna player_id")):
    """Consulta um único jogador pelo identificador; retorna 404 se não existir."""
    with connect() as conn:
        row = conn.execute("SELECT * FROM players WHERE player_id = ?", (id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")
    return dict(row)


@app.get("/fifa/nat/{exp}", tags=["Jogadores"], response_model=list[Player], summary="Buscar jogadores por nacionalidade")
def players_by_nationality(exp: str = Path(min_length=1, max_length=100, description="Ex.: Brazil")):
    """Filtra por igualdade exata na coluna nationality; exemplo: /fifa/nat/Brazil."""
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM players WHERE nationality = ? ORDER BY player_id", (exp,)
        ).fetchall()
    return [dict(row) for row in rows]
