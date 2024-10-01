from typing import TYPE_CHECKING

from dopynion.cards import CardContainer, CardName
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
        self.deck = CardContainer()
        self.deck.append_several(7, CardName.COPPER)
        self.deck.append_several(3, CardName.ESTATE)
        self.deck.shuffle()
        self.hand = CardContainer()
        self.discard = CardContainer()
        self.played_cards = CardContainer()
        self.actions_left: int = 0
        self.buys_left: int = 0
        self.money: int = 0
        self.state = State.ACTION
        self._adjust()

    def _check_for_action_to_buy_transition(self) -> None:
        if not self.hand.contains_action() or not self.actions_left:
            self.actions_left = 0
            self.state = State.BUY

    def _check_for_buy_to_adjust_transition(self) -> None:
        if not self.hand.contains_money() or not self.buys_left:
            self.buys_left = 0
            self.state = State.ADJUST

    def start_turn(self) -> None:
        self.state = State.ACTION
        self.actions_left = 1
        self.buys_left = 1
        self.money = 0
        self._check_for_action_to_buy_transition()

    def end_turn(self) -> None:
        self._adjust()

    def _adjust(self) -> None:
        for _ in range(5):
            self.hand.append(self.deck.pop(0))
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
                self.deleteme,
            )
            card = self.deleteme.pop()
            self.played_cards.append(CardName[card.__name__.upper()])

    def buy(self, card_name: str) -> None:
        source = self.game.stock.get(card_name, [])
        if not source:
            raise InvalidBuyError(card_name)
        card = source[0]
        self._prepare_money(card.cost)
        if self.money >= card.cost:
            self.money -= card.cost
            self.game.move_card(0, source, self.deleteme)
            card = self.deleteme.pop()
            self.discard.append(CardName[card.__name__.upper()])
            self.buys_left -= 1
        else:
            raise NotEnoughMoneyError
        self._check_for_buy_to_adjust_transition()

    def action(self, card_name: CardName) -> None:
        if self.state != State.ACTION:
            raise ActionDuringBuyError(card_name)
        try:
            action = getattr(self, f"_action_{card_name}")
        except AttributeError as err:
            raise UnknownActionError(card_name) from err
        if card_name not in self.hand:
            raise InvalidActionError(card_name)
        action()
        self.actions_left -= 1
        self.hand.remove(card_name)
        self.played_cards.append(card_name)
        self._check_for_action_to_buy_transition()

    def _action_smithy(self) -> None:
        pass

    def _action_village(self) -> None:
        pass
