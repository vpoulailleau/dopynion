from __future__ import annotations

import inspect
import random
import sys
from collections import defaultdict
from enum import StrEnum
from typing import TYPE_CHECKING, ClassVar

from dopynion.data_model import Cards

if TYPE_CHECKING:
    from collections.abc import Callable

    from dopynion.player import Player


class CardName(StrEnum):  # Create with a metaclass
    COPPER = "copper"
    COUNCILROOM = "councilroom"
    CURSE = "curse"
    DUCHY = "duchy"
    ESTATE = "estate"
    FESTIVAL = "festival"
    GOLD = "gold"
    LABORATORY = "laboratory"
    MARKET = "market"
    PROVINCE = "province"
    SILVER = "silver"
    SMITHY = "smithy"
    VILLAGE = "village"
    WOODCUTTER = "woodcutter"

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

    def __init_subclass__(cls) -> None:
        Card.types[CardName[cls.__name__.upper()]] = cls

    def __eq__(self, other: object) -> bool:
        return isinstance(self, other) or self.__class__ is other

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return self.name

    @classmethod
    def action(cls, player: Player) -> None:
        raise NotImplementedError


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

    @classmethod
    def action(cls, player: Player) -> None:
        for _ in range(4):
            player.hand.append(player.take_one_card_from_deck())
        player.purchases_left += 1


class Curse(Card):
    name = "Malédiction"
    cost = 0
    is_kingdom = False


class Duchy(Card):
    name = "Duché"
    cost = 5
    is_kingdom = False


class Estate(Card):
    name = "Domaine"
    cost = 2
    is_kingdom = False


class Festival(Card):
    name = "Festival"
    cost = 5
    is_action = True

    @classmethod
    def action(cls, player: Player) -> None:
        player.actions_left += 2
        player.purchases_left += 1
        player.money += 2


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

    @classmethod
    def action(cls, player: Player) -> None:
        for _ in range(2):
            player.hand.append(player.take_one_card_from_deck())
        player.actions_left += 1


class Market(Card):
    name = "Marché"
    cost = 5
    is_action = True

    @classmethod
    def action(cls, player: Player) -> None:
        player.hand.append(player.take_one_card_from_deck())
        player.actions_left += 1
        player.purchases_left += 1
        player.money += 1


class Province(Card):
    name = "Province"
    cost = 8
    is_kingdom = False


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

    @classmethod
    def action(cls, player: Player) -> None:
        for _ in range(3):
            player.hand.append(player.take_one_card_from_deck())


class Village(Card):
    name = "Village"
    cost = 3
    is_action = True

    @classmethod
    def action(cls, player: Player) -> None:
        player.hand.append(player.take_one_card_from_deck())
        player.actions_left += 2


class Woodcutter(Card):
    name = "Bucheron"
    cost = 3
    is_action = True

    @classmethod
    def action(cls, player: Player) -> None:
        player.purchases_left += 1
        player.money += 2


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

    def append(self, card_name: CardName) -> None:
        self._cards.append(card_name)
        self._quantities[card_name] += 1

    def append_several(self, qty: int, card_name: CardName) -> None:
        for _ in range(qty):
            self.append(card_name)

    def remove(self, card_name: CardName) -> None:
        self._quantities[card_name] -= 1
        self._cards.remove(card_name)

    def shuffle(self) -> None:
        random.shuffle(self._cards)

    def contains_action(self) -> bool:
        return any(
            card_name in actions_card_name
            for card_name, qty in self._quantities.items()
            if qty > 0
        )

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
