from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING

from dopynion.cards import Card, CardContainer, CardName
from dopynion.data_model import Player as PlayerData
from dopynion.exceptions import (
    ActionDuringBuyError,
    InvalidActionError,
    InvalidBuyError,
    InvalidDiscardError,
    NotEnoughMoneyError,
)

if TYPE_CHECKING:
    from collections.abc import Generator

    import dopynion.game


class State(Enum):
    ACTION = 1
    BUY = 2
    ADJUST = 3


class PlayerHooks(ABC):
    @abstractmethod
    def confirm_discard_card_from_hand(
        self,
        card_name: CardName,
        hand: list[CardName],
    ) -> bool:
        pass

    @abstractmethod
    def discard_card_from_hand(
        self,
        hand: list[CardName],
    ) -> CardName:
        pass

    @abstractmethod
    def confirm_discard_deck(self) -> bool:
        pass

    @abstractmethod
    def choose_card_to_receive_in_discard(
        self,
        possible_cards: list[CardName],
    ) -> CardName:
        pass

    @abstractmethod
    def skip_card_reception_in_hand(
        self,
        card_name: CardName,
        hand: list[CardName],
    ) -> bool:
        pass

    @abstractmethod
    def trash_money_card_for_better_money_card(
        self,
        money_in_hand: list[CardName],
    ) -> CardName | None:
        pass


class DefaultPlayerHooks(PlayerHooks):
    def confirm_discard_card_from_hand(  # noqa: PLR6301
        self,
        _card_name: CardName,
        _hand: list[CardName],
    ) -> bool:
        return False

    def discard_card_from_hand(  # noqa: PLR6301
        self,
        hand: list[CardName],
    ) -> CardName:
        return hand[0]

    def confirm_discard_deck(self) -> bool:  # noqa: PLR6301
        return False

    def choose_card_to_receive_in_discard(  # noqa: PLR6301
        self,
        possible_cards: list[CardName],
    ) -> CardName:
        return possible_cards[0]

    def skip_card_reception_in_hand(  # noqa: PLR6301
        self,
        _card_name: CardName,
        _hand: list[CardName],
    ) -> bool:
        return False

    def trash_money_card_for_better_money_card(  # noqa: PLR6301
        self,
        _money_in_hand: list[CardName],
    ) -> CardName | None:
        return None


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
        self.purchases_left: int = 0
        self.money: int = 0
        self.playing = False
        self.state_machine: State = State.ACTION
        self.hooks: PlayerHooks = DefaultPlayerHooks()
        self._adjust()

    def __repr__(self) -> str:
        ret = f"Player: {self.name}\n"
        ret += f" - actions left: {self.actions_left}, "
        ret += f"purchases left: {self.purchases_left}, "
        ret += f"money left: {self.money + self.hand.money}\n"
        ret += f" - hand: {self.hand}\n"
        ret += f" - played cards: {self.played_cards}\n"
        ret += f" - deck: {self.deck}\n"
        ret += f" - discard: {self.discard}\n"
        return ret

    def _check_for_action_to_buy_transition(self) -> None:
        if not self.hand.contains_action() or not self.actions_left:
            self.actions_left = 0
            self.state_machine = State.BUY
            logging.debug("go from action to buy")

    def _check_for_buy_to_adjust_transition(self) -> None:
        if not self.purchases_left:
            self.purchases_left = 0
            self.state_machine = State.ADJUST
            logging.debug("go from buy to adjust")

    def start_turn(self) -> None:
        logging.debug("start turn (%s, %d)", self.name, id(self))
        self.game.record.start_turn()
        self.playing = True
        self.state_machine = State.ACTION
        self.actions_left = 1
        self.purchases_left = 1
        self.money = 0
        self._check_for_action_to_buy_transition()

    def end_turn(self) -> None:
        self.game.record.add_action("END OF TURN", self)
        self._adjust()
        self.playing = False
        logging.debug("end turn")

    def take_one_card_from_deck(self) -> CardName:
        if not self.deck:
            self.discard.empty_to(self.deck)
            self.deck.shuffle()
        return self.deck.pop(0)

    def _adjust(self) -> None:
        self.played_cards.empty_to(self.discard)
        self.hand.empty_to(self.discard)
        for _ in range(5):
            self.hand.append(self.take_one_card_from_deck())
        self.state_machine = State.ADJUST

    def _prepare_money(self, money: int) -> None:
        money_cards = self.hand.money_cards
        money_cards.sort(key=lambda card_name: Card.types[card_name].money)
        while self.money < money:
            if not money_cards:
                break
            money_card = money_cards.pop(0)
            self.money += Card.types[money_card].money
            self.hand.remove(money_card)
            self.played_cards.append(money_card)

    def buy(self, card_name: CardName) -> None:
        logging.debug("> BUY %s", card_name)
        self.game.record.add_action(f"BUY {card_name}", self)
        quantity = getattr(self.game.stock, card_name + "_qty")
        if not quantity:
            raise InvalidBuyError(card_name)
        card = Card.types[card_name]
        if self.money + self.hand.money < card.cost:
            raise NotEnoughMoneyError
        self._prepare_money(card.cost)
        self.money -= card.cost
        self.game.stock.remove(card_name)
        self.discard.append(card_name)
        self.purchases_left -= 1
        self._check_for_buy_to_adjust_transition()

    def action(self, card_name: CardName) -> None:
        logging.debug("> ACTION %s", card_name)
        self.game.record.add_action(f"ACTION {card_name}", self)
        if self.state_machine != State.ACTION:
            logging.debug("actions_left %d", self.actions_left)
            logging.debug(self.state_machine.name)
            logging.debug(self.state)
            raise ActionDuringBuyError(card_name)
        if card_name not in self.hand:
            logging.debug(self.state)
            raise InvalidActionError(card_name)
        self.actions_left -= 1
        self.hand.remove(card_name)
        self.played_cards.append(card_name)
        Card.types[card_name].action(self)
        self._check_for_action_to_buy_transition()

    @property
    def state(self) -> PlayerData:
        score = self.score()["score"]
        state = PlayerData(name=self.name, hand=None, score=score)
        if self.playing:
            state.hand = self.hand.state
        return state

    def score(self) -> dict:
        cards = self.hand + self.discard + self.deck
        ret = {}
        ret["province_qty"] = cards.province_qty
        ret["duchy_qty"] = cards.duchy_qty
        ret["estate_qty"] = cards.estate_qty
        ret["curse_qty"] = cards.curse_qty
        ret["gardens_qty"] = cards.gardens_qty
        ret["score"] = sum(
            Card.types[card_name].victory_points for card_name in cards
        ) + cards.gardens_qty * (len(cards) // 10)
        return ret

    def discard_one_card_from_hand(self, card_name: CardName) -> None:
        if card_name not in self.hand:
            msg = f"{card_name} not in player hand"
            raise InvalidDiscardError(msg)
        self.hand.remove(card_name)
        self.discard.append(card_name)

    def other_players(self) -> Generator[Player, None, None]:
        for other_player in self.game.players:
            if other_player != self:
                yield other_player
