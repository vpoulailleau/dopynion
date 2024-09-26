from dopynion.cards import Copper, Duchy, Estate, Gold, Province, Silver
from dopynion.constants import MAX_NB_PLAYERS
from dopynion.exceptions import AddPlayerDuringGameError, InvalidCommandError
from dopynion.player import Player


class Game:
    def __init__(self) -> None:
        self.players: list[Player] = []
        self.started = False
        self.golds: list[type[Gold]] = [Gold] * 30
        self.silvers: list[type[Silver]] = [Silver] * 40
        self.coppers: list[type[Copper]] = [Copper] * 60
        self.estates: list[type[Estate]] = [Estate] * 12
        self.duchies: list[type[Duchy]] = [Duchy] * 12
        self.provinces: list[type[Province]] = [Province] * 12

    def add_player(self, player: Player) -> None:
        if self.started:
            raise AddPlayerDuringGameError
        if len(self.players) < MAX_NB_PLAYERS:
            self.players.append(player)
            self.coppers = self.coppers[7:]
        else:
            msg = f"At most {MAX_NB_PLAYERS} players"
            raise InvalidCommandError(msg)

    def start(self) -> None:
        self.started = True
        if len(self.players) <= 2:  # noqa: PLR2004
            self.estates = self.estates[:8]
            self.duchies = self.duchies[:8]
            self.provinces = self.provinces[:8]
