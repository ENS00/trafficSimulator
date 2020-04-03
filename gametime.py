from time import strftime,gmtime
import const

class Gametime():
    def __init__(self, graphic_lib, ratio, fps=30):
        self.clock = graphic_lib.graphic.time.Clock()
        graphic_lib.clock = self.clock
        self.ratio = ratio
        self.graphic_lib = graphic_lib
        self.fps = fps
        self.timeFromStart = 0
    def getTime(self):
        self.clock.tick(self.fps) #necessary for fps
        # difference = self.graphic_lib.graphic.time.get_ticks()*self.ratio - self.timeFromStart
        # self.timeFromStart += difference*self.getFps()/self.fps
        if self.getFps():
            self.timeFromStart += self.ratio/self.fps
        return self.timeFromStart
    def getFps(self):
        return self.clock.get_fps()
    def getFormattedTime(self):
        return strftime('%H:%M',gmtime(self.timeFromStart))#'%H:%M:%S'