import const
import graphic_lib
import gametime
import roads
import vehicles
from objects import IDassigner
from timepanel import TimePanel

# Everything is created here
class Game():
    # Creates window, inizializes time, id assigner
    def __init__(self):
        self.graphic_lib = graphic_lib.Graphic(const.W_TITLE, const.W_WIDTH, const.W_HEIGHT, const.BACKGROUND_COLOR, const.ICON_PATH)

        self.idassigner = IDassigner()

        self.time = gametime.Gametime(self.graphic_lib, const.TIME_SPEED)
        self.timepanel = TimePanel(self, self.time)

        self.statusLights = None                        # it memorize the last update of traffic lights
        self.vehicles = []                              # all active vehicles
        self.removeObjects = []                         # all vehicles to remove
        self.autoSpawn = True                           # enable autospawn randomly
        self.randomSpawn = const.randint(100,300)       # every x time spawn a vehicle
        self.lastSpawn = 0                              # when the last spawn happened

    # Inizializes roads and draws crossroad (the crossroad object call for every object it owns the draw method)
    def drawField(self):
        # ROADS
        road_north = roads.Road(self,(const.W_WIDTH/2,0),(const.W_WIDTH/2,const.W_HEIGHT/2))
        road_east = roads.Road(self,(const.W_WIDTH,const.W_HEIGHT/2),(const.W_WIDTH/2,const.W_HEIGHT/2))
        road_south = roads.Road(self,(const.W_WIDTH/2,const.W_HEIGHT),(const.W_WIDTH/2,const.W_HEIGHT/2))
        road_west = roads.Road(self,(0,const.W_HEIGHT/2),(const.W_WIDTH/2,const.W_HEIGHT/2))

        # crossroad
        self.crossroad = roads.Crossroad(self,(road_north,road_east,road_south,road_west))

    # Draws everything and update properties
    def updateField(self):
        # Updates vehicle position and parameters (velocity, steer, acceleration etc.)
        for i in self.vehicles:
            i.update()

        # Draws background
        self.graphic_lib.graphic.draw.rect(self.graphic_lib.screen, self.graphic_lib.background_color, (0, 0, self.graphic_lib.width, self.graphic_lib.height))
        [o.draw() for o in self.idassigner.objects]

        self.graphic_lib.update()
        self.timepanel.update()

    # The repeated functions on each frame are here
    def loop(self):
        # Ignores input (just for now! We can only quit)
        events = self.graphic_lib.graphic.event.get()
        for event in events:
            if event.type == self.graphic_lib.graphic.QUIT:
                exit()
        self.currentTimeFromStart = self.time.getTime()
        # print(self.time.getFps())# show FPS on console

        # Controls all trafficlights
        if self.currentTimeFromStart//480 % 10 != self.statusLights:
            self.statusLights = self.currentTimeFromStart//480 % 10
            self.crossroad.updateTLights()

        # Random spawn
        if self.autoSpawn and self.currentTimeFromStart > self.lastSpawn+self.randomSpawn:
            self.lastSpawn = self.currentTimeFromStart+self.randomSpawn
            self.randomSpawn = const.randint(100,300)
            self.spawnVehicle()

        # The vehicles are moving
        for i in self.vehicles:
            if i.arrived:
                right_side_out = i.points[2][0] > const.W_WIDTH or i.points[2][1] > const.W_HEIGHT or i.points[2][0] < 0 or i.points[2][1] < 0
                left_side_out = i.points[3][0] > const.W_WIDTH or i.points[3][1] > const.W_HEIGHT or i.points[3][0] < 0 or i.points[3][1] < 0
                if left_side_out or right_side_out:
                    # Destroy object
                    #print(i.id,'passed the crossroad in',self.time.getFormattedTime(currentTimeFromStart-i.spawnTime))
                    self.deleteObject(i)
                else:
                    i.drive(self.vehicles)
            else:
                i.drive(self.vehicles)

        for i in self.removeObjects:
            # print(i.id,'removed')
            self.vehicles.remove(i)
            i.delete()

        self.removeObjects.clear()

        # Necessary to upload object states
        self.updateField()

    def spawnVehicle(self, entryL = None, exitL = None):
        if not entryL:
            entryL = self.crossroad.randomEntry()
        if not entryL:
            print('Could not spawn vehicle right now')
            return
        if not exitL:
            exitL = self.crossroad.randomExit(entryL)
        if(const.randint(0,7) > 5):
            newVehicle = vehicles.Bus(self, self.crossroad, entryL)
        else:
            newVehicle = vehicles.Car(self, self.crossroad, entryL)
        # For now we set that all cars do not turn
        newVehicle.setObjective(exitL)#self.crossroad.getOppositeLanes(newVehicle,const.LEFT)[0])#
        self.vehicles.append(newVehicle)
        return newVehicle

    # Adds an object to the list of objects to be removed
    def deleteObject(self, obj):
        if obj not in self.removeObjects:
            self.removeObjects.append(obj)