from pydantic import BaseModel


class Cards(BaseModel):
    quantities: dict[str, int]


class Player(BaseModel):
    name: str
    hand: Cards | None


class Game(BaseModel):
    finished: bool
    players: list[Player]
    stock: Cards
