from game import Game
import data_output as tx
import influxdb_connection as influxdb_out

# Gameloop calls his father methods on main
class Gameloop(Game):
    def __init__(self):
        super().__init__()
        #self.autoSpawn = False
        self.drawField()
        self.crossroad.turnOnTLights()

# main method
if __name__ == "__main__":
    
    db_prova = influxdb_out.DBOutput()
    db_prova.dbCheckConn()

    game = Gameloop()
    while 1:
        game.loop()
        tx.printTxt()

    
    
    