from dopynion import Game, Player


def test_can_add_player() -> None:
    game = Game()
    game.add_player(Player("player 1"))
    assert len(game.players) == 1
