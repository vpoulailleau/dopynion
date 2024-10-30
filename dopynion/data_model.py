from datetime import datetime

from pydantic import BaseModel, Field


class Cards(BaseModel):
    quantities: dict[str, int]


class Player(BaseModel):
    name: str
    hand: Cards | None
    score: int


class Game(BaseModel):
    finished: bool
    players: list[Player]
    stock: Cards


class ActionRecord(BaseModel):
    action: str
    player: Player
    score: int


class PlayerTurnRecord(BaseModel):
    actions: list[ActionRecord] = Field(default_factory=list)


class GameRecord(BaseModel):
    date: datetime
    turns: list[PlayerTurnRecord] = Field(default_factory=list)
