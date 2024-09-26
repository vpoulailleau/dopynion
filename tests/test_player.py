from dopynion import Copper, Estate, Player


def test_initial_deck() -> None:
    player = Player("Toto")
    assert len(player.deck) == 10
    assert sum(card == Copper for card in player.deck) == 7
    assert sum(card == Estate for card in player.deck) == 3
