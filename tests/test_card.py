from dataclasses import dataclass

import pytest

from dopynion.cards import Card, CardContainer, CardName, Village
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


def test_chancellor_dont_discard_deck(empty_player: Player) -> None:
    class Hooks(DefaultPlayerHooks):
        def confirm_discard_deck(self) -> bool:  # noqa: PLR6301
            return False

    player = empty_player
    player.hand.append_several(5, CardName.CHANCELLOR)
    player.deck.append_several(3, CardName.GOLD)
    player.hooks = Hooks()

    player.start_turn()

    player.action(CardName.CHANCELLOR)

    assert len(player.hand) == 4
    assert len(player.deck) == 3
    assert len(player.discard) == 0


def test_chancellor_discard_deck(empty_player: Player) -> None:
    class Hooks(DefaultPlayerHooks):
        def confirm_discard_deck(self) -> bool:  # noqa: PLR6301
            return True

    player = empty_player
    player.hand.append_several(5, CardName.CHANCELLOR)
    player.deck.append_several(3, CardName.GOLD)
    player.hooks = Hooks()

    player.start_turn()

    player.action(CardName.CHANCELLOR)

    assert len(player.hand) == 4
    assert len(player.deck) == 0
    assert len(player.discard) == 3


def test_chapel_discard_two_cards(empty_player: Player) -> None:
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
    player.hand.append_several(5, CardName.CHAPEL)
    player.hooks = Hooks()

    player.start_turn()

    player.action(CardName.CHAPEL)

    assert len(player.hand) == 2
    assert len(player.deck) == 0
    assert len(player.discard) == 2


def test_chapel_discard_as_many_cards_as_possible_that_is_four(
    empty_player: Player,
) -> None:
    class Hooks(DefaultPlayerHooks):
        def __init__(self, *args: tuple, **kwargs: dict) -> None:
            super().__init__(*args, **kwargs)
            self.nb_cards = 0

        def confirm_discard_card_from_hand(  # noqa: PLR6301
            self,
            card_name: CardName,
            hand: CardContainer,
        ) -> bool:
            return True

    player = empty_player
    player.hand.append_several(15, CardName.CHAPEL)
    player.hooks = Hooks()

    player.start_turn()

    player.action(CardName.CHAPEL)

    assert len(player.hand) == 10
    assert len(player.deck) == 0
    assert len(player.discard) == 4


def test_feast_trash(empty_player: Player) -> None:
    player = empty_player
    player.hand.append_several(5, CardName.FEAST)
    player.start_turn()

    player.action(CardName.FEAST)

    assert len(player.played_cards) == 0


def test_feast_trash_good_cardname(empty_player: Player) -> None:
    player = empty_player
    player.hand.append_several(4, CardName.FEAST)
    player.hand.append(CardName.FESTIVAL)
    player.start_turn()
    player.action(CardName.FESTIVAL)

    player.action(CardName.FEAST)

    assert len(player.played_cards) == 1
    assert CardName.FESTIVAL in player.played_cards


def test_feast_choose_a_card(empty_player: Player) -> None:
    class Hooks(DefaultPlayerHooks):
        def __init__(self, *args: tuple, **kwargs: dict) -> None:
            super().__init__(*args, **kwargs)
            self.nb_cards = 0

        def choose_card_to_receive_in_discard(  # noqa: PLR6301
            self,
            possible_cards: list[CardName],
        ) -> CardName:
            return possible_cards[0]

    player = empty_player
    player.hooks = Hooks()
    player.hand.append_several(5, CardName.FEAST)
    player.start_turn()

    player.action(CardName.FEAST)

    assert len(player.discard) == 1


def test_council_room(game_with_two_players: tuple[Game, Player, Player]) -> None:
    _, player, enemy = game_with_two_players
    player.hand.clear()
    player.hand.append_several(5, CardName.COUNCILROOM)
    enemy.hand.clear()

    player.start_turn()

    player.action(CardName.COUNCILROOM)

    assert len(player.hand) == 4 + Card.types[CardName.COUNCILROOM].more_cards_from_deck
    assert len(enemy.hand) == 1


def test_gardens_score_39_cards(empty_player: Player) -> None:
    player = empty_player
    player.deck.append_several(2, CardName.GARDENS)
    player.deck.append_several(37, CardName.COPPER)

    score = player.score()
    assert score["gardens_qty"] == 2
    assert score["score"] == 6


def test_gardens_score_40_cards(empty_player: Player) -> None:
    player = empty_player
    player.deck.append_several(2, CardName.GARDENS)
    player.deck.append_several(38, CardName.COPPER)

    score = player.score()
    assert score["gardens_qty"] == 2
    assert score["score"] == 8


def test_library(empty_player: Player) -> None:
    class Hooks(DefaultPlayerHooks):
        nb_max_skip = 3

        def __init__(self, *args: tuple, **kwargs: dict) -> None:
            super().__init__(*args, **kwargs)
            self.nb_cards = 0

        def skip_card_reception_in_hand(
            self,
            _card_name: CardName,
            _hand: list[CardName],
        ) -> bool:
            self.nb_cards += 1
            return self.nb_cards <= self.nb_max_skip

    player = empty_player
    player.hooks = Hooks()
    player.deck.append_several(7, CardName.VILLAGE)
    player.deck.append_several(50, CardName.COPPER)
    player.hand.append(CardName.GOLD)
    player.hand.append(CardName.LIBRARY)
    player.start_turn()

    player.action(CardName.LIBRARY)

    assert len(player.hand) == 7
    assert len(player.discard) == player.hooks.nb_max_skip


def test_militia(game_with_two_players: tuple[Game, Player, Player]) -> None:
    _, player, enemy = game_with_two_players
    player.hand.clear()
    player.hand.append_several(5, CardName.MILITIA)
    enemy.hand.clear()
    enemy.hand.append_several(5, CardName.MILITIA)

    player.start_turn()

    player.action(CardName.MILITIA)

    assert len(player.hand) == 4
    assert len(enemy.hand) == 3


def test_mine_don_t_trash(empty_player: Player) -> None:
    player = empty_player
    player.hand.append(CardName.COPPER)
    player.hand.append(CardName.MINE)
    player.start_turn()

    player.action(CardName.MINE)

    assert len(player.hand) == 1
    assert player.hand[0] == CardName.COPPER


def test_mine_trash_copper(empty_player: Player) -> None:
    class Hooks(DefaultPlayerHooks):
        def trash_money_card_for_better_money_card(  # noqa: PLR6301
            self,
            _money_in_hand: list[CardName],
        ) -> CardName | None:
            return CardName.COPPER

    player = empty_player
    player.hooks = Hooks()
    player.hand.append(CardName.COPPER)
    player.hand.append(CardName.MINE)
    player.start_turn()

    player.action(CardName.MINE)

    assert len(player.hand) == 1
    assert player.hand[0] == CardName.SILVER


def test_mine_trash_silver(empty_player: Player) -> None:
    class Hooks(DefaultPlayerHooks):
        def trash_money_card_for_better_money_card(  # noqa: PLR6301
            self,
            _money_in_hand: list[CardName],
        ) -> CardName | None:
            return CardName.SILVER

    player = empty_player
    player.hooks = Hooks()
    player.hand.append(CardName.SILVER)
    player.hand.append(CardName.MINE)
    player.start_turn()

    player.action(CardName.MINE)

    assert len(player.hand) == 1
    assert player.hand[0] == CardName.GOLD


def test_mine_trash_gold(empty_player: Player) -> None:
    class Hooks(DefaultPlayerHooks):
        def trash_money_card_for_better_money_card(  # noqa: PLR6301
            self,
            _money_in_hand: list[CardName],
        ) -> CardName | None:
            return CardName.GOLD

    player = empty_player
    player.hooks = Hooks()
    player.hand.append(CardName.GOLD)
    player.hand.append(CardName.MINE)
    player.start_turn()

    player.action(CardName.MINE)

    assert len(player.hand) == 1
    assert player.hand[0] == CardName.GOLD


# TODO trash don't exist
# TODO check dans les hooks quand ils piochent dans une liste que l'élément choisi est
# bien dans la liste


def test_money_lender_refuse(empty_player: Player) -> None:
    player = empty_player
    player.hand.append_several(2, CardName.COPPER)
    player.hand.append_several(3, CardName.MONEYLENDER)
    player.start_turn()

    player.action(CardName.MONEYLENDER)

    assert len(player.hand) == 4
    assert player.hand.copper_qty == 2


def test_money_lender_accept(empty_player: Player) -> None:
    class Hooks(DefaultPlayerHooks):
        def __init__(self, *args: tuple, **kwargs: dict) -> None:
            super().__init__(*args, **kwargs)
            self.nb_cards = 0

        def confirm_discard_card_from_hand(  # noqa: PLR6301
            self,
            card_name: CardName,
            hand: CardContainer,
        ) -> bool:
            return True

    player = empty_player
    player.hooks = Hooks()
    player.hand.append_several(2, CardName.COPPER)
    player.hand.append_several(3, CardName.MONEYLENDER)
    player.start_turn()

    player.action(CardName.MONEYLENDER)

    assert len(player.deck) == 0
    assert len(player.discard) == 0
    assert len(player.played_cards) == 1
    assert player.hand.copper_qty == 1 + 3
    assert len(player.hand) == 4 - 1 + 3


def test_remodel(empty_player: Player) -> None:
    class Hooks(DefaultPlayerHooks):
        def __init__(self, *args: tuple, **kwargs: dict) -> None:
            super().__init__(*args, **kwargs)
            self.nb_cards = 0

        def discard_card_from_hand(  # noqa: PLR6301
            self,
            _hand: list[CardName],
        ) -> CardName:
            return CardName.COPPER

        def choose_card_to_receive_in_discard(  # noqa: PLR6301
            self,
            possible_cards: list[CardName],
        ) -> CardName:
            for card_name in possible_cards:
                assert (
                    Card.types[card_name].cost <= Card.types[CardName.COPPER].cost + 2
                )
            return possible_cards[0]

    player = empty_player
    player.hooks = Hooks()
    player.hand.append_several(1, CardName.COPPER)
    player.hand.append_several(3, CardName.SILVER)
    player.hand.append_several(1, CardName.REMODEL)
    player.start_turn()

    player.action(CardName.REMODEL)

    assert len(player.deck) == 0
    assert len(player.played_cards) == 1
    assert len(player.hand) == 3
    assert len(player.discard) == 1


def test_witch(game_with_two_players: tuple[Game, Player, Player]) -> None:
    _, player, enemy = game_with_two_players
    player.hand.clear()
    player.hand.append_several(5, CardName.WITCH)
    enemy.hand.clear()
    enemy.hand.append_several(5, CardName.WITCH)

    player.start_turn()

    player.action(CardName.WITCH)

    assert len(player.hand) == 4 + Card.types[CardName.WITCH].more_cards_from_deck
    assert len(enemy.hand) == 5
    assert CardName.CURSE in enemy.discard


def test_workshop(empty_player: Player) -> None:
    class Hooks(DefaultPlayerHooks):
        def __init__(self, *args: tuple, **kwargs: dict) -> None:
            super().__init__(*args, **kwargs)
            self.nb_cards = 0

        def choose_card_to_receive_in_discard(  # noqa: PLR6301
            self,
            possible_cards: list[CardName],
        ) -> CardName:
            for card_name in possible_cards:
                assert Card.types[card_name].cost <= 4
            return possible_cards[0]

    player = empty_player
    player.hooks = Hooks()
    player.hand.append_several(5, CardName.WORKSHOP)

    player.start_turn()

    player.action(CardName.WORKSHOP)

    assert len(player.discard) == 1
    assert len(player.hand) == 4


@dataclass
class CardParameter:
    card_name: CardName
    more_purchase: int
    more_actions: int
    more_money: int
    more_cards: int


@pytest.mark.parametrize(
    ("card_param"),
    [
        CardParameter(
            CardName.CELLAR,
            more_purchase=0,
            more_actions=1,
            more_money=0,
            more_cards=0,
        ),
        CardParameter(
            CardName.CHANCELLOR,
            more_purchase=0,
            more_actions=0,
            more_money=2,
            more_cards=0,
        ),
        CardParameter(
            CardName.COUNCILROOM,
            more_purchase=1,
            more_actions=0,
            more_money=0,
            more_cards=4,
        ),
        CardParameter(
            CardName.FESTIVAL,
            more_purchase=1,
            more_actions=2,
            more_money=2,
            more_cards=0,
        ),
        CardParameter(
            CardName.LABORATORY,
            more_purchase=0,
            more_actions=1,
            more_money=0,
            more_cards=2,
        ),
        CardParameter(
            CardName.MARKET,
            more_purchase=1,
            more_actions=1,
            more_money=1,
            more_cards=1,
        ),
        CardParameter(
            CardName.MILITIA,
            more_purchase=0,
            more_actions=0,
            more_money=2,
            more_cards=0,
        ),
        CardParameter(
            CardName.SMITHY,
            more_purchase=0,
            more_actions=0,
            more_money=0,
            more_cards=3,
        ),
        CardParameter(
            CardName.VILLAGE,
            more_purchase=0,
            more_actions=2,
            more_money=0,
            more_cards=1,
        ),
        CardParameter(
            CardName.WITCH,
            more_purchase=0,
            more_actions=0,
            more_money=0,
            more_cards=2,
        ),
        CardParameter(
            CardName.WOODCUTTER,
            more_purchase=1,
            more_actions=0,
            more_money=2,
            more_cards=0,
        ),
    ],
)
def test_basic_cards(
    player_with_action_card: Player,
    card_param: CardParameter,
) -> None:
    player = player_with_action_card
    player.hand.append(card_param.card_name)
    player.start_turn()
    old_purchases_left = player.purchases_left
    old_actions_left = player.actions_left
    old_money = player.money
    old_nb_cards = len(player.hand)

    player.action(card_param.card_name)

    assert Card.types[card_param.card_name].is_action
    assert player.purchases_left == old_purchases_left + card_param.more_purchase
    assert player.actions_left == (old_actions_left - 1) + card_param.more_actions
    assert player.money == old_money + card_param.more_money
    assert len(player.hand) == (old_nb_cards - 1) + card_param.more_cards


def test_card_coverage(player: Player) -> None:
    card = Village()
    print(card, card == Village, hash(card), player.hand)
