from __future__ import annotations


class Card:
    name = "Unknown"
    is_kingdom = True

    def __eq__(self, other: object) -> bool:
        return isinstance(self, other) or self.__class__ is other

    def __hash__(self) -> int:
        return hash(self.name)


class Copper:
    name = "Cuivre"
    is_kingdom = False


class Curse:
    name = "Malédiction"
    is_kingdom = False


class Duchy:
    name = "Duché"
    is_kingdom = False


class Estate:
    name = "Domaine"
    is_kingdom = False


class Gold:
    name = "Or"
    is_kingdom = False


class Province:
    name = "Province"
    is_kingdom = False


class Silver:
    name = "Argent"
    is_kingdom = False
