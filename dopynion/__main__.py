# example of execution

import logging
import random
from pprint import pprint

from dopynion.cards import Card, CardName
from dopynion.game import Game
from dopynion.player import Player

logging.basicConfig(
    filename="game.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format=(
        "%(asctime)s [%(levelname)-8s] %(filename)20s(%(lineno)3s):"
        "%(funcName)-20s :: %(message)s"
    ),
    datefmt="%m/%d/%Y %H:%M:%S",
)
logging.info("Launching server")  # noqa: LOG015 used only once…

game = Game()
player1 = Player("Foo")
player2 = Player("Bar")
player3 = Player("Baz")
game.add_player(player1)
game.add_player(player2)
game.add_player(player3)
game.start()

turn = 0
while not game.finished:
    turn += 1
    print("#" * 80)
    print(f"# turn {turn}")
    print("#" * 80)
    print(game.state)
    player1.start_turn()
    print(player1.state)

    while player1.actions_left and player1.hand.contains_action():
        actions = player1.hand.action_cards
        player1.action(random.choice(actions))  # noqa: S311
        print(player1)

    while player1.purchases_left and player1.hand.contains_money():
        money = player1.hand.money
        buyables: list[CardName] = [
            card_name
            for card_name, class_ in Card.types.items()
            if class_.cost <= money and card_name in game.stock
        ]
        player1.buy(random.choice(buyables))  # noqa: S311
        print(player1)

    player1.end_turn()

    player2.start_turn()
    player2.end_turn()

    player3.start_turn()
    player3.end_turn()

pprint(game.score())  # noqa: T203
game.save()
