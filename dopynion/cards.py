from __future__ import annotations

from typing import ClassVar


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
