import pytest

from dopynion.cards import CardName
from dopynion.game import Game
from dopynion.player import Player


@pytest.fixture(name="game")
def _game() -> Game:
    class TestRecord:
        def save(self) -> None:
            pass

        def start_turn(self) -> None:
            pass

        def add_action(self, action: str, player: Player) -> None:
            pass

        def add_error(self, error: str, player: Player) -> None:
            pass

    return Game(record_factory=TestRecord)


@pytest.fixture(name="player")
def _player(game: Game) -> Player:
    player = Player("toto")
    game.add_player(player)
    game.start()
    return player


@pytest.fixture(name="empty_player")
def _empty_player(player: Player) -> Player:
    player.hand.clear()
    player.discard.clear()
    player.deck.clear()
    return player


@pytest.fixture(name="player_with_action_card")
def _player_with_action_card(player: Player) -> Player:
    player.hand.pop(0)
    player.hand.append(CardName.FESTIVAL)
    return player


@pytest.fixture(name="game_with_two_players")
def _game_with_two_players(game: Game) -> tuple[Game, Player, Player]:
    player = Player("toto")
    enemy = Player("tata")
    game.add_player(player)
    game.add_player(enemy)
    game.start()
    return game, player, enemy
