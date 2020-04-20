from const import BLACK,TIMEPANEL_SIZE,W_WIDTH,W_HEIGHT
from objects import GameRect
# Shows graphically the current in-game time (HH:MM)
class TimePanel(GameRect):
    def __init__(self, game, gametime, size = TIMEPANEL_SIZE):
        super().__init__(game, BLACK, ([W_WIDTH/30,W_HEIGHT/50],
                                             [size*2.5,W_HEIGHT/50],
                                             [size*2.5,size],
                                             [W_WIDTH/30,size]))
        self.gametime = gametime
        self.value = '00:00'
        self.size = size

    # Updates the clock and draws it
    def update(self):
        self.value = self.gametime.getFormattedTime()
        self.draw()

    # Draws on screen the current time
    def draw(self):
        if not self.graphic:
            self.graphic = self.graphic_lib.graphic.draw.polygon(self.graphic_lib.screen, self.color, self.points)
            # self.graphic_lib.updateAreas.append(self.graphic)
            self.position = self.graphic.topleft
        self.graphic = self.graphic_lib.drawText(self.position, self.value, self.size)