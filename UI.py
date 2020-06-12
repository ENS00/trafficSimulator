import const
from objects import GameRect

# Manage all panels
class UI():
    def __init__(self, game):
        self.game = game
        self.panels = []
        self.freePositionLeft = [const.W_WIDTH/30, const.W_HEIGHT/50]
        self.freePositionRight = [const.W_WIDTH*2/3, const.W_HEIGHT/50]
        self.padding = const.PROPORTION

    def createPanel(self, updateFunction = lambda: '', size = const.MEDIUM, show = True, clickFunction = lambda self: None, align = const.LEFT):
        if align == const.LEFT:
            newPanel = Panel(self.game, size, self.freePositionLeft, updateFunction, clickFunction, show, align)
            self.freePositionLeft[1] += size
            self.panels.append(newPanel)
            return newPanel
        newPanel = Panel(self.game, size, self.freePositionRight, updateFunction, clickFunction, show, align)
        self.freePositionRight[1] += size
        self.panels.append(newPanel)
        return newPanel

    def updatePanels(self):
        [panel.update() for panel in self.panels]

    # handle click events on panels
    def handlePanelsClick(self, pos):
        for panel in self.panels:
            if panel.area.collidepoint(pos):
                panel.click()
                return True
        return False

class Panel(GameRect):
    def __init__(self, game, size, position, updateFunction, clickFunction, show, align):
        self.value = updateFunction()
        padding = game.uiManager.padding

        lines = self.value.splitlines()
        width = 0
        for line in lines:
            mywidth, height = game.graphic_lib.fonts[size].size(line)
            if width<mywidth:
                width = mywidth
        height *= self.value.count('\n')+1
        super().__init__(game, const.BACKGROUND_PANEL, ([position[0] - padding, position[1] - padding],
                                                        [position[0] + padding + width, position[1] - padding],
                                                        [position[0] + padding + width, position[1] + padding + height],
                                                        [position[0] - padding, position[1] + padding + height]))

        self.updateFunction = updateFunction
        self.clickFunction = clickFunction
        self.size = size
        self.area = game.graphic_lib.graphic.Rect(self.points[0][0],
                                                  self.points[0][1],
                                                  self.points[2][0],
                                                  self.points[2][1] - self.points[0][1])
        self.textPos = (self.points[0][0] + padding, self.points[0][1] + padding)
        game.graphic_lib.updateAreas.append(self.area)
        self.hidden = not show

    def update(self):
        self.value = self.updateFunction()
        self.draw()

    # Draws the panel on screen
    def draw(self):
        if not self.graphic:
            self.graphic = self.graphic_lib.graphic.draw.polygon(self.graphic_lib.screen, self.color, self.points)
            self.position = self.graphic.topleft
        if not self.hidden:
            self.graphic = self.graphic_lib.drawText(self.textPos, self.value, self.size)

    def changeVisibility(self):
        self.hidden = not self.hidden

    def click(self):
        if not self.hidden:
            self.clickFunction(self)

# control all input events from the user
class EventHandler():
    def __init__(self, game, ui):
        self.game = game
        self.ui = ui
        self.graphic = game.graphic_lib.graphic

    # this method needs an object obtained by self.graphic_lib.graphic.event.get()
    # all pygame events are managed here
    def handleEvents(self, events):
        for event in events:
            # left click on the screen
            if event.type == self.graphic.MOUSEBUTTONUP and event.button == 1:
                if self.ui.handlePanelsClick(event.pos):
                    break
                # check if the target is a vehicle
                for vehicle in self.game.vehicles:
                    if const.GETCOLLISION(event.pos, vehicle.calcPoints()):
                        self.game.selectedVehicle = vehicle
                        self.game.vehicleDetailsPanel.hidden = False
                        break

            # quit simulation
            if event.type == self.graphic.QUIT:
                self.continueProcess = False
                const.OUTPUT_DEVICE.closeConnection()
                exit()
