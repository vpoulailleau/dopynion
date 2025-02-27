import pytest

from dopynion.cards import CardName
from dopynion.exceptions import (
    ActionDuringBuyError,
    InvalidActionError,
)
from dopynion.game import Game
from dopynion.player import Player, State


def test_initial_deck() -> None:
    player = Player("Toto")
    assert len(player.deck) + len(player.hand) == 10
    assert player.deck.copper_qty + player.hand.copper_qty == 7
    assert player.deck.estate_qty + player.hand.estate_qty == 3


def test_make_hand_enough_cards_in_deck() -> None:
    player = Player("toto")
    assert len(player.hand) == 5
    assert len(player.deck) == 5


def test_make_hand_not_enough_cards_in_deck() -> None:
    pass  # TODO add the test


def test_unknown_action(game: Game) -> None:
    player = Player("toto")
    game.add_player(player)
    player.start_turn()
    player.state_machine = State.ACTION
    with pytest.raises(InvalidActionError):
        player.action("FooBar")


def test_invalid_action(game: Game) -> None:
    player = Player("toto")
    game.add_player(player)
    player.start_turn()
    with pytest.raises(ActionDuringBuyError):
        player.action(CardName.SMITHY)


def test_invalid_action_when_no_corresponding_card(game: Game) -> None:
    player = Player("toto")
    game.add_player(player)
    player.start_turn()
    player.state_machine = State.ACTION
    with pytest.raises(InvalidActionError):
        player.action(CardName.VILLAGE)
