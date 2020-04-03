import const
import graphic_lib
import gametime
import objects

class IDassigner():
    def __init__(self):
        self.__idassign = 0
        self.objects = []
    
    def getNewID(self, obj):
        self.__idassign += 1
        self.objects.append(obj)
        return self.__idassign
    
    def delete(self, obj):
        self.objects.remove(obj)

class TimePanel(objects.GameRect):
    def __init__(self, game, gametime, size = const.TIMEPANEL_SIZE):
        super().__init__(game, const.BLACK, ([const.W_WIDTH/30,const.W_HEIGHT/50],
                                             [size*2.5,const.W_HEIGHT/50],
                                             [size*2.5,size],
                                             [const.W_WIDTH/30,size]))
        self.gametime = gametime
        self.value = '00:00'
        self.size = size
    
    def update(self):
        self.value = self.gametime.getFormattedTime()
        self.draw()
    def draw(self):
        if not self.graphic:
            self.graphic = self.graphic_lib.graphic.draw.polygon(self.graphic_lib.screen, self.color, self.points)
            self.graphic_lib.updateAreas.append(self.graphic)
            self.position = self.graphic.topleft
        self.graphic = self.graphic_lib.drawText(self.position, self.value, self.size)

class Game():
    def __init__(self, fps = const.FPS):
        self.graphic_lib = graphic_lib.Graphic(const.W_TITLE,const.W_WIDTH,const.W_HEIGHT,const.BACKGROUND_COLOR,const.ICON_PATH)
        self.graphic_lib.setFps(fps)
        self.idassigner = IDassigner()

        self.statusLights = None
        self.time = gametime.Gametime(self.graphic_lib, const.TIME_SPEED, fps)
        self.timepanel = TimePanel(self, self.time)

        self.vehicles = []
        self.removeObjects = []
        self.randomSpawn = const.randint(150,800)# every x time spawn a vehicle
        self.spawnCount = 0

    def drawField(self):
        # ROADS
        road_north = objects.Road(self,(const.W_WIDTH/2,0),(const.W_WIDTH/2,const.W_HEIGHT/2))
        road_east = objects.Road(self,(const.W_WIDTH,const.W_HEIGHT/2),(const.W_WIDTH/2,const.W_HEIGHT/2))
        road_south = objects.Road(self,(const.W_WIDTH/2,const.W_HEIGHT),(const.W_WIDTH/2,const.W_HEIGHT/2))
        road_west = objects.Road(self,(0,const.W_HEIGHT/2),(const.W_WIDTH/2,const.W_HEIGHT/2))
        
        # crossroad
        self.crossroad = objects.Crossroad(self,(road_north,road_east,road_south,road_west))
        self.crossroad.turnOnTLights()

    def updateField(self):
        # drawing every object
        self.graphic_lib.graphic.draw.rect(self.graphic_lib.screen,self.graphic_lib.background_color,(0,0,self.graphic_lib.width,self.graphic_lib.height))
        [o.draw() for o in self.idassigner.objects]
        self.graphic_lib.update()
        self.timepanel.update()
        for i in self.vehicles:
            i.update()

    def loop(self):
        # ignore input (just for now! We can only quit)
        events = self.graphic_lib.graphic.event.get()
        for event in events:
            if event.type == self.graphic_lib.graphic.QUIT:
                exit()
        currentTimeFromStart = int(self.time.getTime())

        # control all trafficlights
        if currentTimeFromStart//480 % 10 != self.statusLights:
            self.statusLights = currentTimeFromStart//480 % 10
            self.crossroad.updateTLights()

        # random spawn
        if currentTimeFromStart > self.spawnCount+self.randomSpawn:
            self.spawnCount = currentTimeFromStart+self.randomSpawn
            # self.randomSpawn = const.randint(400,1400)
            newVehicle = self.spawnVehicle()

        # the vehicles are moving
        for i in self.vehicles:
            if i.arrived:
                right_side_out = i.points[2][0] > const.W_WIDTH or i.points[2][1] > const.W_HEIGHT or i.points[2][0] < 0 or i.points[2][1] < 0
                left_side_out = i.points[3][0] > const.W_WIDTH or i.points[3][1] > const.W_HEIGHT or i.points[3][0] < 0 or i.points[3][1] < 0
                if left_side_out or right_side_out:
                    # destroy object
                    self.deleteObject(i)
                else:
                    i.drive(self.vehicles)
            else:
                i.drive(self.vehicles)
                # print(i.velocity)

        for i in self.removeObjects:
            print(i.id,'removed')
            self.vehicles.remove(i)
            i.delete()

        self.removeObjects.clear()

        # necessary to upload object states
        self.updateField()

    def spawnVehicle(self, entryL = None, exitL = None):
        if not entryL:
            entryL = self.crossroad.randomEntry()
        if not exitL:
            exitL = self.crossroad.randomExit(entryL)#self.crossroad.getOppositeLanes(newVehicle,const.LEFT)[0])#
        if(const.randint(0,7) > 5):
            newVehicle = objects.Bus(self, self.crossroad, entryL)
        else:
            newVehicle = objects.Car(self, self.crossroad, entryL)
        # for now we set that all cars do not turn
        newVehicle.setObjective(exitL)
        self.vehicles.append(newVehicle)
        return newVehicle
    
    def deleteObject(self, obj):
        self.removeObjects.append(obj)