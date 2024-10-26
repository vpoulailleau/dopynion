import logging
from typing import TYPE_CHECKING

from dopynion.cards import Card, CardContainer, CardName
from dopynion.data_model import Player as PlayerData
from dopynion.exceptions import (
    ActionDuringBuyError,
    InvalidActionError,
    InvalidBuyError,
    NotEnoughMoneyError,
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
        self.purchases_left: int = 0
        self.money: int = 0
        self.playing = False
        self.state_machine = State.ACTION
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
        self.playing = True
        self.state_machine = State.ACTION
        self.actions_left = 1
        self.purchases_left = 1
        self.money = 0
        self._check_for_action_to_buy_transition()

    def end_turn(self) -> None:
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
        if self.state_machine != State.ACTION:
            logging.debug(self.state_machine)
            logging.debug("actions_left %d", self.actions_left)
            logging.debug(self.state)
            raise ActionDuringBuyError(card_name)
        if card_name not in self.hand:
            logging.debug(self.state)
            raise InvalidActionError(card_name)
        try:
            Card.types[card_name].action(self)
        except NotImplementedError as err:
            raise InvalidActionError(card_name) from err
        self.actions_left -= 1
        self.hand.remove(card_name)
        self.played_cards.append(card_name)
        self._check_for_action_to_buy_transition()

    @property
    def state(self) -> PlayerData:
        state = PlayerData(name=self.name, hand=None)
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
        # TODO garden
        ret["score"] = (
            ret["province_qty"] * 6
            + ret["duchy_qty"] * 3
            + ret["estate_qty"] * 1
            - ret["curse_qty"] * 1
        )
        return ret
