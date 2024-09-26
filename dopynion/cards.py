from __future__ import annotations


class Card:
    name = "Unknown"

    def __eq__(self, other: object) -> bool:
        return isinstance(self, other) or self.__class__ is other

    def __hash__(self) -> int:
        return hash(self.name)


class Copper:
    name = "Cuivre"


class Duchy:
    name = "Duché"


class Estate:
    name = "Domaine"


class Gold:
    name = "Or"


class Province:
    name = "Province"


class Silver:
    name = "Argent"
