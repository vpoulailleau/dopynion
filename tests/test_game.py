import pytest

from dopynion.exceptions import AddPlayerDuringGameError, InvalidCommandError
from dopynion.game import Game
from dopynion.player import Player


def test_can_add_player() -> None:
    game = Game()
    game.add_player(Player("player 1"))
    game.start()
    assert len(game.players) == 1


def test_cannot_add_player_on_started_game() -> None:
    game = Game()
    game.add_player(Player("player 1"))
    game.start()
    with pytest.raises(AddPlayerDuringGameError):
        game.add_player(Player("2"))


def test_max_nb_players() -> None:
    game = Game()
    game.add_player(Player("1"))
    game.add_player(Player("2"))
    game.add_player(Player("3"))
    game.add_player(Player("4"))
    with pytest.raises(InvalidCommandError):
        game.add_player(Player("5"))
    game.start()


def test_initial_money() -> None:
    game = Game()
    game.add_player(Player("1"))
    game.add_player(Player("2"))
    game.start()
    assert len(game.golds) == 30
    assert len(game.silvers) == 40
    assert len(game.coppers) == 60 - 7 * 2


def test_initial_estates_2_players() -> None:
    game = Game()
    game.add_player(Player("1"))
    game.add_player(Player("2"))
    game.start()
    assert len(game.estates) == 8
    assert len(game.duchies) == 8
    assert len(game.provinces) == 8


def test_initial_estates_3_players() -> None:
    game = Game()
    game.add_player(Player("1"))
    game.add_player(Player("2"))
    game.add_player(Player("3"))
    game.start()
    assert len(game.estates) == 12
    assert len(game.duchies) == 12
    assert len(game.provinces) == 12
