from __future__ import annotations

import inspect
import random
import sys
from collections import defaultdict
from enum import StrEnum
from typing import ClassVar


class CardName(StrEnum):  # Create with a metaclass
    COPPER = "copper"
    CURSE = "curse"
    DUCHY = "duchy"
    ESTATE = "estate"
    GOLD = "gold"
    PROVINCE = "province"
    SILVER = "silver"
    SMITHY = "smithy"
    VILLAGE = "village"


class ClassNameRepr(type):
    def __repr__(cls) -> str:
        return cls.__name__


class Card(metaclass=ClassNameRepr):
    types: ClassVar[dict[str, type[Card]]] = {}
    name = "Unknown"
    cost = 10_000
    money = 0
    is_action = False
    is_kingdom = True
    is_money = False

    def __init_subclass__(cls) -> None:
        Card.types[cls.__name__.lower()] = cls

    def __eq__(self, other: object) -> bool:
        return isinstance(self, other) or self.__class__ is other

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return self.name


class Copper(Card):
    name = "Cuivre"
    money = 1
    is_kingdom = False
    is_money = True


class Curse(Card):
    name = "Malédiction"
    is_kingdom = False


class Duchy(Card):
    name = "Duché"
    is_kingdom = False


class Estate(Card):
    name = "Domaine"
    is_kingdom = False


class Gold(Card):
    name = "Or"
    money = 3
    is_kingdom = False
    is_money = True


class Province(Card):
    name = "Province"
    is_kingdom = False


class Silver(Card):
    name = "Argent"
    money = 2
    is_kingdom = False
    is_money = True


class Smithy(Card):
    name = "Forgeron"
    is_action = True


actions_card_name: list[CardName] = [
    name.lower()
    for name, class_ in inspect.getmembers(sys.modules[__name__], inspect.isclass)
    if issubclass(class_, Card) and class_.name != "Unknown" and class_.is_action
]


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

    def contains_money(self) -> bool:
        return any(
            card_name in {CardName.COPPER, CardName.SILVER, CardName.GOLD}
            for card_name, qty in self._quantities.items()
            if qty > 0
        )

    def pop(self, index: int = -1) -> CardName:
        card_name = self._cards.pop(index)
        self._quantities[card_name] -= 1
        return card_name

    def __contains__(self, card_name: CardName) -> bool:
        return self._quantities.get(card_name, 0) > 0

    def __len__(self) -> int:
        return len(self._cards)
