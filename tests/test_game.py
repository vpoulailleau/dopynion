import pytest

from dopynion import Game, InvalidCommandError, Player


def test_can_add_player() -> None:
    game = Game()
    game.add_player(Player("player 1"))
    assert len(game.players) == 1


def test_max_nb_players() -> None:
    game = Game()
    game.add_player(Player("1"))
    game.add_player(Player("2"))
    game.add_player(Player("3"))
    game.add_player(Player("4"))
    with pytest.raises(InvalidCommandError):
        game.add_player(Player("5"))
