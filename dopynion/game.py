from dopynion import InvalidCommandError
from dopynion.constants import MAX_NB_PLAYERS
from dopynion.player import Player


class Game:
    def __init__(self) -> None:
        self.players: list[Player] = []

    def add_player(self, player: Player) -> None:
        if len(self.players) < MAX_NB_PLAYERS:
            self.players.append(player)
        else:
            msg = f"At most {MAX_NB_PLAYERS} players"
            raise InvalidCommandError(msg)
