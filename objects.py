import const

# ID assigner uniquely identifies an object
class IDassigner():
    def __init__(self):
        self.__idassign = 0
        self.objects = []

    # Gets an unique number, starting from 1
    def getNewID(self, obj):
        self.__idassign += 1
        self.objects.append(obj)
        return self.__idassign

    # Removes the object from the listed game items
    def delete(self, obj):
        self.objects.remove(obj)

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