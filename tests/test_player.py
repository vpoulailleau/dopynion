import pytest

from dopynion.cards import Copper, Estate
from dopynion.exceptions import UnknownActionError
from dopynion.player import Player


def test_initial_deck() -> None:
    player = Player("Toto")
    assert len(player.deck) == 10
    assert sum(card == Copper for card in player.deck) == 7
    assert sum(card == Estate for card in player.deck) == 3


def test_make_hand_enough_cards_in_deck() -> None:
    player = Player("toto")
    player.start_turn()
    assert len(player.hand) == 5
    assert len(player.deck) == 5


def test_make_hand_not_enough_cards_in_deck() -> None:
    pass  # TODO add the test


def test_unknown_action() -> None:
    player = Player("toto")
    player.start_turn()
    with pytest.raises(UnknownActionError):
        player.action("FooBar")
