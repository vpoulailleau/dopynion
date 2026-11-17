import pytest

from dopynion.cards import Card, CardName
from dopynion.exceptions import (
    AddPlayerDuringGameError,
    InvalidCommandError,
)
from dopynion.game import Game
from dopynion.player import Player


def test_can_add_player(game: Game) -> None:
    game.add_player(Player("player 1"))
    game.start()
    assert len(game.players) == 1


def test_cannot_add_player_on_started_game(game: Game) -> None:
    game.add_player(Player("player 1"))
    game.start()
    with pytest.raises(AddPlayerDuringGameError):
        game.add_player(Player("2"))


def test_max_nb_players(game: Game) -> None:
    game.add_player(Player("1"))
    game.add_player(Player("2"))
    game.add_player(Player("3"))
    game.add_player(Player("4"))
    with pytest.raises(InvalidCommandError):
        game.add_player(Player("5"))
    game.start()


def test_initial_money(game: Game) -> None:
    game.add_player(Player("1"))
    game.add_player(Player("2"))
    game.start()
    assert game.platinum_qty == 12
    assert game.gold_qty == 30
    assert game.silver_qty == 40
    assert game.copper_qty == 60 - 7 * 2


def test_initial_estates_2_players(game: Game) -> None:
    game.add_player(Player("1"))
    game.add_player(Player("2"))
    game.start()
    assert game.estate_qty == 8 * 5
    assert game.stock.quantity(CardName.ESTATE) == 8 * 5
    assert game.duchy_qty == 8 * 5
    assert game.stock.quantity(CardName.DUCHY) == 8 * 5
    assert game.province_qty == 8 * 5
    assert game.stock.quantity(CardName.PROVINCE) == 8 * 5
    assert game.colony_qty == 8 * 5
    assert game.stock.quantity(CardName.COLONY) == 8 * 5


def test_initial_estates_2_players_without_colony_card_type(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delitem(Card.types, CardName.COLONY, raising=False)
    game = Game()
    game.add_player(Player("1"))
    game.add_player(Player("2"))
    game.start()
    assert game.colony_qty == 0
    assert game.stock.quantity(CardName.COLONY) == 0


def test_initial_estates_3_players(game: Game) -> None:
    game.add_player(Player("1"))
    game.add_player(Player("2"))
    game.add_player(Player("3"))
    game.start()
    # For 3+ players, victory_factor now applies to estates/duchy/province too
    assert game.estate_qty == 12 * 5
    assert game.duchy_qty == 12 * 5
    assert game.province_qty == 12 * 5
    assert game.colony_qty == 12 * 5


def test_initial_malediction_2_players(game: Game) -> None:
    game.add_player(Player("1"))
    game.add_player(Player("2"))
    game.start()
    assert game.curse_qty == 10 * 5


def test_initial_malediction_3_players(game: Game) -> None:
    game.add_player(Player("1"))
    game.add_player(Player("2"))
    game.add_player(Player("3"))
    game.start()
    assert game.curse_qty == 20 * 5


def test_initial_malediction_4_players(game: Game) -> None:
    game.add_player(Player("1"))
    game.add_player(Player("2"))
    game.add_player(Player("3"))
    game.add_player(Player("4"))
    game.start()
    assert game.curse_qty == 30 * 5


def test_victory_factor_with_colony_2_players(game: Game) -> None:
    """Test victory_factor is 5 when COLONY is in Card.types (2 players)."""
    # COLONY is in Card.types by default
    game.add_player(Player("1"))
    game.add_player(Player("2"))
    game.start()
    assert game.estate_qty == 8 * 5
    assert game.duchy_qty == 8 * 5
    assert game.province_qty == 8 * 5
    assert game.colony_qty == 8 * 5
    assert game.curse_qty == 10 * 5


def test_victory_factor_without_colony_2_players(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test victory_factor is 1 when COLONY is not in Card.types (2 players)."""
    monkeypatch.delitem(Card.types, CardName.COLONY, raising=False)
    game = Game()
    game.add_player(Player("1"))
    game.add_player(Player("2"))
    game.start()
    assert game.estate_qty == 8 * 1
    assert game.duchy_qty == 8 * 1
    assert game.province_qty == 8 * 1
    assert game.colony_qty == 0
    assert game.curse_qty == 10 * 1


def test_victory_factor_with_colony_3_players(game: Game) -> None:
    """Test victory_factor is 5 when COLONY is in Card.types (3 players)."""
    game.add_player(Player("1"))
    game.add_player(Player("2"))
    game.add_player(Player("3"))
    game.start()
    # Now victory_factor applies to estates/duchy/province for 3+ players too
    assert game.estate_qty == 12 * 5
    assert game.duchy_qty == 12 * 5
    assert game.province_qty == 12 * 5
    assert game.colony_qty == 12 * 5
    assert game.curse_qty == 20 * 5


def test_victory_factor_without_colony_3_players(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test victory_factor is 1 when COLONY is not in Card.types (3 players)."""
    monkeypatch.delitem(Card.types, CardName.COLONY, raising=False)
    game = Game()
    game.add_player(Player("1"))
    game.add_player(Player("2"))
    game.add_player(Player("3"))
    game.start()
    # Without COLONY, victory_factor is 1, so all quantities should be base values
    assert game.estate_qty == 12 * 1
    assert game.duchy_qty == 12 * 1
    assert game.province_qty == 12 * 1
    assert game.colony_qty == 0
    assert game.curse_qty == 20 * 1


def test_victory_factor_with_colony_4_players(game: Game) -> None:
    """Test victory_factor is 5 when COLONY is in Card.types (4 players)."""
    game.add_player(Player("1"))
    game.add_player(Player("2"))
    game.add_player(Player("3"))
    game.add_player(Player("4"))
    game.start()
    # Now victory_factor applies to estates/duchy/province for 4 players too
    assert game.estate_qty == 12 * 5
    assert game.duchy_qty == 12 * 5
    assert game.province_qty == 12 * 5
    assert game.colony_qty == 12 * 5
    assert game.curse_qty == 30 * 5


def test_victory_factor_without_colony_4_players(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test victory_factor is 1 when COLONY is not in Card.types (4 players)."""
    monkeypatch.delitem(Card.types, CardName.COLONY, raising=False)
    game = Game()
    game.add_player(Player("1"))
    game.add_player(Player("2"))
    game.add_player(Player("3"))
    game.add_player(Player("4"))
    game.start()
    # Without COLONY, victory_factor is 1, so all quantities should be base values
    assert game.estate_qty == 12 * 1
    assert game.duchy_qty == 12 * 1
    assert game.province_qty == 12 * 1
    assert game.colony_qty == 0
    assert game.curse_qty == 30 * 1
