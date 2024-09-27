from random import shuffle

from dopynion.cards import Card, Copper, Estate
from dopynion.exceptions import UnknownActionError


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

    def start_turn(self) -> None:
        self._adjust()
        self.state = State.ACTION

    def end_turn(self) -> None:
        pass

    def _adjust(self) -> None:
        self.hand = self.deck[-5:]
        self.deck = self.deck[:-5]
        self.state = State.ADJUST

    def action(self, card_name: str) -> None:
        try:
            getattr(self, f"_action_{card_name.lower()}")()
        except AttributeError as err:
            raise UnknownActionError(card_name) from err
