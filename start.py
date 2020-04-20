from game import Game

# Gameloop calls his father methods on main
class Gameloop(Game):
    def __init__(self):
        super().__init__()
        #self.autoSpawn = False
        self.drawField()
        self.crossroad.turnOnTLights()
        #self.spawnVehicle()
        while 1:
            self.loop()

# main method
if __name__ == "__main__":
    game = Gameloop()