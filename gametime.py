from time import gmtime, time, strftime
from const import START_TIME, FPS

# Manage the current in-game time
class Gametime():
    def __init__(self, graphic_lib, ratio, startTime = START_TIME, fps = FPS):
        self.clock = graphic_lib.graphic.time.Clock()
        graphic_lib.clock = self.clock
        self.ratio = ratio
        self.graphic_lib = graphic_lib
        self.fps = float(fps)
        self.startTime = startTime
        self.timeFromStart = 0

    # Get the current in-game time
    def getTime(self):
        self.clock.tick(self.fps) # necessary for fps
        self.timeFromStart += self.ratio/50000*self.getFps()
        return int(self.timeFromStart)

    def getFps(self):
        return self.clock.get_fps() or self.fps

    # Get a formatted version of current time (from 113 to 01:53)
    def getFormattedTime(self, timestamp = None):
        if not timestamp:
            timestamp = self.startTime + self.timeFromStart
        return strftime('%H:%M',gmtime(timestamp))#'%H:%M:%S'

    # Get a formatted version of current time (from 113 to 01:53)
    def getHours(self, timestamp = None):
        if not timestamp:
            timestamp = self.startTime + self.timeFromStart
        return int(strftime('%H',gmtime(timestamp)))

    # Get a formatted version of current time (from 113 to 01:53)
    def getMinutes(self, timestamp = None):
        if not timestamp:
            timestamp = self.startTime + self.timeFromStart
        return int(strftime('%M',gmtime(timestamp)))

    # Get a formatted version of time difference (from 113 to 1h53m)
    def getFormattedTimeDelta(self, timeDelta):
        return strftime('%H:%M:%S',gmtime(timeDelta))

    def getRealISODateTime(self):
        return strftime("%Y-%m-%dT%H:%M:%SZ", gmtime(time()))
