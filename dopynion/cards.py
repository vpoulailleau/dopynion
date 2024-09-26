from __future__ import annotations

import inspect
import sys


class Card:
    name = "Unknown"
    is_kingdom = True

    def __eq__(self, other: object) -> bool:
        return isinstance(self, other) or self.__class__ is other

    def __hash__(self) -> int:
        return hash(self.name)


class Copper(Card):
    name = "Cuivre"
    is_kingdom = False


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
    is_kingdom = False


class Province(Card):
    name = "Province"
    is_kingdom = False


class Silver(Card):
    name = "Argent"
    is_kingdom = False


class Smithy(Card):
    name = "Forgeron"


kingdom_cards: list[type[Card]] = [
    class_
    for _, class_ in inspect.getmembers(sys.modules[__name__], inspect.isclass)
    if issubclass(class_, Card) and class_.name != "Unknown" and class_.is_kingdom
]
