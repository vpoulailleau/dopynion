# example of execution

import random

from dopynion.cards import Card, CardName
from dopynion.game import Game
from dopynion.player import Player

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
