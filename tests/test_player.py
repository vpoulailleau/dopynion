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


# Tests for score calculation
def test_score_eliminated_player(empty_player: Player) -> None:
    """Score should be -10000 for eliminated player"""
    empty_player.eliminate()
    score_dict = empty_player.score()
    assert score_dict["score"] == -10000


def test_score_no_cards(empty_player: Player) -> None:
    """Score should be 0 when player has no cards"""
    score_dict = empty_player.score()
    assert score_dict["score"] == 0
    assert score_dict["colony_qty"] == 0
    assert score_dict["province_qty"] == 0
    assert score_dict["duchy_qty"] == 0
    assert score_dict["estate_qty"] == 0
    assert score_dict["curse_qty"] == 0
    assert score_dict["gardens_qty"] == 0


def test_score_single_province(empty_player: Player) -> None:
    """Province is worth 6 victory points"""
    empty_player.hand.append(CardName.PROVINCE)
    score_dict = empty_player.score()
    assert score_dict["province_qty"] == 1
    assert score_dict["score"] == 6


def test_score_single_duchy(empty_player: Player) -> None:
    """Duchy is worth 3 victory points"""
    empty_player.hand.append(CardName.DUCHY)
    score_dict = empty_player.score()
    assert score_dict["duchy_qty"] == 1
    assert score_dict["score"] == 3


def test_score_single_estate(empty_player: Player) -> None:
    """Estate is worth 1 victory point"""
    empty_player.hand.append(CardName.ESTATE)
    score_dict = empty_player.score()
    assert score_dict["estate_qty"] == 1
    assert score_dict["score"] == 1


def test_score_single_curse(empty_player: Player) -> None:
    """Curse is worth -1 victory point"""
    empty_player.hand.append(CardName.CURSE)
    score_dict = empty_player.score()
    assert score_dict["curse_qty"] == 1
    assert score_dict["score"] == -1


def test_score_single_colony(empty_player: Player) -> None:
    """Colony is worth 10 victory points"""
    empty_player.hand.append(CardName.COLONY)
    score_dict = empty_player.score()
    assert score_dict["colony_qty"] == 1
    assert score_dict["score"] == 10


def test_score_multiple_cards_in_hand(empty_player: Player) -> None:
    """Score should sum all victory points when cards are in hand"""
    empty_player.hand.append(CardName.PROVINCE)
    empty_player.hand.append(CardName.DUCHY)
    empty_player.hand.append(CardName.ESTATE)
    empty_player.hand.append(CardName.CURSE)
    score_dict = empty_player.score()
    # Province: 6, Duchy: 3, Estate: 1, Curse: -1 = 9
    assert score_dict["score"] == 9
    assert score_dict["province_qty"] == 1
    assert score_dict["duchy_qty"] == 1
    assert score_dict["estate_qty"] == 1
    assert score_dict["curse_qty"] == 1


def test_score_cards_distributed_across_containers(empty_player: Player) -> None:
    """Score should count cards from hand, deck, discard, and played_cards"""
    empty_player.hand.append(CardName.PROVINCE)
    empty_player.deck.append(CardName.DUCHY)
    empty_player.discard.append(CardName.ESTATE)
    empty_player.played_cards.append(CardName.CURSE)
    score_dict = empty_player.score()
    # Province: 6, Duchy: 3, Estate: 1, Curse: -1 = 9
    assert score_dict["score"] == 9


def test_score_multiple_same_card(empty_player: Player) -> None:
    """Score should handle multiple copies of the same card"""
    empty_player.hand.append_several(3, CardName.PROVINCE)
    score_dict = empty_player.score()
    assert score_dict["province_qty"] == 3
    assert score_dict["score"] == 18  # 3 * 6


def test_score_gardens_bonus_zero(empty_player: Player) -> None:
    """Gardens should give 0 bonus when total cards < 10"""
    empty_player.hand.append(CardName.GARDENS)
    empty_player.hand.append_several(5, CardName.COPPER)
    score_dict = empty_player.score()
    # 6 total cards, 6 // 10 = 0, so no bonus
    assert score_dict["gardens_qty"] == 1
    assert score_dict["score"] == 0  # 0 (gardens) + 0 bonus


def test_score_gardens_bonus_one_per_ten(empty_player: Player) -> None:
    """Gardens should give 1 point per 10 cards"""
    empty_player.hand.append(CardName.GARDENS)
    empty_player.hand.append_several(9, CardName.COPPER)
    # Total: 10 cards, 10 // 10 = 1, so 1 bonus per garden
    score_dict = empty_player.score()
    assert score_dict["gardens_qty"] == 1
    assert score_dict["score"] == 1  # 0 (gardens victory points) + 1 * 1 (bonus)


def test_score_gardens_bonus_two(empty_player: Player) -> None:
    """Gardens should give 2 points when total cards = 20"""
    empty_player.hand.append(CardName.GARDENS)
    empty_player.hand.append_several(19, CardName.COPPER)
    # Total: 20 cards, 20 // 10 = 2
    score_dict = empty_player.score()
    assert score_dict["gardens_qty"] == 1
    assert score_dict["score"] == 2


def test_score_multiple_gardens(empty_player: Player) -> None:
    """Multiple gardens should each get the bonus"""
    empty_player.hand.append_several(2, CardName.GARDENS)
    empty_player.hand.append_several(18, CardName.COPPER)
    # Total: 20 cards, 20 // 10 = 2, 2 gardens * 2 = 4
    score_dict = empty_player.score()
    assert score_dict["gardens_qty"] == 2
    assert score_dict["score"] == 4


def test_score_fairgrounds_bonus_zero(empty_player: Player) -> None:
    """Fairgrounds should give 0 bonus when < 5 different card types"""
    empty_player.hand.append(CardName.FAIRGROUNDS)
    empty_player.hand.append_several(4, CardName.COPPER)
    # 2 types (Fairgrounds + Copper), 2 // 5 = 0
    score_dict = empty_player.score()
    assert score_dict["score"] == 0


def test_score_fairgrounds_bonus_one(empty_player: Player) -> None:
    """Fairgrounds should give 1 point per 5 different card types"""
    empty_player.hand.append(CardName.FAIRGROUNDS)
    empty_player.hand.append(CardName.COPPER)
    empty_player.hand.append(CardName.SILVER)
    empty_player.hand.append(CardName.GOLD)
    empty_player.hand.append(CardName.PROVINCE)
    # 5 types: Fairgrounds, Copper, Silver, Gold, Province
    # 5 // 5 = 1
    score_dict = empty_player.score()
    assert score_dict["score"] == 6 + 1  # Province (6) + fairgrounds bonus (1)


def test_score_fairgrounds_bonus_two(empty_player: Player) -> None:
    """Fairgrounds should give 2 points when 10+ different card types"""
    empty_player.hand.append(CardName.FAIRGROUNDS)
    # Add 9 other different cards
    empty_player.hand.append(CardName.COPPER)
    empty_player.hand.append(CardName.SILVER)
    empty_player.hand.append(CardName.GOLD)
    empty_player.hand.append(CardName.PROVINCE)
    empty_player.hand.append(CardName.DUCHY)
    empty_player.hand.append(CardName.ESTATE)
    empty_player.hand.append(CardName.CURSE)
    empty_player.hand.append(CardName.VILLAGE)
    empty_player.hand.append(CardName.SMITHY)
    # 10 types total
    # 10 // 5 = 2
    score_dict = empty_player.score()
    expected = (
        6 + 3 + 1 + (-1) + 2
    )  # Province + Duchy + Estate + Curse + fairgrounds bonus
    assert score_dict["score"] == expected


def test_score_combined_gardens_and_fairgrounds(empty_player: Player) -> None:
    """Test score with both gardens and fairgrounds bonuses"""
    empty_player.hand.append(CardName.GARDENS)
    empty_player.hand.append(CardName.FAIRGROUNDS)
    empty_player.hand.append(CardName.PROVINCE)
    # Add 7 more different cards to reach 10 types and 10+ total cards
    empty_player.hand.append(CardName.COPPER)
    empty_player.hand.append(CardName.SILVER)
    empty_player.hand.append(CardName.GOLD)
    empty_player.hand.append(CardName.DUCHY)
    empty_player.hand.append(CardName.ESTATE)
    empty_player.hand.append(CardName.CURSE)
    empty_player.hand.append(CardName.VILLAGE)
    empty_player.hand.append_several(2, CardName.SMITHY)
    # Total cards: 12, types: 10 (Smithy counted once)
    # Gardens bonus: 12 // 10 = 1
    # Fairgrounds bonus: 10 // 5 = 2
    # Victory points: Province (6) + Duchy (3) + Estate (1) + Curse (-1) = 9
    # Total: 9 + 1 + 2 = 12
    score_dict = empty_player.score()
    assert score_dict["gardens_qty"] == 1
    assert score_dict["score"] == 12
