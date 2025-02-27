import pytest

from dopynion.game import Game
from dopynion.player import Player


@pytest.fixture(name="game")
def _game() -> Game:
    class TestRecord:
        def save(self) -> None:
            pass

        def start_turn(self) -> None:
            pass

        def add_action(self, action: str, player: Player) -> None:
            pass

    return Game(record_factory=TestRecord)


@pytest.fixture(name="player")
def _player(game: Game) -> Player:
    player = Player("toto")
    game.add_player(player)
    return player
