from time import gmtime, time, strftime
from const import START_TIME, FPS, CONFIGURATION_SPEED

# Manage the current in-game time
class Gametime():
    def __init__(self, graphic_lib, startTime = START_TIME, fps = FPS):
        self.clock = graphic_lib.graphic.time.Clock()
        graphic_lib.clock = self.clock
        self.graphic_lib = graphic_lib
        self.fps = float(fps)
        self.speed = CONFIGURATION_SPEED
        self.startTime = startTime
        self.timeFromStart = 0

    # Get the current in-game time
    def getTime(self):
        self.clock.tick(self.fps) # necessary for fps
        self.timeFromStart += 3/500*self.getFps()
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

    # Get a formatted version of time difference (from 113 to 1m 53s)
    def getFormattedTimeDelta(self, timeDelta):
        return timeDelta#strftime('%Mm %Ss',gmtime(timeDelta/60))

    def getRealISODateTime(self):
        return strftime("%Y-%m-%dT%H:%M:%SZ", gmtime(time()))

    def increaseSpeed(self):
        self.speed+=1
        if self.speed>3:
            self.speed = 3
            return
        self.fps += 25

    def decreaseSpeed(self):
        self.speed -= 1
        if self.speed < 1:
            self.speed = 1
            return
        self.fps -= 25
