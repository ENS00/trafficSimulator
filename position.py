from const import atan2,fabs,pi,sqrt

# A coordinate with a velocity, desired target and check traffic light attributes
class Waypoint():
    def __init__(self, x, y, velocity=None, desired=True, checkTLight=False):
        # Position of waypoint
        self.position = (x, y)
        # Target velocity
        self.velocity = velocity
        # Is this the point I was waiting for?
        self.desired = desired
        self.checkTLight = checkTLight

    # Gets a clone with same properties
    def clone(self):
        return Waypoint(self.position[0], self.position[1], self.velocity, self.desired, self.checkTLight)

# Gets a list of directions of a vector
def getDirection(pos1, pos2):
    rad = atan2(pos2[1]-pos1[1], pos2[0]-pos1[0])
    ret = []
    if rad > -pi/2+0.001 and rad < pi/2-0.001:
        ret.append('right')
    if (rad > pi/2+0.001 and rad < pi+0.001) or (rad > -pi-0.001 and rad < -pi/2-0.001):
        ret.append('left')
    if rad > 0.001 and rad < pi-0.001:
        ret.append('down')
    if rad > -pi+0.001 and rad < -0.001:
        ret.append('up')
    return ret

# Gets the center between a list of points [x,y]
def getCenter(point_list):
    center = [0,0]
    count = len(point_list)
    if count>0:
        for p in point_list:
            center[0] = center[0] + p[0]
            center[1] = center[1] + p[1]
        center[0]/=count
        center[1]/=count
        return center

# Basic pythagorean algorithm to calculate the distance between two points [x,y]
def distance(p1, p2):
    dif1 = p1[0] - p2[0]
    dif2 = p1[1] - p2[1]
    return sqrt(dif1*dif1 + dif2*dif2)

# Pos1 and pos2 define the line, it calculate the projection of the point [x,y] on the straight line
def projection(point, pos1, pos2):
    # Find a point in a line that is the nearest to another point
    # That point is the projection of the point in the line
    # Find line from 2 points
    if fabs(pos2[0] - pos1[0])>0:
        # y = mx + q
        m = (pos2[1] - pos1[1]) / (pos2[0] - pos1[0])
        q = pos1[1] - pos1[0]*m
        # Perpendicular
        if fabs(m)>0:
            # y = mx + q
            m2 = -1/m
            q2 = point[1] - point[0]*m2
            # Solution
            valx = (q2-q)/(m-m2)
            valy = m*valx + q
            projectionOnLine = [valx, valy]
        else:
            # y = c
            valx = point[0]
            valy = pos1[1]
            projectionOnLine = [valx, valy]
    else:
        # x = c
        valx = pos1[0]
        valy = point[1]
        projectionOnLine = [valx, valy]
    return projectionOnLine

# Is the projection of a point on a line A:B between points A and B?
def betweenProjection(point, pos1, pos2, tolerance=2):
    projectionPoint = projection(point,pos1,pos2)
    if (projectionPoint[0] <= pos1[0]+tolerance and projectionPoint[0] >= pos2[0]-tolerance) or (projectionPoint[0] >= pos1[0]-tolerance and projectionPoint[0] <= pos2[0]+tolerance):
        if projectionPoint[1] <= pos1[1]+tolerance and projectionPoint[1] >= pos2[1]-tolerance:
            return True
        if projectionPoint[1] >= pos1[1]-tolerance and projectionPoint[1] <= pos2[1]+tolerance:
            return True
    return False

# Calculates whether a point is in a rectangular area using the betweenProjection method
def getCollision(pos, points):
    return betweenProjection(pos,points[0],points[1],0) and betweenProjection(pos,points[1],points[2],0)

# Calculates if there is a collision between two rectangles, using the betweenProjection method for every point
def getRectCollision(points1, points2):
    side1_collision = betweenProjection(points1[0],points2[0],points2[1],0) and betweenProjection(points1[0],points2[1],points2[2],0)
    side2_collision = betweenProjection(points1[1],points2[0],points2[1],0) and betweenProjection(points1[1],points2[1],points2[2],0)
    side3_collision = betweenProjection(points1[2],points2[0],points2[1],0) and betweenProjection(points1[2],points2[1],points2[2],0)
    side4_collision = betweenProjection(points1[3],points2[0],points2[1],0) and betweenProjection(points1[3],points2[1],points2[2],0)
    first_check = side1_collision or side2_collision or side3_collision or side4_collision
    if first_check:
        return True
    side1_collision = betweenProjection(points2[0],points1[0],points1[1],0) and betweenProjection(points2[0],points1[1],points1[2],0)
    side2_collision = betweenProjection(points2[1],points1[0],points1[1],0) and betweenProjection(points2[1],points1[1],points1[2],0)
    side3_collision = betweenProjection(points2[2],points1[0],points1[1],0) and betweenProjection(points2[2],points1[1],points1[2],0)
    side4_collision = betweenProjection(points2[3],points1[0],points1[1],0) and betweenProjection(points2[3],points1[1],points1[2],0)
    return side1_collision or side2_collision or side3_collision or side4_collision