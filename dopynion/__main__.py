# example of execution
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
