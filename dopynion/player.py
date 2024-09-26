from random import shuffle

from dopynion.cards import Card, Copper, Estate


class Player:
    def __init__(self, name: str) -> None:
        self.name = name
        self.deck: list[type[Card]] = [Copper] * 7 + [Estate] * 3
        self.hand: list[type[Card]] = []
        shuffle(self.deck)

    def start_turn(self) -> None:
        self.hand = self.deck[-5:]
        self.deck = self.deck[:-5]
