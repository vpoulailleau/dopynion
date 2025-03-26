from __future__ import annotations

import inspect
import logging
import random
import sys
from collections import defaultdict
from enum import StrEnum
from typing import TYPE_CHECKING, ClassVar, Final

from dopynion.data_model import Cards

if TYPE_CHECKING:
    from collections.abc import Callable

    from dopynion.player import Player

logger = logging.getLogger(__name__)


class CardName(StrEnum):  # Create with a metaclass
    ADVENTURER = "adventurer"
    BUREAUCRAT = "bureaucrat"
    CELLAR = "cellar"
    CHANCELLOR = "chancellor"
    CHAPEL = "chapel"
    COPPER = "copper"
    COUNCILROOM = "councilroom"
    CURSE = "curse"
    DUCHY = "duchy"
    ESTATE = "estate"
    FEAST = "feast"
    FESTIVAL = "festival"
    GARDENS = "gardens"
    GOLD = "gold"
    LABORATORY = "laboratory"
    LIBRARY = "library"
    MARKET = "market"
    MILITIA = "militia"
    MINE = "mine"
    MONEYLENDER = "moneylender"
    PROVINCE = "province"
    REMODEL = "remodel"
    SILVER = "silver"
    SMITHY = "smithy"
    VILLAGE = "village"
    WITCH = "witch"
    WOODCUTTER = "woodcutter"
    WORKSHOP = "workshop"

    def __repr__(self) -> str:
        return self.value.title()


class ClassNameRepr(type):
    def __repr__(cls) -> str:
        return cls.__name__


class Card(metaclass=ClassNameRepr):
    types: ClassVar[dict[CardName, type[Card]]] = {}
    name = "Unknown"
    cost = 10_000
    money = 0
    is_action = False
    is_kingdom = True
    is_money = False
    more_cards_from_deck = 0
    more_purchases = 0
    more_actions = 0
    more_money = 0
    victory_points = 0

    @classmethod
    def card_name(cls) -> CardName:
        return CardName[cls.__name__.upper()]

    def __init_subclass__(cls) -> None:
        Card.types[cls.card_name()] = cls

    def __eq__(self, other: object) -> bool:
        return isinstance(self, other) or self.__class__ is other

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return self.name

    @classmethod
    def action(cls, player: Player) -> None:
        for _ in range(cls.more_cards_from_deck):
            player.hand.append(player.take_one_card_from_deck())
        player.purchases_left += cls.more_purchases
        player.actions_left += cls.more_actions
        player.money += cls.more_money

        cls._action(player)

    @classmethod
    def _action(cls, player: Player) -> None:
        pass


class Adventurer(Card):
    name = "Aventurier"
    cost = 6
    is_action = True
    nb_treasure_cards = 2

    @classmethod
    def _action(cls, player: Player) -> None:
        nb_kept_cards = 0
        while nb_kept_cards < cls.nb_treasure_cards:
            card_name = player.take_one_card_from_deck()
            if Card.types[card_name].is_money:
                nb_kept_cards += 1
                player.hand.append(card_name)
            else:
                player.discard.append(card_name)


class Bureaucrat(Card):
    name = "Bureaucrate"
    cost = 4
    is_action = True

    @classmethod
    def _action(cls, player: Player) -> None:
        silver = Silver.card_name()
        if silver in player.game.stock:
            player.deck.prepend(silver)
            player.game.stock.remove(silver)
        for other_player in player.other_players():
            victory_cards = other_player.hand.victory_cards
            if victory_cards:
                other_player.deck.prepend(victory_cards[0])
                other_player.hand.remove(victory_cards[0])


class Cellar(Card):
    name = "Cave"
    cost = 2
    is_action = True
    more_actions = 1

    @classmethod
    def _action(cls, player: Player) -> None:
        nb_discarded_cards = 0
        for card_name in player.hand.copy():
            if player.hooks.confirm_discard_card_from_hand(
                card_name,
                list(player.hand),
            ):
                player.hand.remove(card_name)
                player.discard.append(card_name)
                nb_discarded_cards += 1
        for _ in range(nb_discarded_cards):
            player.hand.append(player.take_one_card_from_deck())


class Chancellor(Card):
    name = "Chancelier"
    cost = 3
    is_action = True
    more_money = 2

    @classmethod
    def _action(cls, player: Player) -> None:
        if player.hooks.confirm_discard_deck():
            player.deck.empty_to(player.discard)


class Chapel(Card):
    name = "Chapelle"
    cost = 2
    is_action = True
    max_discarded_cards: Final[int] = 4

    @classmethod
    def _action(cls, player: Player) -> None:
        nb_discarded_cards = 0
        for card_name in player.hand.copy():
            if player.hooks.confirm_discard_card_from_hand(
                card_name,
                list(player.hand),
            ):
                player.hand.remove(card_name)
                player.discard.append(card_name)
                nb_discarded_cards += 1
            if nb_discarded_cards >= cls.max_discarded_cards:
                break


class Copper(Card):
    name = "Cuivre"
    cost = 0
    money = 1
    is_kingdom = False
    is_money = True


class CouncilRoom(Card):
    name = "Chambre du conseil"
    cost = 5
    is_action = True
    more_cards_from_deck = 4
    more_purchases = 1

    @classmethod
    def _action(cls, player: Player) -> None:
        for other_player in player.other_players():
            other_player.hand.append(other_player.take_one_card_from_deck())


class Curse(Card):
    name = "Malédiction"
    cost = 0
    is_kingdom = False
    victory_points = -1


class Duchy(Card):
    name = "Duché"
    cost = 5
    is_kingdom = False
    victory_points = 3


class Estate(Card):
    name = "Domaine"
    cost = 2
    is_kingdom = False
    victory_points = 1


class Feast(Card):
    name = "Festin"
    cost = 4
    is_action = True
    max_new_card_cost: Final[int] = 5

    @classmethod
    def _action(cls, player: Player) -> None:
        player.played_cards.pop()
        possible_cards = [
            card_name
            for card_name in player.game.stock
            if player.game.stock.quantity(card_name)
            and Card.types[card_name].cost <= cls.max_new_card_cost
        ]
        if possible_cards:
            choosen_card_name = player.hooks.choose_card_to_receive_in_discard(
                possible_cards,
            )
            player.game.stock.remove(choosen_card_name)
            player.discard.append(choosen_card_name)


class Festival(Card):
    name = "Festival"
    cost = 5
    is_action = True
    more_purchases = 1
    more_actions = 2
    more_money = 2


class Gardens(Card):
    name = "Jardins"
    cost = 4
    is_kingdom = True


class Gold(Card):
    name = "Or"
    cost = 6
    money = 3
    is_kingdom = False
    is_money = True


class Laboratory(Card):
    name = "Laboratoire"
    cost = 5
    is_action = True
    more_cards_from_deck = 2
    more_actions = 1


class Library(Card):
    name = "Bibliothèque"
    cost = 5
    is_action = True
    target_hand_size: Final[int] = 7

    @classmethod
    def _action(cls, player: Player) -> None:
        skipped_cards = CardContainer()
        while len(player.hand) < cls.target_hand_size and (
            len(player.deck) + len(player.discard) > 0
        ):
            card_name = player.take_one_card_from_deck()
            if not Card.types[card_name].is_action:
                player.hand.append(card_name)
            elif player.hooks.skip_card_reception_in_hand(
                card_name,
                list(player.hand),
            ):
                skipped_cards.append(card_name)
            else:
                player.hand.append(card_name)
        skipped_cards.empty_to(player.discard)


class Market(Card):
    name = "Marché"
    cost = 5
    is_action = True
    more_cards_from_deck = 1
    more_purchases = 1
    more_actions = 1
    more_money = 1


class Militia(Card):
    name = "Milice"
    cost = 4
    is_action = True
    more_money = 2
    enemy_hand_size_left: Final[int] = 3

    @classmethod
    def _action(cls, player: Player) -> None:
        for other_player in player.other_players():
            while len(other_player.hand) > cls.enemy_hand_size_left:
                removed_card = other_player.hooks.discard_card_from_hand(
                    list(other_player.hand),
                )
                other_player.hand.remove(removed_card)


class Mine(Card):
    name = "Mine"
    cost = 5
    is_action = True

    @classmethod
    def _action(cls, player: Player) -> None:
        money_cards = list(set(player.hand.money_cards))
        trashed_card = player.hooks.trash_money_card_for_better_money_card(money_cards)
        if trashed_card is not None:
            player.hand.remove(trashed_card)
            possible_money_cards = [
                card_name
                for card_name in player.game.stock
                if (class_ := Card.types[card_name]).is_money
                and class_.cost <= Card.types[trashed_card].cost + 3
                and player.game.stock.quantity(card_name)
            ]
            if possible_money_cards:
                best_money = max(
                    possible_money_cards,
                    key=lambda card_name: Card.types[card_name].money,
                )
                player.hand.append(best_money)


class MoneyLender(Card):
    name = "Prêteur sur gages"
    cost = 4
    is_action = True

    @classmethod
    def _action(cls, player: Player) -> None:
        if player.hand.copper_qty >= 1 and player.hooks.confirm_discard_card_from_hand(
            CardName.COPPER,
            list(player.hand),
        ):
            player.hand.remove(CardName.COPPER)
            for _ in range(3):
                if player.game.stock.copper_qty:
                    player.game.stock.remove(CardName.COPPER)
                    player.hand.append(CardName.COPPER)


class Province(Card):
    name = "Province"
    cost = 8
    is_kingdom = False
    victory_points = 6


class Remodel(Card):
    name = "Rénovation"
    cost = 4
    is_action = True

    @classmethod
    def _action(cls, player: Player) -> None:
        if not player.hand:
            return
        thrashed_card = player.hooks.discard_card_from_hand(list(player.hand))
        player.hand.remove(thrashed_card)
        possible_cards = [
            card_name
            for card_name in player.game.stock
            if player.game.stock.quantity(card_name)
            and Card.types[card_name].cost <= Card.types[thrashed_card].cost + 2
        ]
        if possible_cards:
            choosen_card_name = player.hooks.choose_card_to_receive_in_discard(
                possible_cards,
            )
            player.game.stock.remove(choosen_card_name)
            player.discard.append(choosen_card_name)


class Silver(Card):
    name = "Argent"
    cost = 3
    money = 2
    is_kingdom = False
    is_money = True


class Smithy(Card):
    name = "Forgeron"
    cost = 4
    is_action = True
    more_cards_from_deck = 3


class Village(Card):
    name = "Village"
    cost = 3
    is_action = True
    more_cards_from_deck = 1
    more_actions = 2


class Witch(Card):
    name = "Sorcière"
    cost = 5
    is_action = True
    more_cards_from_deck = 2

    @classmethod
    def _action(cls, player: Player) -> None:
        for other_player in player.other_players():
            if player.game.stock.curse_qty:
                other_player.discard.append(CardName.CURSE)
                player.game.stock.remove(CardName.CURSE)


class Woodcutter(Card):
    name = "Bucheron"
    cost = 3
    is_action = True
    more_purchases = 1
    more_money = 2


class Workshop(Card):
    name = "Atelier"
    cost = 3
    is_action = True
    max_cost_of_received_card: Final[int] = 4

    @classmethod
    def _action(cls, player: Player) -> None:
        possible_cards = [
            card_name
            for card_name in player.game.stock
            if player.game.stock.quantity(card_name)
            and Card.types[card_name].cost <= cls.max_cost_of_received_card
        ]
        possible_cards = list(set(possible_cards))
        logger.debug(possible_cards)
        if possible_cards:
            choosen_card_name = player.hooks.choose_card_to_receive_in_discard(
                possible_cards,
            )
            player.game.stock.remove(choosen_card_name)
            player.discard.append(choosen_card_name)


actions_card_name: set[CardName] = {
    name.lower()
    for name, class_ in inspect.getmembers(sys.modules[__name__], inspect.isclass)
    if issubclass(class_, Card) and class_.name != "Unknown" and class_.is_action
}

money_card_name: set[CardName] = {CardName.COPPER, CardName.SILVER, CardName.GOLD}


class CardContainer:
    """Storage for card."""

    def __init__(self) -> None:
        self._quantities: dict[CardName, int] = defaultdict(int)
        self._cards: list[CardName] = []

    def __getattr__(self, attribute: str) -> int:
        if attribute.endswith("_qty"):
            card_name = attribute[:-4]
            return self._quantities[CardName[card_name.upper()]]
        raise AttributeError

    def __repr__(self) -> str:
        return str(self._cards)

    def __add__(self, other: CardContainer) -> CardContainer:
        ret = CardContainer()
        for card_name in self:
            ret.append(card_name)
        for card_name in other:
            ret.append(card_name)
        return ret

    def clear(self) -> None:
        self._quantities.clear()
        self._cards.clear()

    def copy(self) -> CardContainer:
        new = CardContainer()
        new._quantities = self._quantities.copy()  # noqa: SLF001
        new._cards = self._cards.copy()  # noqa: SLF001
        return new

    def prepend(self, card_name: CardName) -> None:
        """Insert next card to be played."""
        self._cards.insert(0, card_name)
        self._quantities[card_name] += 1

    def append(self, card_name: CardName) -> None:
        self._cards.append(card_name)
        self._quantities[card_name] += 1

    def append_several(self, qty: int, card_name: CardName) -> None:
        for _ in range(qty):
            self.append(card_name)

    def remove(self, card_name: CardName) -> None:
        self._cards.remove(card_name)
        self._quantities[card_name] -= 1

    def shuffle(self) -> None:
        random.shuffle(self._cards)

    def contains_action(self) -> bool:
        return any(
            card_name in actions_card_name
            for card_name, qty in self._quantities.items()
            if qty > 0
        )

    @property
    def victory_cards(self) -> CardContainer:
        ret = CardContainer()
        for card_name, qty in self._quantities.items():
            if Card.types[card_name].victory_points:
                ret.append_several(qty, card_name)
        return ret

    @property
    def action_cards(self) -> CardContainer:
        ret = CardContainer()
        for card_name, qty in self._quantities.items():
            if card_name in actions_card_name:
                ret.append_several(qty, card_name)
        return ret

    def contains_money(self) -> bool:
        return any(
            card_name in money_card_name
            for card_name, qty in self._quantities.items()
            if qty > 0
        )

    @property
    def money_cards(self) -> CardContainer:
        ret = CardContainer()
        for card_name, qty in self._quantities.items():
            if card_name in money_card_name:
                ret.append_several(qty, card_name)
        return ret

    @property
    def money(self) -> int:
        return (
            1 * self._quantities.get(CardName.COPPER, 0)
            + 2 * self._quantities.get(CardName.SILVER, 0)
            + 3 * self._quantities.get(CardName.GOLD, 0)
        )

    def pop(self, index: int = -1) -> CardName:
        card_name = self._cards.pop(index)
        self._quantities[card_name] -= 1
        return card_name

    def __contains__(self, card_name: CardName) -> bool:
        return self._quantities.get(card_name, 0) > 0

    def __len__(self) -> int:
        return len(self._cards)

    def __getitem__(self, index: int) -> CardName:
        return self._cards[index]

    def quantity(self, card_name: CardName) -> int:
        return self._quantities.get(card_name, 0)

    def sort(self, key: Callable, *, reverse: bool = False) -> None:
        self._cards.sort(key=key, reverse=reverse)

    def empty_to(self, other: CardContainer) -> None:
        while self:
            card_name = self.pop(0)
            other.append(card_name)
        self._quantities.clear()
        self._cards.clear()

    @property
    def three_empty_piles(self) -> bool:
        nb_piles = 3
        return sum(1 for qty in self._quantities.values() if qty == 0) >= nb_piles

    @property
    def state(self) -> Cards:
        return Cards(quantities=self._quantities.copy())
