from const import BLACK,TIMEPANEL_SIZE,W_WIDTH,W_HEIGHT
from objects import GameRect

class Panel(GameRect):
    def __init__(self, game, size, position):
        super().__init__(game, BLACK, ([position[0], position[1]],
                                       [position[0]+size*2.5, position[1]],
                                       [position[0]+size*2.5, position[1]+size],
                                       [position[0], position[1]+size]))
        self.value = ''
        self.size = size

    # It will be implemented in child class
    def update(self):
        pass

    # Draws the panel on screen
    def draw(self):
        if not self.graphic:
            self.graphic = self.graphic_lib.graphic.draw.polygon(self.graphic_lib.screen, self.color, self.points)
            self.position = self.graphic.topleft
        self.graphic = self.graphic_lib.drawText(self.position, self.value, self.size)

# Shows graphically the current in-game time (HH:MM)
class TimePanel(Panel):
    def __init__(self, game, gametime, size = TIMEPANEL_SIZE, position = (W_WIDTH/30,W_HEIGHT/50)):
        super().__init__(game, size, position)
        self.gametime = gametime
        self.value = '00:00'
        self.size = size

    # Updates the clock and draws it
    def update(self):
        self.value = self.gametime.getFormattedTime()
        self.draw()

class VehicleCountPanel(Panel):
    def __init__(self, game, size = int(TIMEPANEL_SIZE/2), position = (W_WIDTH/30,W_HEIGHT/20)):
        super().__init__(game, size, position)
        self.value = 'Vehicle count: 0'
        self.size = size

    # Updates the panel and draws it
    def update(self):
        self.value = 'Vehicle count: ' + str(len(self.game.vehicles))
        self.draw()