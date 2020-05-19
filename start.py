from game import Game
# debug slow functions
# from cProfile import Profile

# Gameloop calls his father methods on main
class Gameloop(Game):
    def __init__(self):
        super().__init__()
        # self.profile = Profile()
        # self.profile.enable()
        self.drawField()

# main method
if __name__ == "__main__":
    game = Gameloop()
    while 1:
        game.loop()
