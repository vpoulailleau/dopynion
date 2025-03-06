import pytest

from dopynion.cards import CardContainer, CardName, Village
from dopynion.game import Game
from dopynion.player import DefaultPlayerHooks, Player


def test_adventurer(empty_player: Player) -> None:
    player = empty_player

    player.hand.append_several(5, CardName.ADVENTURER)

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


def test_bureaucrat_enemy_with_victory_cards(
    game_with_two_players: tuple[Game, Player, Player],
) -> None:
    _, player, enemy = game_with_two_players

    player.hand.clear()
    player.hand.append_several(5, CardName.BUREAUCRAT)

    enemy.deck.clear()
    enemy.hand.clear()
    enemy.hand.append_several(5, CardName.DUCHY)

    player.start_turn()

    player.action(CardName.BUREAUCRAT)

    assert len(enemy.hand) == 4
    assert enemy.deck[0] == CardName.DUCHY


def test_bureaucrat_enemy_without_victory_cards(
    game_with_two_players: tuple[Game, Player, Player],
) -> None:
    _, player, enemy = game_with_two_players

    player.hand.clear()
    player.hand.append_several(5, CardName.BUREAUCRAT)

    enemy.deck.clear()
    enemy.hand.clear()
    enemy.hand.append_several(5, CardName.GOLD)

    player.start_turn()

    player.action(CardName.BUREAUCRAT)

    assert len(enemy.hand) == 5
    assert not enemy.deck


def test_bureaucrat_with_silver(empty_player: Player) -> None:
    player = empty_player
    player.hand.append_several(5, CardName.BUREAUCRAT)

    player.start_turn()

    player.action(CardName.BUREAUCRAT)

    assert len(player.hand) == 4
    assert player.deck[0] == CardName.SILVER


def test_bureaucrat_without_silver(
    game_with_two_players: tuple[Game, Player, Player],
) -> None:
    game, player, _ = game_with_two_players
    while CardName.SILVER in game.stock:
        game.stock.remove(CardName.SILVER)

    player.deck.clear()
    player.hand.clear()
    player.hand.append_several(5, CardName.BUREAUCRAT)

    player.start_turn()

    player.action(CardName.BUREAUCRAT)

    assert len(player.hand) == 4
    assert not player.deck


def test_cellar(empty_player: Player) -> None:
    class Hooks(DefaultPlayerHooks):
        def __init__(self, *args: tuple, **kwargs: dict) -> None:
            super().__init__(*args, **kwargs)
            self.nb_cards = 0

        def confirm_discard_card_from_hand(
            self,
            card_name: CardName,
            hand: CardContainer,
        ) -> bool:
            self.nb_cards += 1
            return self.nb_cards < 3

    player = empty_player
    player.hand.append_several(5, CardName.CELLAR)
    player.deck.append_several(2, CardName.GOLD)
    player.hooks = Hooks()

    player.start_turn()

    player.action(CardName.CELLAR)

    assert len(player.hand) == 4
    assert player.hand.gold_qty == 2
    assert len(player.discard) == 2


@pytest.mark.parametrize(
    ("card_name", "more_purchase", "more_actions", "more_money", "more_cards"),
    [
        (CardName.CELLAR, 0, 1, 0, 0),
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


def test_card_coverage(player: Player) -> None:
    card = Village()
    print(card, card == Village, hash(card), player.hand)
