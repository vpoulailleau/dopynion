import pytest

from dopynion.cards import CardName
from dopynion.exceptions import (
    ActionDuringBuyError,
    InvalidActionError,
    InvalidDiscardError,
)
from dopynion.player import Player


def test_initial_deck(player: Player) -> None:
    assert len(player.deck) + len(player.hand) == 10
    assert player.deck.copper_qty + player.hand.copper_qty == 6
    assert player.deck.cursedgold_qty + player.hand.cursedgold_qty == 1
    assert player.deck.estate_qty + player.hand.estate_qty == 3


def test_make_hand_enough_cards_in_deck(player: Player) -> None:
    assert len(player.hand) == 5
    assert len(player.deck) == 5


def test_make_hand_not_enough_cards_in_deck() -> None:
    pass  # TODO add the test


def test_unknown_action(player_with_action_card: Player) -> None:
    player = player_with_action_card
    player.start_turn()
    with pytest.raises(InvalidActionError):
        player.action("FooBar")  # type: ignore[arg-type]


def test_invalid_action(player: Player) -> None:
    player.start_turn()
    with pytest.raises(ActionDuringBuyError):
        player.action(CardName.SMITHY)


def test_invalid_action_when_no_corresponding_card(
    player_with_action_card: Player,
) -> None:
    player = player_with_action_card
    player.start_turn()
    with pytest.raises(InvalidActionError):
        player.action(CardName.VILLAGE)


def test_discard_invalid_card(empty_player: Player) -> None:
    player = empty_player
    player.hand.append_several(5, CardName.CELLAR)
    player.start_turn()

    with pytest.raises(InvalidDiscardError):
        player.discard_one_card_from_hand(CardName.VILLAGE)


def test_discard_valid_card(empty_player: Player) -> None:
    player = empty_player
    player.hand.append_several(5, CardName.CELLAR)
    player.start_turn()

    player.discard_one_card_from_hand(CardName.CELLAR)

    assert len(player.discard) == 1
    assert len(player.hand) == 4
