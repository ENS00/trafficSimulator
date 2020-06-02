import const
from objects import GameRect,Waypoint
# Most important and complex class of simulation, common properties for vehicle and decision-making are there
class Vehicle(GameRect):
    def __init__(self, game, crossroad, lane, side, power=const.CAR_ACCELERATION):
        self.game = game
        self.position = lane.startLanePoints[side]

        self.spawnTime = game.currentTimeFromStart
        self.startTimeStop = 0
        self.timeStop = 0 # how long am I waiting to leave
        self.totalTimeStop = 0 # how long am I waiting to leave

        self.velocity = const.VEHICLE_SPAWN_SPEED
        self.power = power
        self.steerDeg = 0
        self.acceleration = 0.5
        self.deceleration = 0
        self.minVel = 1000
        self.maxVel = 0

        self.crossroad = crossroad
        self.spawnLane = lane
        self.spawnSide = side
        self.arrived = False

    def initObject(self, color, points):
        super().__init__(self.game, color, points, self.degrees)
        super().draw()

    # Modifies all its parameters and position, according to its acceleration, deceleration and steering
    def update(self):
        self.velocity += self.acceleration/2*self.power/self.weight
        if self.velocity > 0:
            self.velocity -= self.deceleration/2*self.power/self.weight
        self.acceleration = 0
        self.deceleration = 0
        if self.velocity > 0:
            self.velocity = round(self.velocity - const.VEHICLE_FRICTION*const.ceil(self.velocity/10)*self.weight, const.FLOAT_PRECISION)
        if self.velocity > 0 and self.steerDeg:
            self.velocity = round(self.velocity - abs(self.steerDeg)*0.0005*pow(self.velocity,0.3), const.FLOAT_PRECISION)
        if self.velocity < 0:
            self.velocity = 0
            if not self.startTimeStop:
                self.startTimeStop = self.game.currentTimeFromStart
            self.timeStop = self.game.currentTimeFromStart - self.startTimeStop
        else:
            if self.velocity > self.maxVel:
                self.maxVel = self.velocity
            if self.velocity < self.minVel:
                self.minVel = self.velocity
            if self.startTimeStop and self.velocity>5:
                self.totalTimeStop += self.timeStop
                self.startTimeStop = 0
                self.timeStop = 0
            elif self.startTimeStop:
                self.timeStop = self.game.currentTimeFromStart - self.startTimeStop
            if self.steerDeg:
                determinant,center = self.calcDeterminant()
                if center:
                    # i do not need rear calc because it's fine use one of the rear wheels
                    # rotate the vehicle
                    self.rotate(const.copysign(self.velocity * const.VEHICLE_RENDER*75 / const.DISTANCE(center,self.position), self.steerDeg), center)
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
        if difference > 3:
            difference = 3
        if difference < -3:
            difference = -3
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
        currentLane, rightS = self.crossroad.getLaneFromPos(self.position)
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
                    self.waypoints.append(Waypoint(currentLane.endLanePoints[rightS][0]/2 + const.PROPORTION, currentLane.endLanePoints[rightS][1], 25))
                elif currentLane.isA('left'):
                    self.waypoints.append(Waypoint(currentLane.endLanePoints[rightS][0]*4/3 - const.PROPORTION, currentLane.endLanePoints[rightS][1], 25))
                elif currentLane.isA('up'):
                    self.waypoints.append(Waypoint(currentLane.endLanePoints[rightS][0], currentLane.endLanePoints[rightS][1]*4/3 - const.PROPORTION, 25))
                else:
                    self.waypoints.append(Waypoint(currentLane.endLanePoints[rightS][0], currentLane.endLanePoints[rightS][1]/2 + const.PROPORTION, 25))
            # end of current lane
            if currentLane.isA('right'):
                self.waypoints.append(Waypoint(currentLane.endLanePoints[rightS][0] + const.DOUBLE_PROPORTION, currentLane.endLanePoints[rightS][1], 35, checkTLight=True))
                self.waypoints.append(Waypoint(currentLane.endLanePoints[rightS][0] + const.QUADRUPLE_PROPORTION, currentLane.endLanePoints[rightS][1], 20, checkLeft=True))
                self.waypoints.append(Waypoint(currentLane.endLanePoints[rightS][0] + const.TWENTYTWO_PROPORTION, currentLane.endLanePoints[rightS][1], 10, checkLeft=True))
            elif currentLane.isA('left'):
                self.waypoints.append(Waypoint(currentLane.endLanePoints[rightS][0] - const.DOUBLE_PROPORTION, currentLane.endLanePoints[rightS][1], 35, checkTLight=True))
                self.waypoints.append(Waypoint(currentLane.endLanePoints[rightS][0] - const.QUADRUPLE_PROPORTION, currentLane.endLanePoints[rightS][1], 20, checkLeft=True))
                self.waypoints.append(Waypoint(currentLane.endLanePoints[rightS][0] - const.TWENTYTWO_PROPORTION, currentLane.endLanePoints[rightS][1], 10, checkLeft=True))
            elif currentLane.isA('up'):
                self.waypoints.append(Waypoint(currentLane.endLanePoints[rightS][0], currentLane.endLanePoints[rightS][1] - const.DOUBLE_PROPORTION, 35, checkTLight=True))
                self.waypoints.append(Waypoint(currentLane.endLanePoints[rightS][0], currentLane.endLanePoints[rightS][1] - const.QUADRUPLE_PROPORTION, 20, checkLeft=True))
                self.waypoints.append(Waypoint(currentLane.endLanePoints[rightS][0], currentLane.endLanePoints[rightS][1] - const.TWENTYTWO_PROPORTION, 10, checkLeft=True))
            else:
                self.waypoints.append(Waypoint(currentLane.endLanePoints[rightS][0], currentLane.endLanePoints[rightS][1] + const.DOUBLE_PROPORTION, 35, checkTLight=True))
                self.waypoints.append(Waypoint(currentLane.endLanePoints[rightS][0], currentLane.endLanePoints[rightS][1] + const.QUADRUPLE_PROPORTION, 20, checkLeft=True))
                self.waypoints.append(Waypoint(currentLane.endLanePoints[rightS][0], currentLane.endLanePoints[rightS][1] + const.TWENTYTWO_PROPORTION, 10, checkLeft=True))
            # start of new lane
            if lane.isA('right'):
                self.waypoints.append(Waypoint(lane.startLanePoints[rightS][0] - const.DOUBLE_PROPORTION, lane.startLanePoints[rightS][1], 18))
            elif lane.isA('left'):
                self.waypoints.append(Waypoint(lane.startLanePoints[rightS][0] + const.DOUBLE_PROPORTION, lane.startLanePoints[rightS][1], 18))
            elif lane.isA('up'):
                self.waypoints.append(Waypoint(lane.startLanePoints[rightS][0], lane.startLanePoints[rightS][1] + const.DOUBLE_PROPORTION, 18))
            else:
                self.waypoints.append(Waypoint(lane.startLanePoints[rightS][0], lane.startLanePoints[rightS][1] - const.DOUBLE_PROPORTION, 18))
        elif (currentLane.isA('left') and lane.isA('up')) or (currentLane.isA('up') and lane.isA('right')) or (currentLane.isA('right') and lane.isA('down')) or (currentLane.isA('down') and lane.isA('left')):
            self.objectiveDirection = const.RIGHT
            if(rightS == 1):
                # we are on the wrong side
                rightS = 0
                if currentLane.isA('right'):
                    self.waypoints.append(Waypoint(currentLane.endLanePoints[rightS][0]/2 + const.PROPORTION, currentLane.endLanePoints[rightS][1], 25))
                elif currentLane.isA('left'):
                    self.waypoints.append(Waypoint(currentLane.endLanePoints[rightS][0]*4/3 - const.PROPORTION, currentLane.endLanePoints[rightS][1], 25))
                elif currentLane.isA('up'):
                    self.waypoints.append(Waypoint(currentLane.endLanePoints[rightS][0], currentLane.endLanePoints[rightS][1]*4/3 - const.PROPORTION, 25))
                else:
                    self.waypoints.append(Waypoint(currentLane.endLanePoints[rightS][0], currentLane.endLanePoints[rightS][1]/2 + const.PROPORTION, 25))
            # end of current lane
            if currentLane.isA('right'):
                self.waypoints.append(Waypoint(currentLane.endLanePoints[rightS][0] + self.width, currentLane.endLanePoints[rightS][1], 25, checkTLight=True))
            elif currentLane.isA('left'):
                self.waypoints.append(Waypoint(currentLane.endLanePoints[rightS][0] - self.width, currentLane.endLanePoints[rightS][1], 25, checkTLight=True))
            elif currentLane.isA('up'):
                self.waypoints.append(Waypoint(currentLane.endLanePoints[rightS][0], currentLane.endLanePoints[rightS][1] - self.width, 25, checkTLight=True))
            else:
                self.waypoints.append(Waypoint(currentLane.endLanePoints[rightS][0], currentLane.endLanePoints[rightS][1] + self.width, 25, checkTLight=True))
            # start of new lane
            if lane.isA('right'):
                self.waypoints.append(Waypoint(lane.startLanePoints[rightS][0], lane.startLanePoints[rightS][1], 18))
            elif lane.isA('left'):
                self.waypoints.append(Waypoint(lane.startLanePoints[rightS][0], lane.startLanePoints[rightS][1], 18))
            elif lane.isA('up'):
                self.waypoints.append(Waypoint(lane.startLanePoints[rightS][0], lane.startLanePoints[rightS][1], 18))
            else:
                self.waypoints.append(Waypoint(lane.startLanePoints[rightS][0], lane.startLanePoints[rightS][1], 18))
        else:
            # exit is on the other lane
            self.objectiveDirection = const.FORWARD

        # exit of new lane
        self.waypoints.append(Waypoint(lane.endLanePoints[rightS][0], lane.endLanePoints[rightS][1], 90, checkTLight=True))

        #debug
        # for i in self.waypoints:
        #     self.game.graphic_lib.drawCircle(
        #             i.x,i.y,5, fill=const.RED_OFF)

    # This method defines all decision-making of the driver
    def drive(self, allvehicles):
        if not hasattr(self, 'waypoints') or len(self.waypoints) < 1:
            self.accelerate(1)
            return

        if self.graphic.collidepoint(self.waypoints[0].position):
            # we passed the target
            self.waypoints.pop(0)
            if len(self.waypoints) < 1:
                self.arrived = True
                self.accelerate(1)
                return

        objective = self.waypoints[0].clone()

        # radians that descripes inclination of direction from p1 to p2
        desiredDirection = const.GETRADIANS(self.position, objective.position)

        # if I am in the crossroad i check if I can turn left
        if objective.checkLeft:
            # check for other vehicles
            if self.degrees>45 and self.degrees<=135:
                # down
                collideArea = self.game.graphic_lib.graphic.Rect(self.points[0][0],
                                                                self.points[0][1],
                                                                const.ROAD_LINE_THICKNESS,
                                                                const.TWELVE_PROPORTION)
            elif self.degrees>135 and self.degrees<=225:
                # left
                collideArea = self.game.graphic_lib.graphic.Rect(self.points[0][0]-const.TWELVE_PROPORTION,
                                                                self.points[0][1],
                                                                const.TWELVE_PROPORTION,
                                                                const.ROAD_LINE_THICKNESS)
            elif self.degrees>225 and self.degrees<=315:
                # up
                collideArea = self.game.graphic_lib.graphic.Rect(self.points[0][0]-const.ROAD_LINE_THICKNESS,
                                                                self.points[0][1]-const.TWELVE_PROPORTION,
                                                                const.ROAD_LINE_THICKNESS,
                                                                const.TWELVE_PROPORTION)
            else:
                # right
                collideArea = self.game.graphic_lib.graphic.Rect(self.points[0][0],
                                                                self.points[0][1]-const.ROAD_LINE_THICKNESS,
                                                                const.TWELVE_PROPORTION,
                                                                const.ROAD_LINE_THICKNESS)

            if self.timeStop>600 and self.velocity<2:
                # he changes his mind and prefers to go straight
                lane = self.crossroad.getOppositeLanes(self)[0]
                self.waypoints = [Waypoint(lane.endLanePoints[1][0], lane.endLanePoints[1][1], 90, checkTLight=True)]
                return
            # debug turn area
            # self.game.graphic_lib.graphic.draw.rect(self.game.graphic_lib.screen, const.RED_ON, collideArea)
            # self.game.graphic_lib.graphic.display.update(collideArea)
            for vehicle in allvehicles:
                if vehicle.id == self.id:
                    continue
                # if self.timeStop>600 and self.velocity<2:# and (self.crossroad.hasPrecedence(self,vehicle) or (not self.crossroad.hasPrecedence(vehicle,self) and self.id<vehicle.id)):
                #     # he changes his mind and prefers to go straight
                #     lane = self.crossroad.getOppositeLanes(self)[0]
                #     self.waypoints = [Waypoint(lane.endLanePoints[1][0], lane.endLanePoints[1][1], 90, checkTLight=True)]
                #     return
                if vehicle.graphic.colliderect(collideArea):
                    self.brake(1)
                    return

        currentLane,laneN = self.crossroad.getLaneFromPos(self.points[0])
        if objective.checkTLight and currentLane and currentLane.isA('entry') and currentLane.tLight.on:
            # we need to check tlight
            currentEndLane = currentLane.endLanePoints[laneN]
            if currentLane.tLight.state == const.TL_RED:
                if currentLane.isA('up'):
                    objective = Waypoint(currentEndLane[0], currentEndLane[1] + const.OCTUPLE_PROPORTION, 0)
                elif currentLane.isA('down'):
                    objective = Waypoint(currentEndLane[0], currentEndLane[1] - const.OCTUPLE_PROPORTION, 0)
                elif currentLane.isA('left'):
                    objective = Waypoint(currentEndLane[0] + const.OCTUPLE_PROPORTION, currentEndLane[1], 0)
                else:
                    objective = Waypoint(currentEndLane[0] - const.OCTUPLE_PROPORTION, currentEndLane[1], 0)
            elif currentLane.tLight.state == const.TL_YELLOW:
                if currentLane.isA('up'):
                    objective1 = Waypoint(currentEndLane[0], currentEndLane[1] + const.OCTUPLE_PROPORTION, 0)
                elif currentLane.isA('down'):
                    objective1 = Waypoint(currentEndLane[0], currentEndLane[1] - const.OCTUPLE_PROPORTION, 0)
                elif currentLane.isA('left'):
                    objective1 = Waypoint(currentEndLane[0] + const.OCTUPLE_PROPORTION, currentEndLane[1], 0)
                else:
                    objective1 = Waypoint(currentEndLane[0] - const.OCTUPLE_PROPORTION, currentEndLane[1], 0)
                # will I pass tlight in n cycles?
                # if not canPassTL:
                objective = objective1
                objective.velocity = 0

        distanceFromObjective = const.DISTANCE(self.position, objective.position)

        if distanceFromObjective and objective.velocity > self.velocity:
            if self.velocity:
                accelerate = (objective.velocity-self.velocity) / self.velocity/2 / self.power*self.weight
                self.accelerate(accelerate)
            else:
                self.accelerate(0.25)
        elif distanceFromObjective > const.DOUBLE_PROPORTION and self.velocity<20:
            self.accelerate(0.4)

        elif objective.velocity < self.velocity and distanceFromObjective<100:
            ntimes = distanceFromObjective / self.velocity*2 / const.VEHICLE_RENDER
            if ntimes:
                brake = self.velocity / ntimes / 4/self.power/self.power*self.weight*self.weight
                self.brake(brake)

        avoidx = const.cos(desiredDirection)
        avoidy = const.sin(desiredDirection)

        # check for other vehicles
        magnitude = 0
        points = self.calcFrontArea()
        # self.game.graphic_lib.graphic.draw.circle(self.game.graphic_lib.screen,const.RED_OFF,(int(points[0][0]),int(points[0][1])),5)
        # self.game.graphic_lib.graphic.draw.circle(self.game.graphic_lib.screen,const.RED_OFF,(int(points[1][0]),int(points[1][1])),5)
        # self.game.graphic_lib.graphic.draw.circle(self.game.graphic_lib.screen,const.RED_OFF,(int(points[2][0]),int(points[2][1])),5)
        # self.game.graphic_lib.graphic.draw.circle(self.game.graphic_lib.screen,const.RED_OFF,(int(points[3][0]),int(points[3][1])),5)
        # self.game.graphic_lib.graphic.display.update()
        # collideArea = self.game.graphic_lib.graphic.Rect(points)
        for vehicle in allvehicles:
            if vehicle.id == self.id:
                continue
            # if self.crossroad.hasPrecedence(self,vehicle) or (not self.crossroad.hasPrecedence(vehicle, self) and self.id<vehicle.id):
            #     continue
            distance = const.DISTANCE(vehicle.position, self.position)
            if distance<100:
                if const.GETRECTCOLLISION(self.points, vehicle.points):
                    self.game.registerAccident(self, vehicle)
                    return
                if const.GETRECTCOLLISION(points, vehicle.points):
                    if self.timeStop<300 and self.velocity>8:
                        magnitude = (1+self.velocity)*4/distance
                        resAngle = const.GETRADIANS(self.position,vehicle.position)
                        avoidx -= const.cos(resAngle) / distance * vehicle.width*2
                        avoidy -= const.sin(resAngle) / distance * vehicle.height*2
                    elif self.timeStop>3000:
                        points = self.calcFrontArea(view_w = const.QUADRUPLE_PROPORTION, view_h = const.HALF_PROPORTION)
                        if not const.GETRECTCOLLISION(points, vehicle.points):
                            magnitude = 0
                            resAngle = const.GETRADIANS(self.position, vehicle.position)
                            avoidx -= const.cos(resAngle) / distance * vehicle.width*12
                            avoidy -= const.sin(resAngle) / distance * vehicle.height*12
                        else:
                            magnitude = 1
                    elif self.timeStop>300 or self.velocity<10:
                        points = self.calcFrontArea(view_w = const.QUADRUPLE_PROPORTION)
                        if const.GETRECTCOLLISION(points, vehicle.points):
                            magnitude = (1+self.velocity)*4/distance
                            resAngle = const.GETRADIANS(self.position, vehicle.position)
                            avoidx -= const.cos(resAngle) / distance * vehicle.width*2
                            avoidy -= const.sin(resAngle) / distance * vehicle.height*2

        if magnitude:
            self.brake(magnitude)

        rad = const.degrees(const.atan2(avoidy,avoidx))

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
        return [
            [position[0] + mysin*self.height + mycos*self.width,
                position[1] + mysin*self.width - mycos*self.height],
            [position[0] - mysin*self.height + mycos*self.width,
                position[1] + mysin*self.width + mycos*self.height],
            [position[0] - mysin*self.height - mycos*self.width,
                position[1] - mysin*self.width + mycos*self.height],
            [position[0] + mysin*self.height - mycos*self.width,
                position[1] - mysin*self.width - mycos*self.height]
        ]

    # It's an extention of the car to avoid collisions
    # def calcExtendedPoints(self, position=None, degrees=None):
    #     if not position:
    #         position = self.position
    #     if not degrees:
    #         degrees = self.degrees
    #     mysin = const.sin(const.radians(degrees))
    #     mycos = const.cos(const.radians(degrees))
    #     height = self.height + const.PROPORTION
    #     width = self.width + const.PROPORTION
    #     return (
    #         [round(position[0] + mysin*height + mycos*width, const.FLOAT_PRECISION),
    #             round(position[1] + mysin*width - mycos*height, const.FLOAT_PRECISION)],
    #         [round(position[0] - mysin*height + mycos*width, const.FLOAT_PRECISION),
    #             round(position[1] + mysin*width + mycos*height, const.FLOAT_PRECISION)],
    #         [round(position[0] - mysin*height - mycos*width, const.FLOAT_PRECISION),
    #             round(position[1] - mysin*width + mycos*height, const.FLOAT_PRECISION)],
    #         [round(position[0] + mysin*height - mycos*width, const.FLOAT_PRECISION),
    #             round(position[1] - mysin*width - mycos*height, const.FLOAT_PRECISION)]
    #     )

    # The front of the vehicle
    def calcFrontArea(self, view_h = const.PROPORTION, view_w = const.FIFTEEN_PROPORTION):
        mysin = const.sin(const.radians(self.degrees))
        mycos = const.cos(const.radians(self.degrees))
        points = self.calcPoints()
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
        if difference > 3:
            difference = 3
        if difference < -3:
            difference = -3
        self.steerDeg += difference
