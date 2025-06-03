import inspect
import operator
import random
from collections.abc import Callable
from pathlib import Path

import dopynion.cards
from dopynion.cards import Card, CardContainer, CardName
from dopynion.constants import MAX_NB_PLAYERS
from dopynion.data_model import Game as GameData
from dopynion.exceptions import (
    AddPlayerDuringGameError,
    InvalidCommandError,
)
from dopynion.player import Player


class Game:
    def __init__(self, record_factory: Callable) -> None:
        self.record = record_factory()
        self.players: list[Player] = []
        self.started = False
        self.stock = CardContainer()
        self.stock.append_several(12, CardName.PLATINUM)
        self.stock.append_several(30, CardName.GOLD)
        self.stock.append_several(40, CardName.SILVER)
        self.stock.append_several(60, CardName.COPPER)
        self.stock.append_several(12, CardName.ESTATE)
        self.stock.append_several(12, CardName.DUCHY)
        self.stock.append_several(12, CardName.PROVINCE)
        self.stock.append_several(12, CardName.COLONY)
        self.stock.append_several(30, CardName.CURSE)

    def __getattr__(self, name: str) -> int:
        if name.endswith("_qty"):
            return getattr(self.stock, name)
        raise AttributeError

    def add_player(self, player: Player) -> None:
        if self.started:
            raise AddPlayerDuringGameError
        if len(self.players) < MAX_NB_PLAYERS:
            self.players.append(player)
            player.game = self
            self.copper_qty -= 7  # type: ignore[attr-defined]
        else:
            msg = f"At most {MAX_NB_PLAYERS} players"
            raise InvalidCommandError(msg)

    def start(self) -> None:
        self.started = True
        if len(self.players) <= 2:  # noqa: PLR2004
            self.estate_qty = 8
            self.duchy_qty = 8
            self.province_qty = 8
            self.colony_qty = 8
            self.curse_qty = 10
        elif len(self.players) == 3:  # noqa: PLR2004
            self.curse_qty = 20
        elif len(self.players) == 4:  # noqa: PLR2004
            self.curse_qty = 30
        possible_kingdoms: list[CardName] = [
            CardName[name.upper()]
            for name, class_ in inspect.getmembers(dopynion.cards, inspect.isclass)
            if issubclass(class_, Card)
            and class_.name != "Unknown"
            and class_.is_kingdom
        ]
        for _ in range(10):
            card_name = random.choice(possible_kingdoms)  # noqa: S311
            if card_name == CardName.GARDENS:
                self.stock.append_several(self.duchy_qty, card_name)
            else:
                self.stock.append_several(10, card_name)
            possible_kingdoms.remove(card_name)
        self.record.add_stock(self.stock.state)
        self.save()

    @property
    def finished(self) -> bool:
        return (
            (self.stock.province_qty == 0)
            or (self.stock.colony_qty == 0)
            or self.stock.three_empty_piles
        )

    @property
    def state(self) -> GameData:
        return GameData(
            finished=self.finished,
            players=[player.state for player in self.players],
            stock=self.stock.state,
        )

    def score(self) -> dict:
        ret: dict = {player.name: player.score() for player in self.players}
        leaderboard = [
            (player.name, ret[player.name]["score"])
            for player in reversed(self.players)
        ]
        leaderboard.sort(key=operator.itemgetter(1), reverse=True)
        ret["leaderboard"] = leaderboard
        return ret

    def save(self) -> Path:
        return self.record.save(self.state)
