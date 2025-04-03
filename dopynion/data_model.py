from datetime import datetime

from pydantic import BaseModel, Field

CardName = str


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


class CardNameAndHand(BaseModel):
    card_name: CardName
    hand: list[CardName]


class Hand(BaseModel):
    hand: list[CardName]


class PossibleCards(BaseModel):
    possible_cards: list[CardName]


class MoneyCardsInHand(BaseModel):
    money_in_hand: list[CardName]
