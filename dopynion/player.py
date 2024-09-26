from random import shuffle

from dopynion.cards import Card, Copper, Estate


class Player:
    def __init__(self, name: str) -> None:
        self.name = name
        self.deck: list[Card] = [Copper] * 7 + [Estate] * 3
        shuffle(self.deck)
