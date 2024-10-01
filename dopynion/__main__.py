# example of execution
from dopynion.cards import CardName
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

player1.start_turn()
player1.buy(CardName.SMITHY)
player1.end_turn()

for _ in range(5):
    print("#" * 80)
    player1.start_turn()
    print(player1)
    if CardName.SMITHY in player1.hand:
        player1.action(CardName.SMITHY)
    print(player1)
    player1.end_turn()
