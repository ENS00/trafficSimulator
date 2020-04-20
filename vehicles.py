import const
import position
from objects import GameRect
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
                self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0] + const.QUADRUPLE_PROPORTION, currentLane.endLanePoints[rightS][1], 20, checkLeft=True))
                self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0] + const.TWENTYTWO_PROPORTION, currentLane.endLanePoints[rightS][1], 10, checkLeft=True))
            elif currentLane.isA('left'):
                self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0] - const.DOUBLE_PROPORTION, currentLane.endLanePoints[rightS][1], 35, checkTLight=True))
                self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0] - const.QUADRUPLE_PROPORTION, currentLane.endLanePoints[rightS][1], 20, checkLeft=True))
                self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0] - const.TWENTYTWO_PROPORTION, currentLane.endLanePoints[rightS][1], 10, checkLeft=True))
            elif currentLane.isA('up'):
                self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0], currentLane.endLanePoints[rightS][1] - const.DOUBLE_PROPORTION, 35, checkTLight=True))
                self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0], currentLane.endLanePoints[rightS][1] - const.QUADRUPLE_PROPORTION, 20, checkLeft=True))
                self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0], currentLane.endLanePoints[rightS][1] - const.TWENTYTWO_PROPORTION, 10, checkLeft=True))
            else:
                self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0], currentLane.endLanePoints[rightS][1] + const.DOUBLE_PROPORTION, 35, checkTLight=True))
                self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0], currentLane.endLanePoints[rightS][1] + const.QUADRUPLE_PROPORTION, 20, checkLeft=True))
                self.waypoints.append(position.Waypoint(currentLane.endLanePoints[rightS][0], currentLane.endLanePoints[rightS][1] + const.TWENTYTWO_PROPORTION, 10, checkLeft=True))
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
            if self.degrees>45 and self.degrees<=135:
                # right
                collideArea = self.game.graphic_lib.graphic.Rect(self.points[0][0],
                                                                self.points[0][1]-const.ROAD_LINE_THICKNESS*1.6,
                                                                const.TEN_PROPORTION,
                                                                const.ROAD_LINE_THICKNESS*2)
            elif self.degrees>135 and self.degrees<=225:
                # up
                collideArea = self.game.graphic_lib.graphic.Rect(self.points[0][0]-const.TEN_PROPORTION,
                                                                self.points[0][1]-const.ROAD_LINE_THICKNESS*1.6,
                                                                const.TEN_PROPORTION,
                                                                const.ROAD_LINE_THICKNESS*2)
            elif self.degrees>225 and self.degrees<=315:
                # left
                collideArea = self.game.graphic_lib.graphic.Rect(self.points[0][0]-const.TEN_PROPORTION,
                                                                self.points[0][1],
                                                                const.TEN_PROPORTION,
                                                                const.ROAD_LINE_THICKNESS*2)
            else:
                # down
                collideArea = self.game.graphic_lib.graphic.Rect(self.points[0][0],
                                                                self.points[0][1],
                                                                const.TEN_PROPORTION,
                                                                const.ROAD_LINE_THICKNESS*2)
            for vehicle in allvehicles:
                if vehicle.id == self.id:
                    continue
                if self.crossroad.hasPrecedence(self,vehicle) or (not self.crossroad.hasPrecedence(vehicle,self) and self.id<vehicle.id) and self.velocity<10:
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
            self.accelerate(0.5)

        elif objective.velocity < self.velocity:
            ntimes = distanceFromObjective / self.velocity*2 / const.VEHICLE_RENDER
            if ntimes:
                brake = self.velocity / ntimes / 4/self.power/self.power*self.weight*self.weight
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
            # if self.crossroad.hasPrecedence(self,vehicle) or (not self.crossroad.hasPrecedence(vehicle, self) and self.id<vehicle.id):
            #     continue
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
        view_w = const.TWELVE_PROPORTION
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