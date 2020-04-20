import const
import position

# Primary basic object with all common properties
class GameObject():
    def __init__(self, game, color, degrees):
        self.id = game.idassigner.getNewID(self)
        self.game = game
        self.graphic_lib = self.game.graphic_lib
        self.degrees = degrees
        self.graphic = None
        self.position = None
        self.color = color

    # On draw it sets only the center
    def draw(self):
        self.position = self.graphic.center

    # On delete it calls the id assigner to remove it from the known objects
    def delete(self):
        self.game.idassigner.delete(self)

# Basic shape with 4 sides
class GameRect(GameObject):
    def __init__(self, game, color, points, degrees = 0):
        super().__init__(game, color, degrees)
        self.points = points

    # On draw gets the graphic object and then sets the center
    def draw(self):
        self.graphic = self.graphic_lib.graphic.draw.polygon(self.graphic_lib.screen, self.color, self.points)
        self.position = self.graphic.center

    # Move every side (but not the center, it is modified only when it is drawn)
    def move(self, x, y):
        self.points[0][0] += x
        self.points[0][1] += y
        self.points[1][0] += x
        self.points[1][1] += y
        self.points[2][0] += x
        self.points[2][1] += y
        self.points[3][0] += x
        self.points[3][1] += y

    # It modifies the sides starting from a new given center, but doesn't modify the center
    def moveTo(self, position):
        x = position[0] - self.position[0]
        y = position[1] - self.position[1]
        self.position = position
        self.points[0][0] += x
        self.points[0][1] += y
        self.points[1][0] += x
        self.points[1][1] += y
        self.points[2][0] += x
        self.points[2][1] += y
        self.points[3][0] += x
        self.points[3][1] += y

    # Move every side with a specific rule in order to rotate the whole shape
    def rotate(self, angle, center = None):
        if angle!=0:
            self.degrees += angle
            if self.degrees > 360:
                self.degrees -= 360
            if self.degrees < 0:
                self.degrees += 360

            const.ROTATE(self.points[0], center or self.position, angle)
            const.ROTATE(self.points[1], center or self.position, angle)
            const.ROTATE(self.points[2], center or self.position, angle)
            const.ROTATE(self.points[3], center or self.position, angle)

# Basic object with a center and a radius
class GameCircle(GameObject):
    def __init__(self, game, color, center, radius, degrees = 0):
        super().__init__(game, color, degrees)
        self.position = [round(center[0]), round(center[1])]
        self.radius = radius

    # On draw gets the graphic object and then sets the center
    def draw(self):
        self.graphic = self.graphic_lib.graphic.draw.circle(self.graphic_lib.screen, self.color, self.position, self.radius)
        self.position = self.graphic.center

    # Since the center is needed to draw the object, it's modified
    def move(self, x, y):
        self.position[0] = round(x) + self.position[0]
        self.position[1] = round(y) + self.position[1]

# It's a graphic object but we can add tags that better describe the object (and also it's generally static)
class RoadObject(GameRect):
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
class Light(GameCircle):
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
        direction = position.getDirection(pstart, pstop)

        self.pEntryStart = list(self.pstart)
        self.pEntryStop = list(self.pstop)
        self.pExitStop = list(self.pstart)
        self.pExitStart = list(self.pstop)
        if 'left' in direction:
            self.pEntryStart[1]-=dim/2
            self.pEntryStop[1]-=dim/2
            self.pExitStart[1]+=dim/2
            self.pExitStop[1]+=dim/2
        elif 'right' in direction:
            self.pEntryStart[1]+=dim/2
            self.pEntryStop[1]+=dim/2
            self.pExitStart[1]-=dim/2
            self.pExitStop[1]-=dim/2
        elif 'up' in direction:
            self.pEntryStart[0]+=dim/2
            self.pEntryStop[0]+=dim/2
            self.pExitStart[0]-=dim/2
            self.pExitStop[0]-=dim/2
        else:
            self.pEntryStart[0]-=dim/2
            self.pEntryStop[0]-=dim/2
            self.pExitStart[0]+=dim/2
            self.pExitStop[0]+=dim/2

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
        self.tags = position.getDirection(pstart, pstop)
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
        step = self.lineS*2+self.lineW
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
            self.borderLines = (GameRect(self.game, const.WHITE, ((self.points[0][0], self.points[0][1]+borderW),
                                                                  (self.points[0][0], self.points[0][1]-borderW),
                                                                  (self.points[1][0], self.points[0][1]-borderW),
                                                                  (self.points[1][0], self.points[0][1]+borderW)
                                                                )),
                                GameRect(self.game, const.WHITE, ((self.points[0][0], self.points[2][1]+borderW),
                                                                  (self.points[0][0], self.points[2][1]-borderW),
                                                                  (self.points[1][0], self.points[2][1]-borderW),
                                                                  (self.points[1][0], self.points[2][1]+borderW)
                                                                )))
            for posx in road_lines:
                self.road_lines.append(GameRect(self.game, const.WHITE, ((posx, self.pstart[1]-self.dim/32),
                                                                            (posx+self.lineW, self.pstart[1]-self.dim/32),
                                                                            (posx+self.lineW, self.pstart[1]+self.dim/32),
                                                                            (posx, self.pstart[1]+self.dim/32))))
            if self.isA('entry'):
                if self.stopLine:
                    self.stopLine.delete()
                if self.isA('right'):
                    self.stopLine = GameRect(self.game, const.WHITE, ((self.points[1][0]-const.STOPLINE_WIDTH, self.points[0][1]),
                                                                      (self.points[1][0], self.points[0][1]),
                                                                      (self.points[1][0], self.points[2][1]),
                                                                      (self.points[1][0]-const.STOPLINE_WIDTH, self.points[2][1])))
                else:
                    self.stopLine = GameRect(self.game, const.WHITE, ((self.points[0][0], self.points[1][1]),
                                                                      (self.points[0][0]+const.STOPLINE_WIDTH, self.points[1][1]),
                                                                      (self.points[0][0]+const.STOPLINE_WIDTH, self.points[3][1]),
                                                                      (self.points[0][0], self.points[3][1])))
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
            self.borderLines = (GameRect(self.game, const.WHITE, ((self.points[1][0]-borderW, self.points[0][1]),
                                                                  (self.points[1][0]+borderW, self.points[0][1]),
                                                                  (self.points[1][0]+borderW, self.points[2][1]),
                                                                  (self.points[1][0]-borderW, self.points[2][1])
                                                                )),
                                GameRect(self.game, const.WHITE, ((self.points[0][0]-borderW, self.points[0][1]),
                                                                  (self.points[0][0]+borderW, self.points[0][1]),
                                                                  (self.points[0][0]+borderW, self.points[2][1]),
                                                                  (self.points[0][0]-borderW, self.points[2][1])
                                                                )))
            for posy in road_lines:
                self.road_lines.append(GameRect(self.game, const.WHITE, ((self.pstart[0]-self.dim/32, posy),
                                                                         (self.pstart[0]+self.dim/32, posy),
                                                                         (self.pstart[0]+self.dim/32, posy+self.lineW),
                                                                         (self.pstart[0]-self.dim/32, posy+self.lineW))))
            if self.isA('entry'):
                if self.stopLine:
                    self.stopLine.delete()
                if self.isA('up'):
                    self.stopLine = GameRect(self.game, const.WHITE, ((self.points[0][0], self.points[0][1]),
                                                                      (self.points[1][0], self.points[0][1]),
                                                                      (self.points[1][0], self.points[0][1]+const.STOPLINE_WIDTH),
                                                                      (self.points[0][0], self.points[0][1]+const.STOPLINE_WIDTH)))
                else:
                    self.stopLine = GameRect(self.game, const.WHITE, ((self.points[0][0], self.points[2][1]-const.STOPLINE_WIDTH),
                                                                      (self.points[1][0], self.points[2][1]-const.STOPLINE_WIDTH),
                                                                      (self.points[1][0], self.points[2][1]),
                                                                      (self.points[0][0], self.points[2][1])))

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
        
# Most important and complex class of simulation, common properties for vehicle and decision-making are there
class Vehicle(GameRect):
    def __init__(self, game, crossroad, lane, side, power=const.CAR_ACCELERATION):
        self.game = game
        self.position = lane.startLanePoints[side]

        self.velocity = const.VEHICLE_SPAWN_SPEED
        self.power = power
        self.steerDeg = 0
        self.acceleration = 0.5
        self.deceleration = 0
        self.prev_acceleration = self.acceleration
        self.prev_deceleration = self.deceleration

        self.crossroad = crossroad
        self.spawnLane = lane
        self.spawnSide = side
        self.arrived = False

    def initObject(self, color, points):
        super().__init__(self.game, color, points, self.degrees)
        super().draw()

    # Modifies all its parameters and position, according to its acceleration, deceleration and steering
    def update(self):
        self.velocity += self.acceleration*self.power/self.weight
        if self.velocity > 0:
            self.velocity -= self.deceleration*4*self.power/self.weight
        # prev_acceleration prev_deceleration used in predict function
        self.prev_acceleration = self.acceleration
        self.prev_deceleration = self.deceleration
        self.acceleration = 0
        self.deceleration = 0
        if self.velocity > 0:
            self.velocity = round(self.velocity - const.VEHICLE_FRICTION*const.ceil(self.velocity/10)*self.weight, const.FLOAT_PRECISION)
        if self.velocity > 0 and self.steerDeg:
            self.velocity = round(self.velocity - const.fabs(self.steerDeg)*0.0005*pow(self.velocity,0.3), const.FLOAT_PRECISION)
        if self.velocity < 0:
            self.velocity = 0
        else:
            if self.steerDeg:
                determinant,center = self.calcDeterminant()
                if center:
                    # i do not need rear calc because it's fine use one of the rear wheels
                    # rotate the vehicle
                    self.rotate(const.copysign(self.velocity * const.VEHICLE_RENDER*75 / position.distance(center,self.position), self.steerDeg), center)
                else:
                    radians = const.radians(self.degrees)
                    calc_x = round(const.cos(radians) * self.velocity * const.VEHICLE_RENDER, const.FLOAT_PRECISION)
                    calc_y = round(const.sin(radians) * self.velocity * const.VEHICLE_RENDER, const.FLOAT_PRECISION)
                    self.move(calc_x, calc_y)
            else:
                radians = const.radians(self.degrees)
                calc_x = round(const.cos(radians) * self.velocity * const.VEHICLE_RENDER, const.FLOAT_PRECISION)
                calc_y = round(const.sin(radians) * self.velocity * const.VEHICLE_RENDER, const.FLOAT_PRECISION)
                self.move(calc_x, calc_y)

    # Modifies his steering wheel rotation, respecting a defined maximum
    def steer(self, power = 0):
        if power < -33:
            power = -33
        if power > 33:
            power = 33
        # speed of steering
        difference = power - self.steerDeg
        if difference > 2:
            difference = 2
        if difference < -2:
            difference = -2
        self.steerDeg += difference

    # Modifies his acceleration
    def accelerate(self, power = 0.5):
        if power < 0:
            power = 0
        if power > 1:
            power = 1
        self.acceleration = power
        self.deceleration = 0

    # Modifies his deceleration
    def brake(self, power = 0.5):
        if power < 0:
            power = 0
        if power > 1:
            power = 1
        self.deceleration = power
        self.acceleration = 0

    # Sets the vehicle waypoints to get to destination
    def setObjective(self, lane):
        self.waypoints = []
        currentLane, rightS = self.crossroad.getLaneFromPos(self)
        if not currentLane:
            currentLane = self.spawnLane
            rightS = self.spawnSide
            # if currentLane == None or rightS == None:
            #     raise Exception('This object is not in a lane')
        # if not currentLane.isA('entry'):
        #     raise Exception('Cannot set objective when the vehicle is already leaving')
        if ((currentLane.isA('right') and lane.isA('left')) or
            (currentLane.isA('up') and lane.isA('down')) or
            (currentLane.isA('left') and lane.isA('right')) or
                (currentLane.isA('down') and lane.isA('up'))):
            raise Exception('Cannot set objective same road (you can only move right, forward or left)')
        # find if we want to turn left or right or go forward
        # then think if we need extra waypoints
        if (currentLane.isA('left') and lane.isA('down')) or (currentLane.isA('up') and lane.isA('left')) or (currentLane.isA('right') and lane.isA('up')) or (currentLane.isA('down') and lane.isA('right')):
            self.objectiveDirection = const.LEFT
            if(rightS == 0):
                # we are on the wrong side
                rightS = 1
                if currentLane.isA('right'):
                    self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0]/2 + const.PROPORTION, currentLane.endLanePoints[rightS][1], 25))
                elif currentLane.isA('left'):
                    self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0]*4/3 - const.PROPORTION, currentLane.endLanePoints[rightS][1], 25))
                elif currentLane.isA('up'):
                    self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0], currentLane.endLanePoints[rightS][1]*4/3 - const.PROPORTION, 25))
                else:
                    self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0], currentLane.endLanePoints[rightS][1]/2 + const.PROPORTION, 25))
            # end of current lane
            if currentLane.isA('right'):
                self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0] + const.DOUBLE_PROPORTION, currentLane.endLanePoints[rightS][1], 35, checkTLight=True))
                self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0] + const.EIGHTEEN_PROPORTION, currentLane.endLanePoints[rightS][1], 10, checkLeft=True))
            elif currentLane.isA('left'):
                self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0] - const.DOUBLE_PROPORTION, currentLane.endLanePoints[rightS][1], 35, checkTLight=True))
                self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0] - const.EIGHTEEN_PROPORTION, currentLane.endLanePoints[rightS][1], 10, checkLeft=True))
            elif currentLane.isA('up'):
                self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0], currentLane.endLanePoints[rightS][1] - const.DOUBLE_PROPORTION, 35, checkTLight=True))
                self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0], currentLane.endLanePoints[rightS][1] - const.EIGHTEEN_PROPORTION, 10, checkLeft=True))
            else:
                self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0], currentLane.endLanePoints[rightS][1] + const.DOUBLE_PROPORTION, 35, checkTLight=True))
                self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0], currentLane.endLanePoints[rightS][1] + const.EIGHTEEN_PROPORTION, 10, checkLeft=True))
            # start of new lane
            if lane.isA('right'):
                self.waypoints.append(position.Waypoint(lane.startLanePoints[rightS][0] - const.DOUBLE_PROPORTION, lane.startLanePoints[rightS][1], 18))
            elif lane.isA('left'):
                self.waypoints.append(position.Waypoint(lane.startLanePoints[rightS][0] + const.DOUBLE_PROPORTION, lane.startLanePoints[rightS][1], 18))
            elif lane.isA('up'):
                self.waypoints.append(position.Waypoint(lane.startLanePoints[rightS][0], lane.startLanePoints[rightS][1] + const.DOUBLE_PROPORTION, 18))
            else:
                self.waypoints.append(position.Waypoint(lane.startLanePoints[rightS][0], lane.startLanePoints[rightS][1] - const.DOUBLE_PROPORTION, 18))
        elif (currentLane.isA('left') and lane.isA('up')) or (currentLane.isA('up') and lane.isA('right')) or (currentLane.isA('right') and lane.isA('down')) or (currentLane.isA('down') and lane.isA('left')):
            self.objectiveDirection = const.RIGHT
            if(rightS == 1):
                # we are on the wrong side
                rightS = 0
                if currentLane.isA('right'):
                    self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0]/2 + const.PROPORTION, currentLane.endLanePoints[rightS][1], 25))
                elif currentLane.isA('left'):
                    self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0]*4/3 - const.PROPORTION, currentLane.endLanePoints[rightS][1], 25))
                elif currentLane.isA('up'):
                    self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0], currentLane.endLanePoints[rightS][1]*4/3 - const.PROPORTION, 25))
                else:
                    self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0], currentLane.endLanePoints[rightS][1]/2 + const.PROPORTION, 25))
            # end of current lane
            if currentLane.isA('right'):
                self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0] + self.width, currentLane.endLanePoints[rightS][1], 25, checkTLight=True))
            elif currentLane.isA('left'):
                self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0] - self.width, currentLane.endLanePoints[rightS][1], 25, checkTLight=True))
            elif currentLane.isA('up'):
                self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0], currentLane.endLanePoints[rightS][1] - self.width, 25, checkTLight=True))
            else:
                self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0], currentLane.endLanePoints[rightS][1] + self.width, 25, checkTLight=True))
            # start of new lane
            if lane.isA('right'):
                self.waypoints.append(position.Waypoint(lane.startLanePoints[rightS][0], lane.startLanePoints[rightS][1], 18))
            elif lane.isA('left'):
                self.waypoints.append(position.Waypoint(lane.startLanePoints[rightS][0], lane.startLanePoints[rightS][1], 18))
            elif lane.isA('up'):
                self.waypoints.append(position.Waypoint(lane.startLanePoints[rightS][0], lane.startLanePoints[rightS][1], 18))
            else:
                self.waypoints.append(position.Waypoint(lane.startLanePoints[rightS][0], lane.startLanePoints[rightS][1], 18))
        else:
            # exit is on the other lane
            self.objectiveDirection = const.FORWARD

        # exit of new lane
        self.waypoints.append(position.Waypoint(lane.endLanePoints[rightS][0], lane.endLanePoints[rightS][1], 90, checkTLight=True))

        #debug
        # for i in self.waypoints:
        #     self.game.graphic_lib.drawCircle(
        #             i.x,i.y,5, fill=const.RED_OFF)

    # This method defines all decision-making of the driver
    def drive(self, allvehicles):
        if not hasattr(self, 'waypoints') or len(self.waypoints) < 1:
            self.accelerate(1)
            return

        if self.graphic.collidepoint(self.waypoints[0].position):#position.distance(self.position, self.waypoints[0].position) < 7:
            # we passed the target
            self.waypoints.pop(0)
            if len(self.waypoints) < 1:
                self.arrived = True
                self.accelerate(1)
                return

        objective = self.waypoints[0].clone()

        # radians that descripes inclination of direction from p1 to p2
        desiredDirection = position.getRadians(self.position, objective.position)

        # if I am in the crossroad i check if I can turn left
        if objective.checkLeft:
            # check for other vehicles
            x,y = 1,1
            if abs(const.cos(const.radians(self.degrees))) > abs(const.sin(const.radians(self.degrees))):
                x,y = 4,0.5
            else:
                x,y = 0.5,4
            collideArea = self.game.graphic_lib.graphic.Rect(objective.position[0]-const.TEN_PROPORTION*x,
                                                             objective.position[1]+const.TEN_PROPORTION*y,
                                                             const.TEN_PROPORTION*x,
                                                             const.TEN_PROPORTION*y)
            for vehicle in allvehicles:
                if vehicle.id == self.id:
                    continue
                if self.crossroad.hasPrecedence(self,vehicle) or (not self.crossroad.hasPrecedence(vehicle,self) and self.id<vehicle.id):
                    continue
                if vehicle.graphic.colliderect(collideArea):
                    self.brake(1)
                    return

        currentLane,laneN = self.crossroad.getLaneFromPos(self.points[0])
        if objective.checkTLight and currentLane and currentLane.isA('entry') and currentLane.tLight.on:
            # we need to check tlight
            currentEndLane = currentLane.endLanePoints[laneN]
            objectiveLane,laneObjN = self.crossroad.getLaneFromPos(objective.position)
            if currentLane.tLight.state == const.TL_RED:
                if currentLane.isA('up'):
                    objective = position.Waypoint(currentEndLane[0], currentEndLane[1] + const.OCTUPLE_PROPORTION,0)
                elif currentLane.isA('down'):
                    objective = position.Waypoint(currentEndLane[0], currentEndLane[1] - const.OCTUPLE_PROPORTION,0)
                elif currentLane.isA('left'):
                    objective = position.Waypoint(currentEndLane[0] + const.OCTUPLE_PROPORTION, currentEndLane[1],0)
                else:
                    objective = position.Waypoint(currentEndLane[0] - const.OCTUPLE_PROPORTION, currentEndLane[1],0)
            elif currentLane.tLight.state == const.TL_YELLOW:
                if currentLane.isA('up'):
                    objective1 = position.Waypoint(currentEndLane[0], currentEndLane[1] + const.OCTUPLE_PROPORTION,0)
                elif currentLane.isA('down'):
                    objective1 = position.Waypoint(currentEndLane[0], currentEndLane[1] - const.OCTUPLE_PROPORTION,0)
                elif currentLane.isA('left'):
                    objective1 = position.Waypoint(currentEndLane[0] + const.OCTUPLE_PROPORTION, currentEndLane[1],0)
                else:
                    objective1 = position.Waypoint(currentEndLane[0] - const.OCTUPLE_PROPORTION, currentEndLane[1],0)
                # will I pass tlight in n cycles?
                # if not canPassTL:
                objective = objective1
                objective.velocity = 0

        distanceFromObjective = position.distance(self.position, objective.position)

        if distanceFromObjective and objective.velocity > self.velocity:
            if self.velocity:
                accelerate = (objective.velocity-self.velocity) / self.velocity/2 / self.power*self.weight
                self.accelerate(accelerate)
            else:
                self.accelerate(1)
        elif distanceFromObjective > const.DOUBLE_PROPORTION and self.velocity<10:
            self.accelerate(1)

        elif objective.velocity < self.velocity:
            ntimes = distanceFromObjective / self.velocity*2.2 / const.VEHICLE_RENDER
            if ntimes:
                brake = self.velocity / ntimes / 4/self.power*self.weight
                self.brake(brake)

        avoidx = const.cos(desiredDirection)
        avoidy = const.sin(desiredDirection)
        magnitude = 0
        # check for other vehicles
        points = self.calcFrontArea()
        # collideArea = self.game.graphic_lib.graphic.Rect(points)
        for vehicle in allvehicles:
            if vehicle.id == self.id:
                continue
            if self.crossroad.hasPrecedence(self,vehicle) or (not self.crossroad.hasPrecedence(vehicle, self) and self.id<vehicle.id):
                continue
            distance = position.distance(vehicle.position, self.position)
            if distance<100:
                if position.getRectCollision(self.points,vehicle.points):
                    print('Accident between %i and %i' %(self.id,vehicle.id))
                    self.game.deleteObject(self)
                    self.game.deleteObject(vehicle)
                    return
                if position.getRectCollision(points, vehicle.points):
                    brake = self.velocity*2/distance
                    magnitude = max(brake, magnitude)
                    resAngle = position.getRadians(self.position,vehicle.position)
                    avoidx -= const.cos(resAngle) / distance * vehicle.width
                    avoidy -= const.sin(resAngle) / distance * vehicle.height

        rad = const.degrees(const.atan2(avoidy,avoidx))
        # rad = const.degrees(desiredDirection)

        if magnitude:
            self.brake(magnitude)

        left = self.degrees - rad
        if left < 0:
            left = round(left + 360, const.FLOAT_PRECISION)
        right = rad - self.degrees
        if right < 0:
            right = round(right + 360, const.FLOAT_PRECISION)
        if right < left:
            self.steer(right)
        else:
            self.steer(-left)

    # It returns determinant and if possible center of a rotation
    def calcDeterminant(self, degrees=None):
        if degrees == None:
            degrees = self.degrees
        # +90 because we want the line perpendicular to the front axis
        steerRad = const.radians(90 + self.steerDeg + degrees)
        # using ackermann algorithm to steer the vehicle
        wheels = self.calcWheelsPosition()
        # find the center
        front = (wheels[0][0] + (wheels[1][0]-wheels[0][0])/2, wheels[0][1] + (wheels[1][1] - wheels[0][1])/2)
        fronti = (front[0] + const.cos(steerRad),
                front[1] + const.sin(steerRad))

        rearA = wheels[2][1] - wheels[3][1]                 # N *x
        rearB = wheels[3][0] - wheels[2][0]                 # N *y
        rearC = rearA*(wheels[3][0]) + rearB*(wheels[3][1]) # C
        if rearA<0 and rearB<0:
            rearA = -rearA
            rearB = -rearB
            rearC = -rearC
        # it could be -x -y = -c... to fix
        frontA = front[1] - fronti[1]
        frontB = fronti[0] - front[0]
        frontC = frontA*(fronti[0]) + frontB*(fronti[1])
        if frontA<0 and frontB<0:
            frontA = -frontA
            frontB = -frontB
            frontC = -frontC

        determinant = frontA*rearB - rearA*frontB
        if determinant:
            return determinant,((rearB*frontC - frontB*rearC)/determinant, (frontA*rearC - rearA*frontC)/determinant)
        return None,None

    # Having the inclination and the center, it's possible to calculate each of its points
    def calcPoints(self, position=None, degrees=None):
        if not position:
            position = self.position
        if not degrees:
            degrees = self.degrees
        mysin = const.sin(const.radians(degrees))
        mycos = const.cos(const.radians(degrees))
        return (
            [round(position[0] + mysin*self.height + mycos*self.width, const.FLOAT_PRECISION),
                round(position[1] + mysin*self.width - mycos*self.height, const.FLOAT_PRECISION)],
            [round(position[0] - mysin*self.height + mycos*self.width, const.FLOAT_PRECISION),
                round(position[1] + mysin*self.width + mycos*self.height, const.FLOAT_PRECISION)],
            [round(position[0] - mysin*self.height - mycos*self.width, const.FLOAT_PRECISION),
                round(position[1] - mysin*self.width + mycos*self.height, const.FLOAT_PRECISION)],
            [round(position[0] + mysin*self.height - mycos*self.width, const.FLOAT_PRECISION),
                round(position[1] - mysin*self.width - mycos*self.height, const.FLOAT_PRECISION)]
        )

    # It's an extention of the car to avoid collisions
    def calcExtendedPoints(self, position=None, degrees=None):
        if not position:
            position = self.position
        if not degrees:
            degrees = self.degrees
        mysin = const.sin(const.radians(degrees))
        mycos = const.cos(const.radians(degrees))
        height = self.height+5
        width = self.width+5
        return (
            [round(position[0] + mysin*height + mycos*width, const.FLOAT_PRECISION),
                round(position[1] + mysin*width - mycos*height, const.FLOAT_PRECISION)],
            [round(position[0] - mysin*height + mycos*width, const.FLOAT_PRECISION),
                round(position[1] + mysin*width + mycos*height, const.FLOAT_PRECISION)],
            [round(position[0] - mysin*height - mycos*width, const.FLOAT_PRECISION),
                round(position[1] - mysin*width + mycos*height, const.FLOAT_PRECISION)],
            [round(position[0] + mysin*height - mycos*width, const.FLOAT_PRECISION),
                round(position[1] - mysin*width - mycos*height, const.FLOAT_PRECISION)]
        )

    # The front of the vehicle
    def calcFrontArea(self):
        mysin = const.sin(const.radians(self.degrees))
        mycos = const.cos(const.radians(self.degrees))
        points = list(self.calcPoints())
        view_h = const.DOUBLE_PROPORTION
        view_w = const.TEN_PROPORTION
        points[2] = list(points[1])
        points[3] = list(points[0])
        points[0][0] += mysin*view_h + mycos*view_w
        points[0][1] += mysin*view_w - mycos*view_h
        points[1][0] += -mysin*view_h + mycos*view_w
        points[1][1] += mysin*view_w + mycos*view_h

        points[2][0] -= mysin*view_h
        points[2][1] += mycos*view_h
        points[3][0] += mysin*view_h
        points[3][1] -= mycos*view_h

        return points

# Main vehicle
class Car(Vehicle):
    def __init__(self, game, crossroad, lane, side = const.randint(0,1), color = None):
        if not color:
            color = const.RANDOM_COLOR()
        self.width = const.HALF_CAR_WIDTH
        self.height = const.HALF_CAR_HEIGHT
        super().__init__(game, crossroad, lane, side)
        # SIDES
        if self.spawnLane.isA('up'):
            self.spawnDirection = const.UP
            self.degrees = 270
        elif self.spawnLane.isA('down'):
            self.spawnDirection = const.DOWN
            self.degrees = 90
        elif self.spawnLane.isA('left'):
            self.spawnDirection = const.LEFT
            self.degrees = 180
        else:
            self.spawnDirection = const.RIGHT
            self.degrees = 0
        points = self.calcPoints()

        self.weight = const.CAR_WEIGHT
        super().initObject(color, points)

    # Having the inclination and the center, it's possible to calculate each of its wheels
    # Its wheels are used only for the calculation of the rotary movement
    def calcWheelsPosition(self):
        mysin = const.sin(const.radians(self.degrees))
        mycos = const.cos(const.radians(self.degrees))
        distX = self.width - const.CAR_WHEELS_POSITION
        distY = self.height - const.PROPORTION
        return (
            [self.position[0] + mysin*distY + mycos*distX,
                self.position[1] + mysin*distX - mycos*distY],
            [self.position[0] - mysin*distY + mycos*distX,
                self.position[1] + mysin*distX + mycos*distY],
            [self.position[0] - mysin*distY - mycos*distX,
                self.position[1] - mysin*distX + mycos*distY],
            [self.position[0] + mysin*distY - mycos*distX,
                self.position[1] - mysin*distX - mycos*distY]
        )

# Other specified vehicle
class Bus(Vehicle):
    def __init__(self, game, crossroad, lane, side = const.randint(0,1), color = None):
        if not color:
            color = const.RANDOM_COLOR()
        self.width = const.HALF_BUS_WIDTH
        self.height = const.HALF_BUS_HEIGHT
        super().__init__(game, crossroad, lane, side)
        # SIDES
        if self.spawnLane.isA('up'):
            self.spawnDirection = const.UP
            self.degrees = 270
        elif self.spawnLane.isA('down'):
            self.spawnDirection = const.DOWN
            self.degrees = 90
        elif self.spawnLane.isA('left'):
            self.spawnDirection = const.LEFT
            self.degrees = 180
        else:
            self.spawnDirection = const.RIGHT
            self.degrees = 0
        points = self.calcPoints()

        self.weight = const.BUS_WEIGHT
        super().initObject(color, points)

    # Having the inclination and the center, it's possible to calculate each of its wheels
    # Its wheels are used only for the calculation of the rotary movement
    def calcWheelsPosition(self):
        mysin = const.sin(const.radians(self.degrees))
        mycos = const.cos(const.radians(self.degrees))
        distX = self.width - const.BUS_WHEELS_POSITION
        distY = self.height - const.PROPORTION
        return (
            [self.position[0] + mysin*distY + mycos*distX,
                self.position[1] + mysin*distX - mycos*distY],
            [self.position[0] - mysin*distY + mycos*distX,
                self.position[1] + mysin*distX + mycos*distY],
            [self.position[0] - mysin*distY - mycos*distX,
                self.position[1] - mysin*distX + mycos*distY],
            [self.position[0] + mysin*distY - mycos*distX,
                self.position[1] - mysin*distX - mycos*distY]
        )

    # This vehicle can steer more than 33 deg
    def steer(self, power = 0):
        if power < -50:
            power = -50
        if power > 50:
            power = 50
        self.steerDeg = power
        # speed of steering
        difference = power - self.steerDeg
        if difference > 2:
            difference = 2
        if difference < -2:
            difference = -2
        self.steerDeg += difference