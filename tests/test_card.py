from dopynion.cards import CardName
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


def test_festival(player_with_action_card: Player) -> None:
    player = player_with_action_card
    player.hand.append(CardName.FESTIVAL)
    player.start_turn()
    old_purchases_left = player.purchases_left
    old_actions_left = player.actions_left
    old_money = player.money

    player.action(CardName.FESTIVAL)

    assert player.purchases_left == old_purchases_left + 1
    assert player.actions_left == (old_actions_left - 1) + 2
    assert player.money == old_money + 2
