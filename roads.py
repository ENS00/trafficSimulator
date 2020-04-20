import const
import objects
from position import getDirection
# It's a graphic object but we can add tags that better describe the object (and also it's generally static)
class RoadObject(objects.GameRect):
    def __init__(self, game, color, points, tags=[]):
        super().__init__(game, color, points)
        self.tags = tags

    # Checks if it has a specific tag property
    def isA(self, prop):
        if prop in self.tags:
            return True
        return False

    def draw(self):
        super().draw()

    def rotate(self, angle, center):
        super().rotate(angle, center)

    def move(self, x, y):
        super().move(x, y)

# Traffic light status indicator
class Light(objects.GameCircle):
    def __init__(self, game, tLight, position, color_type = const.TL_RED, state_on = False, radius = const.TL_LIGHT_SIZE):
        super().__init__(game, const.TL_COLORS[color_type][state_on], position, radius)
        self.color_type = color_type
        self.state_on = state_on
        self.tLight = tLight
        self.offset = (position[1]-tLight.points[0][1])

    # This method is called when TL modifies his position and its lights need to be updated
    def updatePosition(self):
        rad = const.radians(self.tLight.degrees)
        self.position = [round(-self.offset*const.sin(rad) + const.TL_DISTANCES*2/3*const.cos(rad) + self.tLight.points[0][0]),
                         round(self.offset*const.cos(rad) + const.TL_DISTANCES*2/3*const.sin(rad) + self.tLight.points[0][1])]

    # The only way to move this object is to move the tLight ↑
    def move(self):
        return

    # Changes its color to a darker one
    def turnOff(self):
        state_on = False
        self.color = const.TL_COLORS[self.color_type][False]

    # Changes its color to a lighter one
    def turnOn(self):
        state_on = True
        self.color = const.TL_COLORS[self.color_type][True]

# Dark gray rect with three lights with different colors inside
class TrafficLight(RoadObject):
    def __init__(self, game, posred, direction = const.DOWN, state = const.TL_RED, on = False):
        p0 = [round(posred[0]-const.TL_DISTANCES*2/3),
              round(posred[1]-const.TL_DISTANCES)]
        p1 = [round(posred[0]+const.TL_DISTANCES*2/3),
              round(posred[1]-const.TL_DISTANCES)]
        p2 = [round(posred[0]+const.TL_DISTANCES*2/3),
              round(posred[1]+const.TL_DISTANCES*3)]
        p3 = [round(posred[0]-const.TL_DISTANCES*2/3),
              round(posred[1]+const.TL_DISTANCES*3)]
        super().__init__(game, const.DARK_GRAY, (p0, p1, p2, p3))
        self.on = on
        self.state = state
        if self.state == const.TL_RED:
            self.count = 5
        elif self.state == const.TL_YELLOW:
            self.count = 4
        else:
            self.count = 12

        super().draw()
        self.red = Light(game, self, [self.position[0], self.position[1] - const.TL_DISTANCES*4/3],
                         const.TL_RED, self.on and self.state==const.TL_RED)
        self.yellow = Light(game, self, self.position, const.TL_YELLOW, self.on and self.state==const.TL_YELLOW)
        self.green = Light(game, self, [self.position[0], self.position[1] + const.TL_DISTANCES*4/3],
                           const.TL_GREEN, self.on and self.state==const.TL_GREEN)

        if direction == const.LEFT:
            self.rotate(270)
        elif direction == const.RIGHT:
            self.rotate(90)
        elif direction == const.DOWN:
            self.rotate(180)

    # Move the rect and its lights
    def move(self, x, y):
        super().move(x,y)
        self.red.updatePosition()
        self.yellow.updatePosition()
        self.green.updatePosition()

    # Rotate the rect and its lights
    def rotate(self, angle):
        super().rotate(angle, self.red.position)
        self.red.updatePosition()
        self.yellow.updatePosition()
        self.green.updatePosition()

    # Changing the state of the TL and then updates its lights
    def changeState(self):
        if self.on:
            if self.state == const.TL_RED:
                self.state = const.TL_GREEN
            elif self.state == const.TL_YELLOW:
                self.state = const.TL_RED
            else:
                self.state = const.TL_YELLOW
        else:
            if self.state == const.TL_YELLOW:
                self.state = const.TL_OFF
            else:
                self.state = const.TL_YELLOW
        self.updateLights()

    # Updates the color of the lights
    def updateLights(self):
        if self.on:
            if self.state == const.TL_RED:
                self.red.turnOn()
                self.yellow.turnOff()
                self.green.turnOff()
            elif self.state == const.TL_YELLOW:
                self.red.turnOff()
                self.yellow.turnOn()
                self.green.turnOff()
            else:
                self.red.turnOff()
                self.yellow.turnOff()
                self.green.turnOn()
        else:
            if self.state == const.TL_YELLOW:
                self.red.turnOff()
                self.yellow.turnOn()
                self.green.turnOff()
            else:
                self.red.turnOff()
                self.yellow.turnOff()
                self.green.turnOff()

    # Change mode to on
    def turnOn(self):
        self.on = True
        self.updateLights()

    # Change mode to off
    def turnOff(self):
        self.on = False
        self.updateLights()

    # It has 12 passes get more info on documentation
    def update(self):
        self.count += 1
        if self.count >= 12:
            self.count = 0
        if self.on:
            if self.state == const.TL_GREEN and self.count >= 4:
                self.changeState()
            elif self.state == const.TL_YELLOW and self.count != 4:
                self.changeState()
            elif self.state == const.TL_RED and self.count <= 4:
                self.changeState()
        else:
            self.changeState()

    # Draws itself and its lights
    def draw(self):
        super().draw()
        self.red.draw()
        self.yellow.draw()
        self.green.draw()

# THIS IS NOT A GRAPHICAL OBJECT
# It is the union of one or more lanes
class Road():
    # At the moment, only 2-lane roads with the same direction can be instantiated
    def __init__(self, game, pstart, pstop, dim=const.ROAD_LINE_THICKNESS, lineW=const.ROAD_LINE_WIDTH, lineS=const.ROAD_LINE_SIZE):
        self.pstart = pstart
        self.pstop = pstop
        self.dim = dim
        self.lineW = lineW
        self.lineS = lineS
        direction = getDirection(pstart, pstop)

        self.pEntryStart = list(self.pstart)
        self.pEntryStop = list(self.pstop)
        self.pExitStop = list(self.pstart)
        self.pExitStart = list(self.pstop)
        if 'left' in direction:
            self.pEntryStart[1] -= dim/2
            self.pEntryStop[1] -= dim/2
            self.pExitStart[1] += dim/2
            self.pExitStop[1] += dim/2
        elif 'right' in direction:
            self.pEntryStart[1] += dim/2
            self.pEntryStop[1] += dim/2
            self.pExitStart[1] -= dim/2
            self.pExitStop[1] -= dim/2
        elif 'up' in direction:
            self.pEntryStart[0] += dim/2
            self.pEntryStop[0] += dim/2
            self.pExitStart[0] -= dim/2
            self.pExitStop[0] -= dim/2
        else:
            self.pEntryStart[0] -= dim/2
            self.pEntryStop[0] -= dim/2
            self.pExitStart[0] += dim/2
            self.pExitStop[0] += dim/2

        self.entry = Lane(game, self.pEntryStart, self.pEntryStop, self.dim, self.lineS, self.lineW, tags=['entry'])
        self.exit = Lane(game, self.pExitStart, self.pExitStop, self.dim, self.lineS, self.lineW, tags=['exit'])

    # Draws every lane
    def draw(self):
        self.entry.draw()
        self.exit.draw()

# It's a graphic object and also has some important points
class Lane(RoadObject):
    def __init__(self, game, pstart, pstop, dim, lineS, lineW, tLight=None, tags=[]):
        # I need to specify the game, though __init__ could do that job
        self.game = game

        self.pstart = pstart
        self.pstop = pstop
        self.dim = dim
        self.lineS = lineS
        self.lineW = lineW
        self.tags = getDirection(pstart, pstop)
        self.tags.extend(tags)

        self.borderLines = None
        self.stopLine = None
        self.road_lines = []

        self.setPosition(pstart, pstop)

        super().__init__(game, const.COLOR_ROAD, self.points, self.tags)

    # When it's moved it's needed to reset its points
    def defineLanePoints(self):
        if self.isA('left'):
            self.startLanePoints = (
                self.sides[0].midright,
                self.sides[1].midright
            )
            self.endLanePoints = (
                self.sides[0].midleft,
                self.sides[1].midleft
            )
        elif self.isA('right'):
            self.startLanePoints = (
                self.sides[0].midleft,
                self.sides[1].midleft
            )
            self.endLanePoints = (
                self.sides[0].midright,
                self.sides[1].midright
            )
        elif self.isA('up'):
            self.startLanePoints = (
                self.sides[0].midbottom,
                self.sides[1].midbottom
            )
            self.endLanePoints = (
                self.sides[0].midtop,
                self.sides[1].midtop
            )
        else:
            self.startLanePoints = (
                self.sides[0].midtop,
                self.sides[1].midtop
            )
            self.endLanePoints = (
                self.sides[0].midbottom,
                self.sides[1].midbottom
            )

        # graphic elements
        step = self.lineS*2 + self.lineW
        borderW = const.PROPORTION/4

        if len(self.road_lines)>0:
            [line.delete() for line in self.road_lines]
            self.road_lines = []

        if self.isA('left') or self.isA('right'):
            if self.pstart[0] < self.pstop[0]:
                road_lines = range(round(self.pstart[0]),
                                round(self.pstop[0]), step)
            else:
                road_lines = range(round(self.pstop[0]),
                                round(self.pstart[0]), step)

            if self.borderLines:
                self.borderLines[0].delete()
                self.borderLines[1].delete()
            self.borderLines = (objects.GameRect(self.game, const.WHITE, ((self.points[0][0], self.points[0][1] + borderW),
                                                                          (self.points[0][0], self.points[0][1] - borderW),
                                                                          (self.points[1][0], self.points[0][1] - borderW),
                                                                          (self.points[1][0], self.points[0][1] + borderW)
                                                                         )),
                                objects.GameRect(self.game, const.WHITE, ((self.points[0][0], self.points[2][1] + borderW),
                                                                          (self.points[0][0], self.points[2][1] - borderW),
                                                                          (self.points[1][0], self.points[2][1] - borderW),
                                                                          (self.points[1][0], self.points[2][1] + borderW)
                                                                         )))
            for posx in road_lines:
                self.road_lines.append(objects.GameRect(self.game, const.WHITE, ((posx, self.pstart[1]-self.dim/32),
                                                                                 (posx+self.lineW, self.pstart[1]-self.dim/32),
                                                                                 (posx+self.lineW, self.pstart[1]+self.dim/32),
                                                                                 (posx, self.pstart[1]+self.dim/32)
                                                                                )))
            if self.isA('entry'):
                if self.stopLine:
                    self.stopLine.delete()
                if self.isA('right'):
                    self.stopLine = objects.GameRect(self.game, const.WHITE, ((self.points[1][0] - const.STOPLINE_WIDTH, self.points[0][1]),
                                                                              (self.points[1][0], self.points[0][1]),
                                                                              (self.points[1][0], self.points[2][1]),
                                                                              (self.points[1][0] - const.STOPLINE_WIDTH, self.points[2][1])
                                                                             ))
                else:
                    self.stopLine = objects.GameRect(self.game, const.WHITE, ((self.points[0][0], self.points[1][1]),
                                                                              (self.points[0][0] + const.STOPLINE_WIDTH, self.points[1][1]),
                                                                              (self.points[0][0] + const.STOPLINE_WIDTH, self.points[3][1]),
                                                                              (self.points[0][0], self.points[3][1])
                                                                             ))
        else:
            if self.pstart[1] < self.pstop[1]:
                road_lines = range(round(self.pstart[1]),
                                round(self.pstop[1]), step)
            else:
                road_lines = range(round(self.pstop[1]),
                                round(self.pstart[1]), step)

            if self.borderLines:
                self.borderLines[0].delete()
                self.borderLines[1].delete()
            self.borderLines = (objects.GameRect(self.game, const.WHITE, ((self.points[1][0] - borderW, self.points[0][1]),
                                                                          (self.points[1][0] + borderW, self.points[0][1]),
                                                                          (self.points[1][0] + borderW, self.points[2][1]),
                                                                          (self.points[1][0] - borderW, self.points[2][1])
                                                                         )),
                                objects.GameRect(self.game, const.WHITE, ((self.points[0][0] - borderW, self.points[0][1]),
                                                                          (self.points[0][0] + borderW, self.points[0][1]),
                                                                          (self.points[0][0] + borderW, self.points[2][1]),
                                                                          (self.points[0][0] - borderW, self.points[2][1])
                                                                         )))
            for posy in road_lines:
                self.road_lines.append(objects.GameRect(self.game, const.WHITE, ((self.pstart[0] - self.dim/32, posy),
                                                                                 (self.pstart[0] + self.dim/32, posy),
                                                                                 (self.pstart[0] + self.dim/32, posy + self.lineW),
                                                                                 (self.pstart[0] - self.dim/32, posy + self.lineW)
                                                                                )))
            if self.isA('entry'):
                if self.stopLine:
                    self.stopLine.delete()
                if self.isA('up'):
                    self.stopLine = objects.GameRect(self.game, const.WHITE, ((self.points[0][0], self.points[0][1]),
                                                                              (self.points[1][0], self.points[0][1]),
                                                                              (self.points[1][0], self.points[0][1] + const.STOPLINE_WIDTH),
                                                                              (self.points[0][0], self.points[0][1] + const.STOPLINE_WIDTH)
                                                                             ))
                else:
                    self.stopLine = objects.GameRect(self.game, const.WHITE, ((self.points[0][0], self.points[2][1] - const.STOPLINE_WIDTH),
                                                                              (self.points[1][0], self.points[2][1] - const.STOPLINE_WIDTH),
                                                                              (self.points[1][0], self.points[2][1]),
                                                                              (self.points[0][0], self.points[2][1])
                                                                             ))

    # Changes its sides and sizes based on points passed
    def setPosition(self, pstart, pstop):
        self.pstart = pstart
        self.pstop = pstop
        if self.isA('left'):
            sides = (([self.pstop[0], self.pstop[1] - self.dim/2],
                        [self.pstart[0], self.pstart[1] - self.dim/2],
                        [self.pstart[0], self.pstart[1]],
                        [self.pstop[0], self.pstop[1]]),
                        ([self.pstop[0], self.pstop[1]],
                        [self.pstart[0], self.pstart[1]],
                        [self.pstart[0], self.pstart[1] + self.dim/2],
                        [self.pstop[0], self.pstop[1] + self.dim/2]))
            self.sides = [self.game.graphic_lib.graphic.Rect( sides[0][0],
                                                            (abs(sides[0][1][0]-sides[0][0][0]), self.dim/2) ),
                          self.game.graphic_lib.graphic.Rect( sides[1][0],
                                                            (abs(sides[1][1][0]-sides[1][0][0]), self.dim/2) )]
            self.points = (self.sides[0].topleft, self.sides[0].topright, self.sides[1].bottomright, self.sides[1].bottomleft)
        elif self.isA('right'):
            sides = (([self.pstart[0], self.pstart[1]],
                        [self.pstop[0], self.pstop[1]],
                        [self.pstop[0], self.pstop[1] + self.dim/2],
                        [self.pstart[0], self.pstart[1] + self.dim/2]),
                        ([self.pstart[0], self.pstart[1] - self.dim/2],
                        [self.pstop[0], self.pstop[1] - self.dim/2],
                        [self.pstop[0], self.pstop[1]],
                        [self.pstart[0], self.pstart[1]]))
            self.sides = [self.game.graphic_lib.graphic.Rect( sides[0][0],
                                                            (abs(sides[0][1][0]-sides[0][0][0]), self.dim/2) ),
                          self.game.graphic_lib.graphic.Rect( sides[1][0],
                                                            (abs(sides[1][1][0]-sides[1][0][0]), self.dim/2) )]
            self.points = (self.sides[1].topleft, self.sides[1].topright, self.sides[0].bottomright, self.sides[0].bottomleft)
        elif self.isA('up'):
            sides = (([self.pstop[0], self.pstop[1]],
                      [self.pstop[0] + self.dim/2, self.pstop[1]],
                      [self.pstart[0] + self.dim/2, self.pstart[1]],
                      [self.pstart[0], self.pstart[1]]),
                     ([self.pstop[0] - self.dim/2, self.pstop[1]],
                      [self.pstop[0], self.pstop[1]],
                      [self.pstart[0], self.pstart[1]],
                      [self.pstart[0] - self.dim/2, self.pstart[1]]))
            self.sides = [self.game.graphic_lib.graphic.Rect( sides[0][0],
                                                            (self.dim/2, abs(sides[0][2][1]-sides[0][0][1])) ),
                            self.game.graphic_lib.graphic.Rect( sides[1][0],
                                                            (self.dim/2, abs(sides[1][2][1]-sides[1][0][1])) )]
            self.points = (self.sides[1].topleft, self.sides[0].topright, self.sides[0].bottomright, self.sides[1].bottomleft)
        else:
            sides = (([self.pstart[0] - self.dim/2, self.pstart[1]],
                      [self.pstart[0], self.pstart[1]],
                      [self.pstop[0], self.pstop[1]],
                      [self.pstop[0] - self.dim/2, self.pstop[1]]),
                     ([self.pstart[0], self.pstart[1]],
                      [self.pstart[0] + self.dim/2, self.pstart[1]],
                      [self.pstop[0] + self.dim/2, self.pstop[1]],
                      [self.pstop[0], self.pstop[1]]))
            self.sides = [self.game.graphic_lib.graphic.Rect( sides[0][0],
                                                            (self.dim/2, abs(sides[0][2][1]-sides[0][0][1])) ),
                            self.game.graphic_lib.graphic.Rect( sides[1][0],
                                                            (self.dim/2, abs(sides[1][2][1]-sides[1][0][1])) )]
            self.points = (self.sides[0].topleft, self.sides[1].topright, self.sides[1].bottomright, self.sides[0].bottomleft)
        self.defineLanePoints()

    # Creates a tLight and associate it with the current object
    def createTrafficLight(self, status=const.TL_RED, on=False):
        if hasattr(self,'tLight'):
            self.removeTrafficLight()
        try:
            self.tags.remove('exit')
            self.tags.append('entry')
        except:
            pass

        if(self.isA('entry')):
            self.tLight = None
            # create the tl near the right side of the road
            if self.isA('down'):
                self.tLight = TrafficLight(self.game, (self.sides[0].bottomleft[0]-const.TL_DIST_X, self.sides[0].bottomleft[1]-const.TL_DIST_Y),
                                        const.DOWN, status, on)
            elif self.isA('up'):
                self.tLight = TrafficLight(self.game, (self.sides[0].topright[0]+const.TL_DIST_X, self.sides[0].topright[1]+const.TL_DIST_Y),
                                        const.UP, status, on)
            elif self.isA('left'):
                self.tLight = TrafficLight(self.game,(self.sides[0].topleft[0]+const.TL_DIST_X, self.sides[0].topleft[1]-const.TL_DIST_Y),
                                        const.LEFT, status, on)
            else:
                self.tLight = TrafficLight(self.game,(self.sides[0].bottomright[0]-const.TL_DIST_X, self.sides[0].bottomright[1]+const.TL_DIST_Y),
                                        const.RIGHT, status, on)
            return self.tLight
        
        raise Exception('Please be sure to tell to an "entry" road to create traffic light')

    def removeTrafficLight(self):
        self.tags.remove('entry')
        self.tags.append('exit')
        del self.tLight

# Graphical object (it's a square) but it contains all the intersection roads and manages them
class Crossroad(RoadObject):
    def __init__(self, game, roads):
        self.entries = [i.entry for i in roads]
        self.exits = [i.exit for i in roads]
        # assuming all lanes have equal dimensions
        self.dim = self.entries[0].dim
        minpstop = [20000, 20000]
        maxpstop = [0, 0]
        for i in self.exits:
            if i.isA('left'):
                i.setPosition((i.pstart[0] - self.dim, i.pstart[1]), i.pstop)
            elif i.isA('right'):
                i.setPosition((i.pstart[0] + self.dim, i.pstart[1]), i.pstop)
            elif i.isA('up'):
                i.setPosition((i.pstart[0], i.pstart[1] - self.dim), i.pstop)
            else:
                i.setPosition((i.pstart[0], i.pstart[1] + self.dim), i.pstop)
            i.crossroad = self
        for i in self.entries:
            if i.isA('left'):
                i.setPosition(i.pstart, (i.pstop[0] + self.dim, i.pstop[1]))
            elif i.isA('right'):
                i.setPosition(i.pstart, (i.pstop[0] - self.dim, i.pstop[1]))
            elif i.isA('up'):
                i.setPosition(i.pstart, (i.pstop[0], i.pstop[1] + self.dim))
            else:
                i.setPosition(i.pstart, (i.pstop[0], i.pstop[1] - self.dim))
            
            i.crossroad = self
            if i.pstop[0] < minpstop[0]:
                minpstop[0] = i.pstop[0]
            if i.pstop[1] < minpstop[1]:
                minpstop[1] = i.pstop[1]
            if i.pstop[0] > maxpstop[0]:
                maxpstop[0] = i.pstop[0]
            if i.pstop[1] > maxpstop[1]:
                maxpstop[1] = i.pstop[1]
            # create its own traffic light
            if i.isA('up') or i.isA('down'):
                i.createTrafficLight(const.TL_RED)
            else:
                i.createTrafficLight(const.TL_GREEN)
        points = ([minpstop[0], minpstop[1]], [maxpstop[0], minpstop[1]],
                  [maxpstop[0], maxpstop[1]], [minpstop[0], maxpstop[1]])
        super().__init__(game, const.COLOR_ROAD, points)

    def draw(self):
        super().draw()

    # Easily updates all tLights
    def updateTLights(self):
        for i in self.entries:
            i.tLight.update()

    # Easily turn on/off tLights
    def turnOnTLights(self, turnOn=True):
        if turnOn:
            [i.tLight.turnOn() for i in self.entries]
        else:
            [i.tLight.turnOff() for i in self.entries]

   # Gets where the point is (in which specific lane)
    def getLaneFromPos(self, obj, inflate=True):
        if hasattr(obj, 'graphic'):
            for i in self.entries:
                if obj.graphic.colliderect(i.sides[0]):
                    return i, 0
                if obj.graphic.colliderect(i.sides[1]):
                    return i, 1
            for i in self.exits:
                if obj.graphic.colliderect(i.sides[0]):
                    return i, 0
                if obj.graphic.colliderect(i.sides[1]):
                    return i, 1
        else:
            if inflate:
                for i in self.entries:
                    if i.sides[0].inflate(2,2).collidepoint(obj):
                        return i, 0
                    if i.sides[1].inflate(2,2).collidepoint(obj):
                        return i, 1
                for i in self.exits:
                    if i.sides[0].inflate(2,2).collidepoint(obj):
                        return i, 0
                    if i.sides[1].inflate(2,2).collidepoint(obj):
                        return i, 1
            else:
                for i in self.entries:
                    if i.sides[0].collidepoint(obj):
                        return i, 0
                    if i.sides[1].collidepoint(obj):
                        return i, 1
                for i in self.exits:
                    if i.sides[0].collidepoint(obj):
                        return i, 0
                    if i.sides[1].collidepoint(obj):
                        return i, 1
        # this point is not in a lane
        return None, None

    # Gets one random lane (it checks if there isn't any vehicle in there)
    def randomEntry(self):
        myentries = list(self.entries)
        while len(myentries)>0:
            ret = True
            randomE = myentries[const.randint(0,len(myentries)-1)]
            laneDim = randomE.dim
            xstart = randomE.pstart[0] - laneDim
            ystart = randomE.pstart[1] - const.THIRTY_PROPORTION
            if xstart<0:
                xstart = 0
            if ystart<0:
                ystart = 0
            spawnArea = self.game.graphic_lib.graphic.Rect([xstart, ystart],
                                                           [randomE.pstart[0] + laneDim, randomE.pstart[1] + const.THIRTY_PROPORTION])
            for vehicle in self.game.vehicles:
                if spawnArea.colliderect(vehicle.graphic):
                    myentries.remove(randomE)
                    ret = False
                    break
            if ret:
                return randomE
        return

    # Gets a random lane that does not have the same direction as the past lane
    def randomExit(self, entry=None):
        countElements = len(self.exits)
        if entry:
            roadId = self.entries.index(entry)
            elements = list(range(0,countElements))
            elements.remove(roadId)
            randomElement = elements[const.randint(0,countElements-2)]
            return self.exits[randomElement]
        return self.exits[const.randint(0,countElements-1)]

    # Given a vehicle, its spawn lane is obtained, then the returned lane is relative if we want to turn or go straight ahead
    def getOppositeLanes(self, vehicle, direction=const.FORWARD):
        road = vehicle.spawnLane
        if direction == const.RIGHT:
            if road.isA('up'):
                return [lane for lane in self.exits if lane.isA('right')]
            elif road.isA('down'):
                return [lane for lane in self.exits if lane.isA('left')]
            elif road.isA('left'):
                return [lane for lane in self.exits if lane.isA('up')]
            else:
                return [lane for lane in self.exits if lane.isA('down')]
        elif direction == const.LEFT:
            if road.isA('up'):
                return [lane for lane in self.exits if lane.isA('left')]
            elif road.isA('down'):
                return [lane for lane in self.exits if lane.isA('right')]
            elif road.isA('left'):
                return [lane for lane in self.exits if lane.isA('down')]
            else:
                return [lane for lane in self.exits if lane.isA('up')]
        else:
            if road.isA('up'):
                return [lane for lane in self.exits if lane.isA('up')]
            elif road.isA('down'):
                return [lane for lane in self.exits if lane.isA('down')]
            elif road.isA('left'):
                return [lane for lane in self.exits if lane.isA('left')]
            else:
                return [lane for lane in self.exits if lane.isA('right')]

    # Does a vehicle have precedence (right first) over another?
    def hasPrecedence(self, vehicle1, vehicle2):
        if vehicle1.spawnDirection == vehicle2.spawnDirection:
            return vehicle1.id < vehicle2.id
        # it's possible to get collisions from vehicles that turn
        if vehicle2.objectiveDirection == const.RIGHT:
            return False
        if vehicle1.objectiveDirection == const.RIGHT:
            return True
        if vehicle1.objectiveDirection == vehicle2.objectiveDirection:
            if vehicle1.spawnDirection == const.UP and vehicle2.spawnDirection == const.RIGHT:
                return True
            if vehicle1.spawnDirection == const.LEFT and vehicle2.spawnDirection == const.UP:
                return True
            if vehicle1.spawnDirection == const.DOWN and vehicle2.spawnDirection == const.LEFT:
                return True
            if vehicle1.spawnDirection == const.RIGHT and vehicle2.spawnDirection == const.DOWN:
                return True
            return False
        if vehicle2.objectiveDirection == const.FORWARD:
            return False
        if vehicle1.objectiveDirection == const.FORWARD:
            return True