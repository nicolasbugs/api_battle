"""Modelo fiel às 16 colunas do CSV."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class Player(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    player_id: int = Field(gt=0, description="Identificador único do jogador")
    player_name: str = Field(min_length=1, max_length=200)
    age: int = Field(ge=0, le=120)
    nationality: str = Field(min_length=1, max_length=100)
    club: str = Field(min_length=1, max_length=150)
    position: str = Field(min_length=1, max_length=40)
    overall_rating: int = Field(ge=0, le=100)
    potential_rating: int = Field(ge=0, le=100)
    matches_played: int = Field(ge=0)
    goals: int = Field(ge=0)
    assists: int = Field(ge=0)
    minutes_played: int = Field(ge=0)
    market_value_million_eur: float = Field(ge=0)
    contract_years_left: int = Field(ge=0)
    injury_prone: Literal["Yes", "No"]
    transfer_risk_level: Literal["Low", "Medium", "High"]
