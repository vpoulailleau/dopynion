from random import shuffle
from typing import TYPE_CHECKING

from dopynion.cards import Card, Copper, Estate
from dopynion.exceptions import (
    ActionDuringBuyError,
    InvalidActionError,
    InvalidBuyError,
    NotEnoughMoneyError,
    UnknownActionError,
)

if TYPE_CHECKING:
    import dopynion.game


class State:
    ACTION = 1
    BUY = 2
    ADJUST = 3


class Player:
    def __init__(self, name: str) -> None:
        self.game: dopynion.game.Game = None
        self.name = name
        self.deck: list[type[Card]] = [Copper] * 7 + [Estate] * 3
        shuffle(self.deck)
        self.hand: list[type[Card]] = []
        self.discard: list[type[Card]] = []
        self.played_cards: list[type[Card]] = []
        self.state = State.ACTION
        self.actions_left: int = 0
        self.buys_left: int = 0
        self.money: int = 0

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
        self.money = 0
        self._check_for_action_to_buy_transition()

    def end_turn(self) -> None:
        pass

    def _adjust(self) -> None:
        self.hand = self.deck[-5:]
        self.deck = self.deck[:-5]
        self.state = State.ADJUST

    def _prepare_money(self, money: int) -> None:
        money_cards = [card for card in self.hand if card.is_money]
        money_cards.sort(key=lambda card: card.cost, reverse=True)
        while self.money < money:
            if not money_cards:
                break
            self.money += money_cards[0].money
            self.game.move_card_by_name(
                money_cards[0].__name__,
                self.hand,
                self.played_cards,
            )

    def buy(self, card_name: str) -> None:
        source = self.game.buyable_cards.get(card_name, [])
        if not source:
            raise InvalidBuyError(card_name)
        card = source[0]
        self._prepare_money(card.cost)
        if self.money >= card.cost:
            self.money -= card.cost
            self.game.move_card(0, source, self.discard)
            self.buys_left -= 1
        else:
            raise NotEnoughMoneyError
        self._check_for_buy_to_adjust_transition()

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
        self.game.move_card_by_name(card_name, self.hand, self.played_cards)
        self._check_for_action_to_buy_transition()

    def _action_smithy(self) -> None:
        pass

    def _action_village(self) -> None:
        pass
