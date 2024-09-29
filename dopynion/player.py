from random import shuffle

from dopynion.cards import Card, Copper, Estate
from dopynion.exceptions import (
    ActionDuringBuyError,
    InvalidActionError,
    MissingCardError,
    UnknownActionError,
)


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
        self.discard: list[type[Card]] = []
        self.played_cards: list[type[Card]] = []
        self.state = State.ACTION
        self.actions_left: int = 0
        self.buys_left: int = 0

    def _check_for_action_to_buy_transition(self) -> None:
        if not any(card.is_action for card in self.hand) or not self.actions_left:
            self.actions_left = 0
            self.state = State.BUY

    def _check_for_buy_to_adjust_transition(self) -> None:
        if not any(card.is_money for card in self.hand) or not self.buys_left:
            self.buys_left = 0
            self.state = State.ADJUST

    def start_turn(self) -> None:
        self._adjust()
        self.state = State.ACTION
        self.actions_left = 1
        self.buys_left = 1
        self._check_for_action_to_buy_transition()

    def end_turn(self) -> None:
        pass

    def _adjust(self) -> None:
        self.hand = self.deck[-5:]
        self.deck = self.deck[:-5]
        self.state = State.ADJUST

    @staticmethod
    def move_card(index: int, src: list[type[Card]], dst: list[type[Card]]) -> None:
        dst.append(src.pop(index))

    @staticmethod
    def move_card_by_name(
        card_name: str,
        src: list[type[Card]],
        dst: list[type[Card]],
    ) -> None:
        for index, card in enumerate(src):
            if card.__name__ == card_name:
                Player.move_card(index, src, dst)
                break
        else:
            raise MissingCardError

    def action(self, card_name: str) -> None:
        if self.state != State.ACTION:
            raise ActionDuringBuyError(card_name)
        try:
            action = getattr(self, f"_action_{card_name.lower()}")
        except AttributeError as err:
            raise UnknownActionError(card_name) from err
        if not any(str(card) == card_name for card in self.hand):
            raise InvalidActionError(card_name)
        action()
        self.actions_left -= 1
        self.move_card_by_name(card_name, self.hand, self.played_cards)
        self._check_for_action_to_buy_transition()

    def _action_smithy(self) -> None:
        pass

    def _action_village(self) -> None:
        pass
