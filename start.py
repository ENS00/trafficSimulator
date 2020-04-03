from game import Game

class Gameloop(Game):
    def __init__(self, fps=None):
        if fps:
            super().__init__(fps)
        else:
            super().__init__()
        self.drawField()
        while 1:
            self.loop()

if __name__ == "__main__":
    game = Gameloop()