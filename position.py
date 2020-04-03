from const import atan2,fabs,pi,sqrt
class Position():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return 'Position({},{})'.format(self.x, self.y)

    def moveTo(self, x, y):
        if(hasattr(self,'sides')):
            for i in sides:
                i.x += self.x-x
                i.y += self.y-y
        self.x = x
        self.y = y

    def move(self, x, y):
        self.x += x
        self.y += y
    
    # this point is between two points?
    def between(self, pos1, pos2, tollerance=10):
        if (self.x <= pos1.x+tollerance and self.x >= pos2.x-tollerance) or (self.x >= pos1.x-tollerance and self.x <= pos2.x+tollerance):
            if self.y <= pos1.y+tollerance and self.y >= pos2.y-tollerance:
                return True
            if self.y >= pos1.y-tollerance and self.y <= pos2.y+tollerance:
                return True
        return False
        

    # starting from pos1, where i am going if i want to arrive in pos2?
    @staticmethod
    def getDirection(pos1, pos2):
        rad = atan2(pos2.y-pos1.y, pos2.x-pos1.x)
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
    
    def equals(self,pos):
        return hasattr(pos,'x') and hasattr(pos,'y') and self.x==pos.x and self.y==pos.y

    def clonePosition(self):
        return Position(self.x,self.y)

class Waypoint():
    def __init__(self, x, y, velocity=None, desidered=True, checkTLight=False):
        # position of waypoint
        self.position = (x, y)
        # target velocity
        self.velocity = velocity
        # is this the point I was waiting for?
        self.desidered = desidered
        self.checkTLight = checkTLight
    
    def clone(self):
        return Waypoint(self.position[0], self.position[1], self.velocity, self.desidered, self.checkTLight)


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

def distance(p1, p2):
    dif1 = p1[0] - p2[0]
    dif2 = p1[1] - p2[1]
    return sqrt(dif1*dif1 + dif2*dif2)

# pos1 and pos2 define the line
def projection(point, pos1, pos2):
    # find a point in a line that is the nearest to another point
    # that point is the projection of the point in the line
    # find line from 2 points
    if fabs(pos2[0] - pos1[0])>0:
        # y = mx + q
        m = (pos2[1] - pos1[1]) / (pos2[0] - pos1[0])
        q = pos1[1] - pos1[0]*m
        # perpendicular
        if fabs(m)>0:
            # y = mx + q
            m2 = -1/m
            q2 = point[1] - point[0]*m2
            # solution
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

def betweenProjection(point, pos1, pos2, tollerance=2):
    projectionPoint = projection(point,pos1,pos2)
    if (projectionPoint[0] <= pos1[0]+tollerance and projectionPoint[0] >= pos2[0]-tollerance) or (projectionPoint[0] >= pos1[0]-tollerance and projectionPoint[0] <= pos2[0]+tollerance):
        if projectionPoint[1] <= pos1[1]+tollerance and projectionPoint[1] >= pos2[1]-tollerance:
            return True
        if projectionPoint[1] >= pos1[1]-tollerance and projectionPoint[1] <= pos2[1]+tollerance:
            return True
    return False

def getCollision(pos, points):
    return betweenProjection(pos,points[0],points[1],0) and betweenProjection(pos,points[1],points[2],0)
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