from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING

from dopynion.cards import Card, CardContainer, CardName
from dopynion.data_model import CardName as CardNameDataModel
from dopynion.data_model import (
    CardNameAndHand,
    Hand,
    MoneyCardsInHand,
    PossibleCards,
)
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

logger = logging.getLogger(__name__)


class State(Enum):
    ACTION = 1
    BUY = 2
    ADJUST = 3


class PlayerHooks(ABC):
    @abstractmethod
    def confirm_discard_card_from_hand(
        self,
        decision_input: CardNameAndHand,
    ) -> bool:
        pass

    @abstractmethod
    def confirm_trash_card_from_hand(
        self,
        decision_input: CardNameAndHand,
    ) -> bool:
        pass

    @abstractmethod
    def discard_card_from_hand(
        self,
        decision_input: Hand,
    ) -> CardNameDataModel:
        pass

    @abstractmethod
    def trash_card_from_hand(
        self,
        decision_input: Hand,
    ) -> CardNameDataModel:
        pass

    @abstractmethod
    def confirm_discard_deck(self) -> bool:
        pass

    @abstractmethod
    def choose_card_to_receive_in_discard(
        self,
        decision_input: PossibleCards,
    ) -> CardNameDataModel:
        pass

    @abstractmethod
    def choose_card_to_receive_in_deck(
        self,
        decision_input: PossibleCards,
    ) -> CardNameDataModel:
        pass

    @abstractmethod
    def skip_card_reception_in_hand(
        self,
        decision_input: CardNameAndHand,
    ) -> bool:
        pass

    @abstractmethod
    def trash_money_card_for_better_money_card(
        self,
        decision_input: MoneyCardsInHand,
    ) -> CardNameDataModel | None:
        pass


class DefaultPlayerHooks(PlayerHooks):
    def confirm_discard_card_from_hand(  # noqa: PLR6301
        self,
        _decision_input: CardNameAndHand,
    ) -> bool:
        return False

    def confirm_trash_card_from_hand(  # noqa: PLR6301
        self,
        _decision_input: CardNameAndHand,
    ) -> bool:
        return False

    def discard_card_from_hand(  # noqa: PLR6301
        self,
        decision_input: Hand,
    ) -> CardNameDataModel:
        return decision_input.hand[0]

    def trash_card_from_hand(  # noqa: PLR6301
        self,
        decision_input: Hand,
    ) -> CardNameDataModel:
        return decision_input.hand[0]

    def confirm_discard_deck(self) -> bool:  # noqa: PLR6301
        return False

    def choose_card_to_receive_in_discard(  # noqa: PLR6301
        self,
        decision_input: PossibleCards,
    ) -> CardNameDataModel:
        return decision_input.possible_cards[0]

    def choose_card_to_receive_in_deck(  # noqa: PLR6301
        self,
        decision_input: PossibleCards,
    ) -> CardNameDataModel:
        return decision_input.possible_cards[0]

    def skip_card_reception_in_hand(  # noqa: PLR6301
        self,
        _decision_input: CardNameAndHand,
    ) -> bool:
        return False

    def trash_money_card_for_better_money_card(  # noqa: PLR6301
        self,
        _decision_input: MoneyCardsInHand,
    ) -> CardNameDataModel | None:
        return None


class Player:
    def __init__(self, name: str) -> None:
        self.game: dopynion.game.Game = None  # type: ignore[assignment]
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
        self.eliminated = False
        self.nb_cards_in_hand_at_turn_start = 5
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
            logger.debug("go from action to buy")

    def _check_for_buy_to_adjust_transition(self) -> None:
        if not self.purchases_left:
            self.purchases_left = 0
            self.state_machine = State.ADJUST
            logger.debug("go from buy to adjust")

    def start_turn(self) -> None:
        logger.debug("start turn (%s, %d)", self.name, id(self))
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
        logger.debug("end turn")

    def take_one_card_from_deck(self) -> CardName | None:
        if not self.deck:
            self.discard.empty_to(self.deck)
            self.deck.shuffle()
        if not self.deck:
            return None
        return self.deck.pop(0)

    def _adjust(self) -> None:
        self.played_cards.empty_to(self.discard)
        self.hand.empty_to(self.discard)
        for _ in range(self.nb_cards_in_hand_at_turn_start):
            card_name = self.take_one_card_from_deck()
            if card_name is not None:
                self.hand.append(card_name)
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
        logger.debug("> BUY %s", card_name)
        self.game.record.add_action(f"BUY {card_name}", self)
        if not self.purchases_left:
            msg = "No more buy available"
            self.game.record.add_error(msg, self)
            raise InvalidBuyError(msg)
        quantity = getattr(self.game.stock, card_name + "_qty")
        if not quantity:
            self.game.record.add_error(f"Invalid buy, no {card_name} in stock", self)
            raise InvalidBuyError(card_name)
        card = Card.types[card_name]
        if self.money + self.hand.money < card.cost:
            self.game.record.add_error("Invalid buy, not enough money", self)
            raise NotEnoughMoneyError
        self._prepare_money(card.cost)
        self.money -= card.cost
        self.game.stock.remove(card_name)
        self.discard.append(card_name)
        self.purchases_left -= 1
        self._check_for_buy_to_adjust_transition()

    def action(self, card_name: CardName) -> None:
        logger.debug("> ACTION %s", card_name)
        self.game.record.add_action(f"ACTION {card_name}", self)
        if self.state_machine != State.ACTION:
            logger.debug("actions_left %d", self.actions_left)
            logger.debug(self.state_machine.name)
            logger.debug(self.state)
            self.game.record.add_error("Tried action during buy phase", self)
            raise ActionDuringBuyError(card_name)
        if card_name not in self.hand:
            logger.debug(self.state)
            self.game.record.add_error(f"Invalid action, {card_name} not in hand", self)
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
        if self.playing and not self.eliminated:
            state.hand = self.hand.state
        return state

    def eliminate(self) -> None:
        self.eliminated = True
        self.game.record.add_error("Elimination", self)

    def score(self) -> dict:
        cards = self.hand + self.discard + self.deck
        if self.eliminated:
            return {"score": -10000}
        return {
            "colony_qty": cards.colony_qty,
            "province_qty": cards.province_qty,
            "duchy_qty": cards.duchy_qty,
            "estate_qty": cards.estate_qty,
            "curse_qty": cards.curse_qty,
            "gardens_qty": cards.gardens_qty,
            "score": sum(Card.types[card_name].victory_points for card_name in cards)
            + cards.gardens_qty * (len(cards) // 10),
        }

    def discard_one_card_from_hand(self, card_name: CardName) -> None:
        if card_name not in self.hand:
            msg = f"{card_name} not in player hand"
            self.game.record.add_error("Invalid discard, " + msg, self)
            raise InvalidDiscardError(msg)
        self.hand.remove(card_name)
        self.discard.append(card_name)

    def other_players(self) -> Generator[Player, None, None]:
        for other_player in self.game.players:
            if other_player != self and not other_player.eliminated:
                yield other_player
