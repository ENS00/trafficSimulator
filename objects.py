import const
import position

class GameObject():
    def __init__(self, game, color, degrees):
        self.id = game.idassigner.getNewID(self)
        self.game = game
        self.graphic_lib = self.game.graphic_lib
        self.degrees = degrees
        self.graphic = None
        self.position = None
        self.color = color

    def draw(self):
        self.position = self.graphic.center
    
    def delete(self):
        self.game.idassigner.delete(self)

class GameRect(GameObject):
    def __init__(self, game, color, points, degrees = 0):
        super().__init__(game, color,degrees)
        self.points = points
    
    def draw(self):
        self.graphic = self.graphic_lib.graphic.draw.polygon(self.graphic_lib.screen, self.color, self.points)
        self.position = self.graphic.center

    def move(self, x, y):
        self.points[0][0] += x
        self.points[0][1] += y
        self.points[1][0] += x
        self.points[1][1] += y
        self.points[2][0] += x
        self.points[2][1] += y
        self.points[3][0] += x
        self.points[3][1] += y
    
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

class GameCircle(GameObject):
    def __init__(self, game, color, center, radius, degrees = 0):
        super().__init__(game, color, degrees)
        self.position = [round(center[0]), round(center[1])]
        self.radius = radius
    
    def draw(self):
        self.graphic = self.graphic_lib.graphic.draw.circle(self.graphic_lib.screen, self.color, self.position, self.radius)
        self.position = self.graphic.center
        
    def move(self, x, y):
        self.position[0] = round(x) + self.position[0]
        self.position[1] = round(y) + self.position[1]
            
# a graphic object but we can add tags that better describe the object
class RoadObject(GameRect):
    def __init__(self, game, color, points, tags=[]):
        super().__init__(game, color, points)
        self.tags = tags
        self.firstDraw = True

    def isA(self, prop):
        if prop in self.tags:
            return True
        return False

    def hasSameTags(self,obj):
        if True in [True for prop in self.tags if not prop in obj.tags]:
            return True
        return False
        
    # This class that defines objects that determine areas where we want update the screen
    def draw(self):
        super().draw()
        if self.firstDraw:
            self.firstDraw = False
            self.game.graphic_lib.updateAreas.append(self.graphic)

    def rotate(self, angle, center):
        self.game.graphic_lib.updateAreas.remove(self.graphic)
        self.firstDraw = True
        super().rotate(angle, center)

    def move(self, x, y):
        self.game.graphic_lib.updateAreas.remove(self.graphic)
        self.firstDraw = True
        super().move(x, y)

class Light(GameCircle):
    def __init__(self, game, tLight, position, color_type = const.TL_RED, state_on = False, radius = const.TL_LIGHT_SIZE):
        super().__init__(game, const.TL_COLORS[color_type][state_on], position, radius)
        self.color_type = color_type
        self.state_on = state_on
        self.tLight = tLight
        self.offset = (position[1]-tLight.points[0][1])

    def updatePosition(self):
        rad = const.radians(self.tLight.degrees)
        self.position = [round(-self.offset*const.sin(rad) + const.TL_DISTANCES*2/3*const.cos(rad) + self.tLight.points[0][0]),
                         round(self.offset*const.cos(rad) + const.TL_DISTANCES*2/3*const.sin(rad) + self.tLight.points[0][1])]

    # The only way to move this object is to move the tLight
    def move(self):
        return
    
    def turnOff(self):
        state_on = False
        self.color = const.TL_COLORS[self.color_type][False]

    def turnOn(self):
        state_on = True
        self.color = const.TL_COLORS[self.color_type][True]


class TrafficLight(RoadObject):
    def __init__(self, game, posred, direction=const.DOWN, state=const.TL_RED, on=False):
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

    def move(self, x, y):
        super().move(x,y)
        self.red.updatePosition()
        self.yellow.updatePosition()
        self.green.updatePosition()

    def rotate(self, angle):
        super().rotate(angle, self.red.position)
        self.red.updatePosition()
        self.yellow.updatePosition()
        self.green.updatePosition()

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


    def turnOn(self):
        self.on = True
        self.updateLights()

    def turnOff(self):
        self.on = False
        self.updateLights()

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

    def draw(self):
        super().draw()
        self.red.draw()
        self.yellow.draw()
        self.green.draw()

# THIS IS NOT A GRAPHICAL OBJECT
class Road():
    # now we can instantiate only double direction road
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

    def draw(self):
        self.entry.draw()
        self.exit.draw()


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
                i.setPosition((i.pstart[0]-self.dim,i.pstart[1]),i.pstop)
            elif i.isA('right'):
                i.setPosition((i.pstart[0]+self.dim,i.pstart[1]),i.pstop)
            elif i.isA('up'):
                i.setPosition((i.pstart[0],i.pstart[1]-self.dim),i.pstop)
            else:
                i.setPosition((i.pstart[0],i.pstart[1]+self.dim),i.pstop)
            i.crossroad = self
        for i in self.entries:
            if i.isA('left'):
                i.setPosition(i.pstart,(i.pstop[0]+self.dim,i.pstop[1]))
            elif i.isA('right'):
                i.setPosition(i.pstart,(i.pstop[0]-self.dim,i.pstop[1]))
            elif i.isA('up'):
                i.setPosition(i.pstart,(i.pstop[0],i.pstop[1]+self.dim))
            else:
                i.setPosition(i.pstart,(i.pstop[0],i.pstop[1]-self.dim))
            
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

    def updateTLights(self):
        for i in self.entries:
            i.tLight.update()

    def turnOnTLights(self, turnOn=True):
        if turnOn:
            [i.tLight.turnOn() for i in self.entries]
        else:
            [i.tLight.turnOff() for i in self.entries]

   # we get where the point is (in which specific lane)
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
    
    def randomEntry(self):
        return self.entries[const.randint(0,len(self.entries)-1)]

    def randomExit(self, entry = None):
        countElements = len(self.exits)
        if entry:
            roadId = self.entries.index(entry)
            elements = list(range(0,countElements))
            elements.remove(roadId)
            randomElement = elements[const.randint(0,countElements-2)]
            return self.exits[randomElement]
        return self.exits[const.randint(0,countElements-1)]

    def getOppositeLanes(self, vehicle, direction = const.FORWARD):
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
    
    def hasPrecedence(self,vehicle1,vehicle2):
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
        


class Vehicle(GameRect):
    def __init__(self, game, crossroad, lane, side, power = const.CAR_ACCELERATION):
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

    def update(self):
        self.velocity += self.acceleration*self.power/self.weight
        if self.velocity > 0:
            self.velocity -= self.deceleration*2*self.power/self.weight
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
                    self.rotate(const.copysign(self.velocity*const.VEHICLE_RENDER*75/position.distance(center,self.position),self.steerDeg), center)
                else:
                    radians = const.radians(self.degrees)
                    calc_x = round(const.cos(radians)*self.velocity*const.VEHICLE_RENDER, const.FLOAT_PRECISION)
                    calc_y = round(const.sin(radians)*self.velocity*const.VEHICLE_RENDER, const.FLOAT_PRECISION)
                    self.move(calc_x, calc_y)
            else:
                radians = const.radians(self.degrees)
                calc_x = round(const.cos(radians)*self.velocity*const.VEHICLE_RENDER, const.FLOAT_PRECISION)
                calc_y = round(const.sin(radians)*self.velocity*const.VEHICLE_RENDER, const.FLOAT_PRECISION)
                self.move(calc_x, calc_y)

    def steer(self, power = 0):
        if power < -33:
            power = -33
        if power > 33:
            power = 33
        # speed of steering
        difference = power - self.steerDeg
        if difference > 3:
            difference = 3
        if difference < -3:
            difference = -3
        self.steerDeg += difference

    def accelerate(self, power = 0.5):
        if power < 0:
            power = 0
        if power > 1:
            power = 1
        self.acceleration = power
        self.deceleration = 0

    def brake(self, power = 0.5):
        if power < 0:
            power = 0
        if power > 1:
            power = 1
        self.deceleration = power
        self.acceleration = 0
    # we tell to the vehicle where to go and we set a step by step guide to get there

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
                    self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0]/2+const.PROPORTION, currentLane.endLanePoints[rightS][1], 25))
                elif currentLane.isA('left'):
                    self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0]*4/3-const.PROPORTION, currentLane.endLanePoints[rightS][1], 25))
                elif currentLane.isA('up'):
                    self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0], currentLane.endLanePoints[rightS][1]*4/3-const.PROPORTION, 25))
                else:
                    self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0], currentLane.endLanePoints[rightS][1]/2+const.PROPORTION, 25))
            # end of current lane
            if currentLane.isA('right'):
                self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0]+const.TWELVE_PROPORTION, currentLane.endLanePoints[rightS][1], 25, checkTLight=True))
            elif currentLane.isA('left'):
                self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0]-const.TWELVE_PROPORTION, currentLane.endLanePoints[rightS][1], 25, checkTLight=True))
            elif currentLane.isA('up'):
                self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0], currentLane.endLanePoints[rightS][1]-const.TWELVE_PROPORTION, 25, checkTLight=True))
            else:
                self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0], currentLane.endLanePoints[rightS][1]+const.TWELVE_PROPORTION, 25, checkTLight=True))
            # start of new lane
            if lane.isA('right'):
                self.waypoints.append(position.Waypoint(lane.startLanePoints[rightS][0]-const.DOUBLE_PROPORTION, lane.startLanePoints[rightS][1], 18))
            elif lane.isA('left'):
                self.waypoints.append(position.Waypoint(lane.startLanePoints[rightS][0]+const.DOUBLE_PROPORTION, lane.startLanePoints[rightS][1], 18))
            elif lane.isA('up'):
                self.waypoints.append(position.Waypoint(lane.startLanePoints[rightS][0], lane.startLanePoints[rightS][1]+const.DOUBLE_PROPORTION, 18))
            else:
                self.waypoints.append(position.Waypoint(lane.startLanePoints[rightS][0], lane.startLanePoints[rightS][1]-const.DOUBLE_PROPORTION, 18))
        elif (currentLane.isA('left') and lane.isA('up')) or (currentLane.isA('up') and lane.isA('right')) or (currentLane.isA('right') and lane.isA('down')) or (currentLane.isA('down') and lane.isA('left')):
            self.objectiveDirection = const.RIGHT
            if(rightS == 1):
                # we are on the wrong side
                rightS = 0
                if currentLane.isA('right'):
                    self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0]/2+const.PROPORTION, currentLane.endLanePoints[rightS][1], 25))
                elif currentLane.isA('left'):
                    self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0]*4/3-const.PROPORTION, currentLane.endLanePoints[rightS][1], 25))
                elif currentLane.isA('up'):
                    self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0], currentLane.endLanePoints[rightS][1]*4/3-const.PROPORTION, 25))
                else:
                    self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0], currentLane.endLanePoints[rightS][1]/2+const.PROPORTION, 25))
            # end of current lane
            self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0], currentLane.endLanePoints[rightS][1], 25, checkTLight=True))
            # start of new lane
            if lane.isA('right'):
                self.waypoints.append(position.Waypoint(lane.startLanePoints[rightS][0]-const.PROPORTION, lane.startLanePoints[rightS][1], 18))
            elif lane.isA('left'):
                self.waypoints.append(position.Waypoint(lane.startLanePoints[rightS][0]+const.PROPORTION, lane.startLanePoints[rightS][1], 18))
            elif lane.isA('up'):
                self.waypoints.append(position.Waypoint(lane.startLanePoints[rightS][0], lane.startLanePoints[rightS][1]+const.PROPORTION, 18))
            else:
                self.waypoints.append(position.Waypoint(lane.startLanePoints[rightS][0], lane.startLanePoints[rightS][1]-const.PROPORTION, 18))
        else:
            # exit is on the other lane
            self.objectiveDirection = const.FORWARD

        # exit of new lane
        self.waypoints.append(position.Waypoint(lane.endLanePoints[rightS][0], lane.endLanePoints[rightS][1], 90, checkTLight=True))

        #debug
        # for i in self.waypoints:
        #     self.game.graphic_lib.drawCircle(
        #             i.x,i.y,5, fill=const.RED_OFF)
    # predict where it will be in t time

    def predict(self, t=0, objective=None):

        if not t and not objective:
            t=1

        velocity = self.velocity
        degrees = self.degrees
        calc_x = 0
        calc_y = 0
        myp = list(self.position)

        if not objective:
            for i in range(1, t+1):
                velocity += self.prev_acceleration*self.power/self.weight
                if velocity > 0:
                    velocity -= self.prev_deceleration*2*self.power/self.weight
                if velocity > 0:
                    velocity = round(velocity - const.VEHICLE_FRICTION*const.ceil(velocity/10)*self.weight, const.FLOAT_PRECISION)
                if velocity > 0 and self.steerDeg:
                    velocity = round(velocity - const.fabs(self.steerDeg)*0.0005*pow(velocity, 0.3), const.FLOAT_PRECISION)
                if velocity < 0:
                    velocity = 0
                else:
                    if self.steerDeg:
                        determinant,center = self.calcDeterminant(degrees)
                        if determinant:
                            degrees += determinant
                            if degrees > 360:
                                degrees-=360
                            if degrees < 0:
                                degrees+=360
                            # degrees += self.steerDeg*velocity / (velocity*velocity*1.25 + 1)
                    radians = const.radians(degrees)
                    calc_x += round(const.cos(radians) * velocity * const.VEHICLE_RENDER, const.FLOAT_PRECISION)
                    calc_y += round(const.sin(radians) * velocity * const.VEHICLE_RENDER, const.FLOAT_PRECISION)
            myp[0] += calc_x
            myp[1] += calc_y
        # predict a non-linear movement until it moves far away the desidered point
        else:
            if velocity < 0.2 and not self.prev_acceleration:
                if position.getCollision(objective.position, self.points):
                    return position.Waypoint(myp[0], myp[1], velocity)
                return position.Waypoint(myp[0], myp[1], velocity, False)
            last_distance = 100000
            count = 0
            while velocity > 0.1 and last_distance >= position.distance(myp,objective.position):
                count+=1
                last_distance = position.distance(myp,objective.position)
                # print('-------',myp,objective.position, velocity)
                velocity += self.prev_acceleration*self.power/self.weight
                if velocity > 0:
                    velocity -= self.prev_deceleration*2*self.power/self.weight
                if velocity > 0:
                    velocity = round(velocity - const.VEHICLE_FRICTION*const.ceil(velocity/10)*self.weight, const.FLOAT_PRECISION)
                if velocity > 0 and self.steerDeg:
                    velocity = round(velocity - const.fabs(self.steerDeg)*0.0005*pow(velocity, 0.3), const.FLOAT_PRECISION)
                if velocity < 0.2 and not self.prev_acceleration:
                    velocity = 0
                else:
                    if self.steerDeg:
                        determinant,center = self.calcDeterminant(degrees)
                        if determinant:
                            degrees += determinant
                            if degrees > 360:
                                degrees-=360
                            if degrees < 0:
                                degrees+=360
                    radians = const.radians(degrees)
                    calc_x = round(const.cos(radians) * velocity * const.VEHICLE_RENDER, const.FLOAT_PRECISION)
                    calc_y = round(const.sin(radians) * velocity * const.VEHICLE_RENDER, const.FLOAT_PRECISION)
                    myp[0] += calc_x
                    myp[1] += calc_y
            myp2 = list(myp)
            myp[0] -= calc_x
            myp[1] -= calc_y
            nearestPoint = position.projection(objective.position, myp, myp2)
            # we want that nearestPoint to be in between myp and myp2, if it is not we will use myp2
            if nearestPoint[0]<min(myp[0],myp2[0]) or nearestPoint[0]>max(myp[0],myp2[0]) or nearestPoint[1]<min(myp[1],myp2[1]) or nearestPoint[1]>max(myp[1],myp2[1]):
                nearestPoint = myp2
            
            if t:
                if t < count:#return myp instead?
                    return position.Waypoint(nearestPoint[0], nearestPoint[1], velocity, False)
                return position.Waypoint(myp[0], myp[1], velocity)
            sides = self.calcPoints(nearestPoint,degrees)
            # print(sides,objective.position,self.steerDeg,self.degrees,degrees)
            if position.getCollision(objective.position, sides):
                return position.Waypoint(nearestPoint[0], nearestPoint[1], velocity)
            return position.Waypoint(myp2[0], myp2[1], velocity, False)
        # print(t,self.calcPoints(myp,degrees),self.calcPoints(myp,degrees))
        return position.Waypoint(myp[0], myp[1], velocity)

    def predictCollide(self,vehicle,t=1,tollerance=6):
        velocity1 = self.velocity
        degrees1 = self.degrees
        velocity2 = vehicle.velocity
        degrees2 = vehicle.degrees
        
        myp1 = list(self.position)
        myp2 = list(vehicle.position)

        distance = position.distance(myp1,myp2)

        for i in range(1, t+1):
            velocity1 += self.prev_acceleration*self.power/self.weight
            velocity2 += vehicle.prev_acceleration*vehicle.power/vehicle.weight

            if velocity1 > 0:
                velocity1 -= self.prev_deceleration*2*self.power/self.weight
            if velocity2 > 0:
                velocity2 -= vehicle.prev_deceleration*2*vehicle.power/vehicle.weight

            if velocity1 > 0:
                velocity1 = velocity1 - const.VEHICLE_FRICTION*const.ceil(velocity1/10)*self.weight - const.fabs(self.steerDeg/10)
            if velocity2 > 0:
                velocity2 = velocity2 - const.VEHICLE_FRICTION*const.ceil(velocity2/10)*vehicle.weight - const.fabs(vehicle.steerDeg/10)

            if velocity1 > 0 and self.steerDeg:
                velocity1 = round(velocity1 - const.fabs(self.steerDeg)*0.0005*pow(velocity1, 0.3), const.FLOAT_PRECISION)
            if velocity2 > 0 and vehicle.steerDeg:
                velocity2 = round(velocity2 - const.fabs(self.steerDeg)*0.0005*pow(velocity2, 0.3), const.FLOAT_PRECISION)

            if velocity1 < 0.2 and not self.prev_acceleration:
                velocity1 = 0
                oldp1 = myp1
            else:
                if self.steerDeg:
                    determinant,center = self.calcDeterminant(degrees1)
                    if determinant:
                        degrees1 += determinant
                        if degrees1 > 360:
                            degrees1-=360
                        if degrees1 < 0:
                            degrees1+=360
                radians = const.radians(degrees1)
                oldp1 = list(myp1)
                myp1[0] += round(const.cos(radians) * velocity1 * const.VEHICLE_RENDER, const.FLOAT_PRECISION)
                myp1[1] += round(const.sin(radians) * velocity1 * const.VEHICLE_RENDER, const.FLOAT_PRECISION)

            if velocity2 < 0.2 and not vehicle.prev_acceleration:
                velocity2 = 0
                oldp2 = myp2
            else:
                if self.steerDeg:
                    determinant,center = self.calcDeterminant(degrees2)
                    if determinant:
                        degrees2 += determinant
                        if degrees2 > 360:
                            degrees2-=360
                        if degrees2 < 0:
                            degrees2+=360
                radians = const.radians(degrees2)
                oldp2 = list(myp2)
                myp2[0] += round(const.cos(radians) * velocity2 * const.VEHICLE_RENDER, const.FLOAT_PRECISION)
                myp2[1] += round(const.sin(radians) * velocity2 * const.VEHICLE_RENDER, const.FLOAT_PRECISION)

            newDistance = position.distance(myp1,myp2)
            if newDistance >= distance:
                # from now vehicles are moving away
                p1 = self.calcPoints(oldp1)
                p2 = vehicle.calcPoints(oldp2)
                return position.getRectCollision(p1,p2)
            else:
                distance = newDistance
        # vehicles will move even closer
        p1 = self.calcPoints(myp1)
        p2 = vehicle.calcPoints(myp2)
        return position.getRectCollision(p1,p2)
        # selfSide00 = Position(self.points[0].x + oldp1.x - self.position.x, self.points[0].y + oldp1.y - self.position.y)
        # selfSide01 = Position(self.points[1].x + oldp1.x - self.position.x, self.points[1].y + oldp1.y - self.position.y)
        # selfSide02 = Position(self.points[2].x + oldp1.x - self.position.x, self.points[2].y + oldp1.y - self.position.y)
        # selfSide03 = Position(self.points[3].x + oldp1.x - self.position.x, self.points[3].y + oldp1.y - self.position.y)
        # selfSide10 = Position(vehicle.points[0].x + oldp2.x - vehicle.position.x, vehicle.points[0].y + oldp2.y - vehicle.position.y)
        # selfSide11 = Position(vehicle.points[1].x + oldp2.x - vehicle.position.x, vehicle.points[1].y + oldp2.y - vehicle.position.y)
        # selfSide12 = Position(vehicle.points[2].x + oldp2.x - vehicle.position.x, vehicle.points[2].y + oldp2.y - vehicle.position.y)
        # if (selfSide00.betweenProjection(selfSide10,selfSide11,tollerance) and selfSide00.betweenProjection(selfSide11,selfSide12,tollerance)) or (selfSide01.betweenProjection(selfSide10,selfSide11,tollerance) and selfSide01.betweenProjection(selfSide11,selfSide12,tollerance)) or (selfSide02.betweenProjection(selfSide10,selfSide11,tollerance) and selfSide02.betweenProjection(selfSide11,selfSide12,tollerance)) or (selfSide03.betweenProjection(selfSide10,selfSide11,tollerance) and selfSide03.betweenProjection(selfSide11,selfSide12,tollerance)):
        #     return True
        # return False

    def drive(self, allvehicles):
        # here we got all decision-making of the driver
        if not hasattr(self, 'waypoints') or len(self.waypoints) < 1:
            return

        if self.graphic.collidepoint(self.waypoints[0].position):#position.distance(self.position, self.waypoints[0].position) < 7:
            # we passed the target
            self.waypoints.pop(0)
            if len(self.waypoints) < 1:
                self.arrived = True
                return

        objective = self.waypoints[0].clone()

        # radians that descripes inclination of direction from p1 to p2
        rad = const.degrees(const.atan2(objective.position[1] - self.position[1], objective.position[0] - self.position[0]))
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
                    objective1 = position.Waypoint(currentEndLane[0], currentEndLane[1] + const.PROPORTION,30)
                elif currentLane.isA('down'):
                    objective1 = position.Waypoint(currentEndLane[0], currentEndLane[1] - const.PROPORTION,30)
                elif currentLane.isA('left'):
                    objective1 = position.Waypoint(currentEndLane[0] + const.PROPORTION, currentEndLane[1],30)
                else:
                    objective1 = position.Waypoint(currentEndLane[0] - const.PROPORTION, currentEndLane[1],30)
                # will I pass tlight in n cycles?
                canPassTL = self.predict(20, objective1).desidered
                if not canPassTL:
                    objective = objective1
                    objective.velocity = 0

        distanceFromObjective = position.distance(self.position, objective.position)
        futureWaypoint = self.predict(objective = objective)
        # print('--',futureWaypoint.desidered)

        #USE PREV_ACC AND PREV_DEC
        if (objective.velocity > futureWaypoint.velocity) and futureWaypoint.desidered:
            if self.prev_acceleration>0.05:
                self.prev_acceleration += self.prev_acceleration/self.velocity
            else:
                self.prev_acceleration = 0.1
            # print(self.velocity, 'OK! :) but slow',(objective.velocity, futureWaypoint.velocity), self.prev_acceleration)
            self.accelerate(self.prev_acceleration)

        elif not futureWaypoint.desidered and (objective.velocity > futureWaypoint.velocity or not futureWaypoint.velocity):
            # print(self.velocity,'objective too far')
            # print(futureWaypoint.velocity,futureWaypoint.position,futureWaypoint.desidered,objective.position)
            if self.prev_deceleration>0.05 and distanceFromObjective<150:
                self.prev_deceleration -= self.prev_deceleration/3
                # print(self.velocity,'brake',self.prev_deceleration)
                self.brake(self.prev_deceleration)
            else:
                if self.prev_acceleration>0.05 and self.velocity>1:
                    self.prev_acceleration += self.velocity/20/self.prev_acceleration
                else:
                    if self.velocity>1:
                        self.prev_acceleration = 0.1
                    else:
                        self.prev_acceleration = 0.4
                # print(self.velocity,'accelerate',self.prev_acceleration)
                self.accelerate(self.prev_acceleration)

        elif distanceFromObjective < 3*self.velocity and (objective.velocity < futureWaypoint.velocity or not futureWaypoint.desidered):
            if self.prev_acceleration>0.05 and distanceFromObjective>150:
                self.prev_acceleration -= self.prev_acceleration/3
                # print(self.velocity,'slow',self.prev_acceleration)
                self.accelerate(self.prev_acceleration)
            else:
                if self.prev_deceleration>0.05:
                    self.prev_deceleration += self.velocity/10/self.prev_deceleration
                else:
                    self.prev_deceleration = self.velocity/distanceFromObjective
                # print(self.velocity,'brake',self.prev_deceleration)
                self.brake(self.prev_deceleration)

        else:
            if self.prev_acceleration:
                self.accelerate(self.prev_acceleration)
            else:
                self.brake(self.prev_deceleration)
            # print(self.prev_acceleration,self.prev_deceleration,futureWaypoint.velocity,futureWaypoint.position,futureWaypoint.desidered,objective.position)

        
        # check for vehicles with more precedence
        for vehicle in allvehicles:
            if vehicle.id != self.id:
                if position.distance(vehicle.position,self.position)<300 and (self.crossroad.hasPrecedence(vehicle,self) or (not self.crossroad.hasPrecedence(self,vehicle) and vehicle.id<self.id)):
                    ## wanna explode vehicles if there is an accident?? ##
                    if position.getRectCollision(self.points,vehicle.points):
                        print('Accident between %i and %i' %(self.id,vehicle.id))
                        self.game.deleteObject(self)
                        self.game.deleteObject(vehicle)
                    if self.predictCollide(vehicle,80):#position.distance(vehicle.position,self.position)<180 or
                        self.brake(1)# preventive action to avoid collision
                        print('WARNING',self.id)
                        break

    # returns determinant and if possible center of a rotation
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

    
class Car(Vehicle):
    def __init__(self, game, crossroad, lane, side=const.randint(0,1), color=None):
        if not color:
            color = const.RANDOM_COLOR()
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
            
        super().initObject(color, points)
        self.weight = const.CAR_WEIGHT

    def calcWheelsPosition(self):
        mysin = const.sin(const.radians(self.degrees))
        mycos = const.cos(const.radians(self.degrees))
        distX = const.HALF_CAR_WIDTH-const.CAR_WHEELS_POSITION
        distY = const.HALF_CAR_HEIGHT-const.PROPORTION
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

    def calcPoints(self, position=None, degrees=None):
        if not position:
            position = self.position
        if not degrees:
            degrees = self.degrees
        mysin = const.sin(const.radians(degrees))
        mycos = const.cos(const.radians(degrees))
        return (
                [round(position[0] + mysin*const.HALF_CAR_HEIGHT + mycos*const.HALF_CAR_WIDTH, const.FLOAT_PRECISION),
                 round(position[1] + mysin*const.HALF_CAR_WIDTH - mycos*const.HALF_CAR_HEIGHT, const.FLOAT_PRECISION)],
                [round(position[0] - mysin*const.HALF_CAR_HEIGHT + mycos*const.HALF_CAR_WIDTH, const.FLOAT_PRECISION),
                 round(position[1] + mysin*const.HALF_CAR_WIDTH + mycos*const.HALF_CAR_HEIGHT, const.FLOAT_PRECISION)],
                [round(position[0] - mysin*const.HALF_CAR_HEIGHT - mycos*const.HALF_CAR_WIDTH, const.FLOAT_PRECISION),
                 round(position[1] - mysin*const.HALF_CAR_WIDTH + mycos*const.HALF_CAR_HEIGHT, const.FLOAT_PRECISION)],
                [round(position[0] + mysin*const.HALF_CAR_HEIGHT - mycos*const.HALF_CAR_WIDTH, const.FLOAT_PRECISION),
                 round(position[1] - mysin*const.HALF_CAR_WIDTH - mycos*const.HALF_CAR_HEIGHT, const.FLOAT_PRECISION)]
            )
                                                      
class Bus(Vehicle):
    def __init__(self, game, crossroad, lane, side=const.randint(0,1), color=const.RANDOM_COLOR()):
        super().__init__(game, crossroad, lane, side)#, const.BUS_ACCELERATION)
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

        super().initObject(color, points)
        self.weight = const.BUS_WEIGHT
        
    def calcWheelsPosition(self):
        mysin = const.sin(const.radians(self.degrees))
        mycos = const.cos(const.radians(self.degrees))
        distX = const.HALF_BUS_WIDTH-const.CAR_WHEELS_POSITION
        distY = const.HALF_BUS_HEIGHT-const.PROPORTION
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

    def calcPoints(self, position=None, degrees=None):
        if not position:
            position = self.position
        if not degrees:
            degrees = self.degrees
        mysin = const.sin(const.radians(degrees))
        mycos = const.cos(const.radians(degrees))
        return (
                [round(position[0] + mysin*const.HALF_BUS_HEIGHT + mycos*const.HALF_BUS_WIDTH, const.FLOAT_PRECISION),
                 round(position[1] + mysin*const.HALF_BUS_WIDTH - mycos*const.HALF_BUS_HEIGHT, const.FLOAT_PRECISION)],
                [round(position[0] - mysin*const.HALF_BUS_HEIGHT + mycos*const.HALF_BUS_WIDTH, const.FLOAT_PRECISION),
                 round(position[1] + mysin*const.HALF_BUS_WIDTH + mycos*const.HALF_BUS_HEIGHT, const.FLOAT_PRECISION)],
                [round(position[0] - mysin*const.HALF_BUS_HEIGHT - mycos*const.HALF_BUS_WIDTH, const.FLOAT_PRECISION),
                 round(position[1] - mysin*const.HALF_BUS_WIDTH + mycos*const.HALF_BUS_HEIGHT, const.FLOAT_PRECISION)],
                [round(position[0] + mysin*const.HALF_BUS_HEIGHT - mycos*const.HALF_BUS_WIDTH, const.FLOAT_PRECISION),
                 round(position[1] - mysin*const.HALF_BUS_WIDTH - mycos*const.HALF_BUS_HEIGHT, const.FLOAT_PRECISION)]
            )
    # BUS can steer more than 33 deg
    def steer(self, power = 0):
        if power < -60:
            power = -60
        if power > 60:
            power = 60
        self.steerDeg = power
        # speed of steering
        difference = power - self.steerDeg
        if difference > 4:
            difference = 4
        if difference < -4:
            difference = -4
        self.steerDeg += difference