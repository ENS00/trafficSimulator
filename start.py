from game import Game
import influxdb_connection as influxdb_out

crash = 'incidenti'
timing = 'tempistiche'
dataXhour = 'dati_per_ora'
provaStringa = []
provaStringa.append(crash)
provaStringa.append(timing)
provaStringa.append(dataXhour)

# Gameloop calls his father methods on main
class Gameloop(Game):
    def __init__(self):
        super().__init__()
        self.drawField()
        self.crossroad.turnOnTLights()

# main method
if __name__ == "__main__":

    db_prova = influxdb_out.DBOutput()
    db_prova.dbCheckConn()

    write_csv = influxdb_out.CSVOutput()
    write_csv.createPath()
    write_csv.writeCSV(provaStringa)

    game = Gameloop()
    while 1:
        game.loop()
