from dopynion.cards import CardName
from dopynion.player import Player


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
