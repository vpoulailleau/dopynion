from random import shuffle

from dopynion.cards import Card, Copper, Estate


class State:
    ACTION = 1
    BUY = 2
    ADJUST = 3


class Player:
    def __init__(self, name: str) -> None:
        self.name = name
        self.deck: list[type[Card]] = [Copper] * 7 + [Estate] * 3
        shuffle(self.deck)
        self.hand: list[type[Card]] = []
        self.state = State.ACTION
        self._adjust()

    def start_turn(self) -> None:
        self.state = State.ACTION
        self._adjust()

    def _adjust(self) -> None:
        self.hand = self.deck[-5:]
        self.deck = self.deck[:-5]
        self.state = State.ADJUST
