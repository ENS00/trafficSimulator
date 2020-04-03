from time import strftime,gmtime
import const

# Manage the current in-game time
class Gametime():
    def __init__(self, graphic_lib, ratio, fps = const.FPS):
        self.clock = graphic_lib.graphic.time.Clock()
        graphic_lib.clock = self.clock
        self.ratio = ratio
        self.graphic_lib = graphic_lib
        self.fps = fps
        self.timeFromStart = 0

    # Get the current in-game time
    def getTime(self):
        self.clock.tick(self.fps) #necessary for fps
        # difference = self.graphic_lib.graphic.time.get_ticks()*self.ratio - self.timeFromStart
        # self.timeFromStart += difference*self.getFps()/self.fps
        if self.getFps():
            self.timeFromStart += self.ratio/self.fps
        return self.timeFromStart

    def getFps(self):
        return self.clock.get_fps()

    # Get a formatted version of current time (from 113 to 01:53)
    def getFormattedTime(self):
        return strftime('%H:%M',gmtime(self.timeFromStart))#'%H:%M:%S'