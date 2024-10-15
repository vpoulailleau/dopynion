import inspect
import operator
import random

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
    def __init__(self) -> None:
        self.players: list[Player] = []
        self.started = False
        self.stock = CardContainer()
        self.stock.append_several(30, CardName.GOLD)
        self.stock.append_several(40, CardName.SILVER)
        self.stock.append_several(60, CardName.COPPER)
        self.stock.append_several(12, CardName.ESTATE)
        self.stock.append_several(12, CardName.DUCHY)
        self.stock.append_several(12, CardName.PROVINCE)
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
            self.copper_qty -= 7
        else:
            msg = f"At most {MAX_NB_PLAYERS} players"
            raise InvalidCommandError(msg)

    def start(self) -> None:
        self.started = True
        if len(self.players) <= 2:  # noqa: PLR2004
            self.estate_qty = 8
            self.duchy_qty = 8
            self.province_qty = 8
            self.curse_qty = 10
        elif len(self.players) == 3:  # noqa: PLR2004
            self.curse_qty = 20
        possible_kingdoms: list[CardName] = [
            name.lower()
            for name, class_ in inspect.getmembers(dopynion.cards, inspect.isclass)
            if issubclass(class_, Card)
            and class_.name != "Unknown"
            and class_.is_kingdom
        ]
        for _ in range(10):
            if not possible_kingdoms:
                break  # TODO à virer quand on aura plus de 10 possibles
            card_name = random.choice(possible_kingdoms)  # noqa: S311
            self.stock.append_several(10, card_name)
            # TODO pour jardin c'est particulier, cf bas de la page 2
            possible_kingdoms.remove(card_name)

    @property
    def finished(self) -> bool:
        return (self.stock.province_qty == 0) or self.stock.three_empty_piles

    @property
    def state(self) -> GameData:
        return GameData(
            finished=self.finished,
            players=[player.state for player in self.players],
            stock=self.stock.state,
        )

    def score(self) -> dict:
        ret = {player.name: player.score() for player in self.players}
        leaderboard = [
            (player.name, ret[player.name]["score"])
            for player in reversed(self.players)
        ]
        leaderboard.sort(key=operator.itemgetter(1), reverse=True)
        ret["leaderboard"] = leaderboard
        return ret
