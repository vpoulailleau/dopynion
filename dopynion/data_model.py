from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class CardName(StrEnum):  # Create with a metaclass
    ADVENTURER = "adventurer"
    BUREAUCRAT = "bureaucrat"
    CELLAR = "cellar"
    CHANCELLOR = "chancellor"
    CHAPEL = "chapel"
    COPPER = "copper"
    COUNCILROOM = "councilroom"
    CURSE = "curse"
    DUCHY = "duchy"
    ESTATE = "estate"
    FEAST = "feast"
    FESTIVAL = "festival"
    GARDENS = "gardens"
    GOLD = "gold"
    LABORATORY = "laboratory"
    LIBRARY = "library"
    MARKET = "market"
    MILITIA = "militia"
    MINE = "mine"
    MONEYLENDER = "moneylender"
    NONE = "NONE"
    PROVINCE = "province"
    REMODEL = "remodel"
    SILVER = "silver"
    SMITHY = "smithy"
    VILLAGE = "village"
    WITCH = "witch"
    WOODCUTTER = "woodcutter"
    WORKSHOP = "workshop"

    def __repr__(self) -> str:
        return self.value.title()


class Cards(BaseModel):
    quantities: dict[CardName, int]


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
