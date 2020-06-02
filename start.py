from game import Game

# Gameloop calls his father methods on main
class Gameloop(Game):
    def __init__(self):
        super().__init__()
        self.drawField()

# main method
if __name__ == "__main__":
    game = Gameloop()
    while 1:
        game.loop()
