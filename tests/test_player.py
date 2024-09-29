import pytest

from dopynion.cards import Copper, Estate
from dopynion.exceptions import (
    ActionDuringBuyError,
    InvalidActionError,
    UnknownActionError,
)
from dopynion.player import Player, State


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
    player.state = State.ACTION
    with pytest.raises(UnknownActionError):
        player.action("FooBar")


def test_invalid_action() -> None:
    player = Player("toto")
    player.start_turn()
    with pytest.raises(ActionDuringBuyError):
        player.action("Smithy")


def test_invalid_action_when_no_corresponding_card() -> None:
    player = Player("toto")
    player.start_turn()
    player.state = State.ACTION
    with pytest.raises(InvalidActionError):
        player.action("Village")


def test_move_card() -> None:
    src = [Estate, Copper, Estate, Estate]
    dst = [Estate, Copper]
    Player.move_card(1, src, dst)
    assert src == [Estate, Estate, Estate]
    assert dst == [Estate, Copper, Copper]
