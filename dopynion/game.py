import inspect
import random

import dopynion.cards
from dopynion.cards import (
    Card,
    Copper,
    Curse,
    Duchy,
    Estate,
    Gold,
    Province,
    Silver,
)
from dopynion.constants import MAX_NB_PLAYERS
from dopynion.exceptions import (
    AddPlayerDuringGameError,
    InvalidCommandError,
    MissingCardError,
)
from dopynion.player import Player


class Game:
    def __init__(self) -> None:
        self.players: list[Player] = []
        self.started = False
        self.buyable_cards: dict[str, list[type[Card]]] = {
            "Gold": [Gold] * 30,
            "Silver": [Silver] * 40,
            "Copper": [Copper] * 60,
            "Estate": [Estate] * 12,
            "Duchy": [Duchy] * 12,
        }
        self.provinces: list[type[Province]] = [Province] * 12
        self.curses: list[type[Curse]] = [Curse] * 30
        self.kingdoms: dict[type[Card], int] = {}

    def add_player(self, player: Player) -> None:
        if self.started:
            raise AddPlayerDuringGameError
        if len(self.players) < MAX_NB_PLAYERS:
            self.players.append(player)
            player.game = self
            self.buyable_cards["Copper"] = self.buyable_cards["Copper"][7:]
        else:
            msg = f"At most {MAX_NB_PLAYERS} players"
            raise InvalidCommandError(msg)

    def start(self) -> None:
        self.started = True
        if len(self.players) <= 2:  # noqa: PLR2004
            self.buyable_cards["Estate"] = self.buyable_cards["Estate"][:8]
            self.buyable_cards["Duchy"] = self.buyable_cards["Duchy"][:8]
            self.provinces = self.provinces[:8]
            self.curses = self.curses[:10]
        elif len(self.players) == 3:  # noqa: PLR2004
            self.curses = self.curses[:20]
        possible_kingdoms: list[type[Card]] = [
            class_
            for _, class_ in inspect.getmembers(dopynion.cards, inspect.isclass)
            if issubclass(class_, Card)
            and class_.name != "Unknown"
            and class_.is_kingdom
        ]
        for _ in range(10):
            card_type = random.choice(possible_kingdoms)  # noqa: S311
            self.kingdoms[card_type] = 10
            # TODO pour jardin c'est particulier, cf bas de la page 2
            # TODO possible_kingdoms.remove(card_type)
        print(self.kingdoms)

    @staticmethod
    def move_card(index: int, src: list[type[Card]], dst: list[type[Card]]) -> None:
        dst.append(src.pop(index))

    @staticmethod
    def move_card_by_name(
        card_name: str,
        src: list[type[Card]],
        dst: list[type[Card]],
    ) -> None:
        for index, card in enumerate(src):
            if card.__name__ == card_name:
                Game.move_card(index, src, dst)
                break
        else:
            raise MissingCardError
