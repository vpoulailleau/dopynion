import pytest

from dopynion.cards import CardName, Village
from dopynion.player import Player


def test_adventurer(player_with_action_card: Player) -> None:
    player = player_with_action_card

    # hand building
    while player.hand:
        player.hand.pop()
    player.hand.append_several(5, CardName.ADVENTURER)

    # deck building
    while player.deck:
        player.deck.pop()
    player.deck.append(CardName.ADVENTURER)
    player.deck.append(CardName.BUREAUCRAT)
    player.deck.append(CardName.GOLD)
    player.deck.append(CardName.COUNCILROOM)
    player.deck.append(CardName.CURSE)
    player.deck.append(CardName.SILVER)
    player.deck.append(CardName.DUCHY)
    player.deck.append(CardName.ESTATE)
    player.deck.append(CardName.COPPER)
    player.deck.append(CardName.SMITHY)

    player.start_turn()

    player.action(CardName.ADVENTURER)

    assert player.discard[0] == CardName.ADVENTURER
    assert player.discard[1] == CardName.BUREAUCRAT
    assert player.discard[2] == CardName.COUNCILROOM
    assert player.discard[3] == CardName.CURSE
    assert len(player.discard) == 4
    assert CardName.GOLD in player.hand
    assert CardName.SILVER in player.hand
    assert CardName.COPPER not in player.hand


@pytest.mark.parametrize(
    ("card_name", "more_purchase", "more_actions", "more_money", "more_cards"),
    [
        (CardName.COUNCILROOM, 1, 0, 0, 4),
        (CardName.FESTIVAL, 1, 2, 2, 0),
        (CardName.LABORATORY, 0, 1, 0, 2),
        (CardName.MARKET, 1, 1, 1, 1),
        (CardName.SMITHY, 0, 0, 0, 3),
        (CardName.VILLAGE, 0, 2, 0, 1),
        (CardName.WOODCUTTER, 1, 0, 2, 0),
    ],
)
def test_basic_cards(  # noqa: PLR0913, PLR0917
    player_with_action_card: Player,
    card_name: CardName,
    more_purchase: int,
    more_actions: int,
    more_money: int,
    more_cards: int,
) -> None:
    player = player_with_action_card
    player.hand.append(card_name)
    player.start_turn()
    old_purchases_left = player.purchases_left
    old_actions_left = player.actions_left
    old_money = player.money
    old_nb_cards = len(player.hand)

    player.action(card_name)

    assert player.purchases_left == old_purchases_left + more_purchase
    assert player.actions_left == (old_actions_left - 1) + more_actions
    assert player.money == old_money + more_money
    assert len(player.hand) == (old_nb_cards - 1) + more_cards


def test_card_coverage() -> None:
    card = Village()
    print(card, card == Village, hash(card))
