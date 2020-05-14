import const
from graphic_lib import Graphic
import gametime
import roads
import vehicles
from objects import IDassigner
from UI import TimePanel, VehicleCountPanel

from threading import Timer,Thread

# Everything is created here
class Game():
    # Creates window, inizializes time, id assigner
    def __init__(self):
        self.graphic_lib = Graphic(const.W_TITLE, const.W_WIDTH, const.W_HEIGHT, const.BACKGROUND_COLOR, const.ICON_PATH)

        self.idassigner = IDassigner()

        self.time = gametime.Gametime(self.graphic_lib, const.TIME_SPEED)
        self.timepanel = TimePanel(self, self.time)
        self.vehicleCountPanel = VehicleCountPanel(self)
        self.hourlyData = {
                           'vehicle_count': 0,
                           'accidents': 0
                          }

        self.currentHour = const.START_TIME//3600%24

        self.statusLights = None                            # it memorize the last update of traffic lights
        self.vehicles = []                                  # all active vehicles
        self.removeObjects = []                             # all vehicles to remove
        self.randomSpawn = self.getRandomSpawnTime()        # get time to wait until next spawn
        self.lastSpawn = 0                                  # when the last spawn happened
        self.currentTimeFromStart = 0
        self.count = 0                                      # used to control 2nd process and time speed

        self.continueProcess = True                         # control other process


    # Inizializes roads and draws crossroad (the crossroad object call for every object it owns the draw method)
    def drawField(self):
        # ROADS
        road_north = roads.Road(self, (const.W_WIDTH/2,0), (const.W_WIDTH/2,const.W_HEIGHT/2), name='North')
        road_east = roads.Road(self, (const.W_WIDTH,const.W_HEIGHT/2), (const.W_WIDTH/2,const.W_HEIGHT/2), name='East')
        road_south = roads.Road(self, (const.W_WIDTH/2,const.W_HEIGHT), (const.W_WIDTH/2,const.W_HEIGHT/2), name='South')
        road_west = roads.Road(self, (0,const.W_HEIGHT/2), (const.W_WIDTH/2,const.W_HEIGHT/2), name='West')

        # crossroad
        self.crossroad = roads.Crossroad(self, (road_north, road_east, road_south, road_west))

    # Draws everything and update properties
    def updateField(self):
        # Draws background
        self.graphic_lib.graphic.draw.rect(self.graphic_lib.screen, self.graphic_lib.background_color, (0, 0, self.graphic_lib.width, self.graphic_lib.height))
        [o.draw() for o in self.idassigner.objects]

        self.graphic_lib.update()
        self.timepanel.update()
        self.vehicleCountPanel.update()
        self.count = 0
        Thread(target=self.moveVehicles).start()

    # The repeated functions on each frame are here
    def loop(self):
        # Ignores input (just for now! We can only quit)
        events = self.graphic_lib.graphic.event.get()
        for event in events:
            if event.type == self.graphic_lib.graphic.QUIT:
                self.continueProcess = False
                const.OUTPUT_DEVICE.closeConnection()
                exit()

        self.currentTimeFromStart = self.time.getTime()

        # Every simulation hour
        if self.currentTimeFromStart//3600 %24 != self.currentHour:
            lastHour = self.currentTimeFromStart//3600 %24
            if const.PEAK_TIMES[lastHour] != const.PEAK_TIMES[self.currentHour]:
                # if hour changes and spawn probability is different we need to recalculate the next spawn
                self.randomSpawn = self.getRandomSpawnTime() - (self.currentTimeFromStart - self.lastSpawn)
            # register hourly report
            data = {
                    'measurement': 'dati_per_ora',
                    'tags': {
                             'start_hour': self.currentHour,
                             'end_hour': lastHour,
                            },
                    'fields': {
                               'generated_cars': self.hourlyData['vehicle_count'],
                               'accidents': self.hourlyData['accidents']
                              },
                    'time': self.time.getRealISODateTime()
                   }
            const.OUTPUT_DEVICE.writeData(data)
            # reset hourly data
            self.hourlyData['vehicle_count'] = 0
            self.hourlyData['accidents'] = 0
            self.currentHour = lastHour

        # print(self.time.getFps())# show FPS on console

        # Controls all trafficlights
        if self.currentTimeFromStart//const.TL_DURATION % 10 != self.statusLights:
            self.statusLights = self.currentTimeFromStart//const.TL_DURATION % 10
            self.crossroad.updateTLights()

        # Necessary to upload object states
        self.updateField()

    def spawnVehicle(self, entryL = None, exitL = None):
        if not entryL:
            entryL = self.crossroad.randomEntry()
        if not entryL:
            print('I: Could not spawn vehicle right now')
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
        self.hourlyData['vehicle_count'] += 1
        return newVehicle

    def getRandomSpawnTime(self):
        time = const.SPAWN_FREQUENCY
        while const.randint(1,101) > const.PEAK_TIMES[self.currentHour]:
            time += const.SPAWN_FREQUENCY
        return time

    # Adds an object to the list of objects to be removed
    def deleteObject(self, obj, accident = False):
        if obj not in self.removeObjects:
            self.removeObjects.append(obj)
            obj.totalTime = self.currentTimeFromStart - obj.spawnTime
            if not accident:
                data = {
                        'measurement': 'tempistiche',
                        'tags': {
                                 'vehicle_type': type(obj).__name__,
                                 'spawn_lane': obj.spawnLane,
                                 'objective_direction': obj.objectiveDirection
                                },
                        'fields': {
                                   'total_time': obj.totalTime,
                                   'total_stop_time': obj.totalTimeStop,
                                   'min_vel': round(obj.minVel),
                                   'max_vel': round(obj.maxVel)
                                  },
                        'time': self.time.getRealISODateTime()
                       }
                const.OUTPUT_DEVICE.writeData(data)

    def moveVehicles(self):
        while self.continueProcess and self.count < const.CONFIGURATION_SPEED:
            # Random spawn
            # TODO: use function that looks at peak times
            if self.currentTimeFromStart > self.lastSpawn + self.randomSpawn:
                self.lastSpawn = self.currentTimeFromStart + self.randomSpawn
                self.randomSpawn = self.getRandomSpawnTime()
                self.spawnVehicle()

            for i in self.vehicles:
                if i.arrived:
                    right_side_out = i.points[2][0] > const.W_WIDTH or i.points[2][1] > const.W_HEIGHT or i.points[2][0] < 0 or i.points[2][1] < 0
                    left_side_out = i.points[3][0] > const.W_WIDTH or i.points[3][1] > const.W_HEIGHT or i.points[3][0] < 0 or i.points[3][1] < 0
                    if left_side_out or right_side_out:
                        # Destroy object
                        self.deleteObject(i)
                    else:
                        i.drive(self.vehicles)
                else:
                    i.drive(self.vehicles)
                # Updates vehicle position and parameters (velocity, steer, acceleration etc.)
                i.update()

            for i in self.removeObjects:
                self.vehicles.remove(i)
                i.delete()
            self.removeObjects.clear()
            self.count += 1

    def registerAccident(self, vehicle1, vehicle2):
        print('I: Accident between %i and %i' %(vehicle1.id, vehicle2.id))
        self.hourlyData['accidents'] += 1
        data = {
                'measurement': 'incidenti',
                'tags': {
                         'vehicle1_type': type(vehicle1).__name__,
                         'vehicle1_spawn_lane': vehicle1.spawnLane,
                         'vehicle1_objective_direction': vehicle1.objectiveDirection,
                         'vehicle2_type': type(vehicle2).__name__,
                         'vehicle2_spawn_lane': vehicle2.spawnLane,
                         'vehicle2_objective_direction': vehicle2.objectiveDirection
                        },
                'fields': {
                           'vehicle1_position_x': vehicle1.position[0],
                           'vehicle1_position_y': vehicle1.position[1],
                           'vehicle2_position_x': vehicle2.position[0],
                           'vehicle2_position_y': vehicle2.position[1],
                           'vehicle1_degrees': round(vehicle1.degrees),
                           'vehicle2_degrees': round(vehicle2.degrees),
                           'vehicle1_velocity': round(vehicle1.velocity),
                           'vehicle2_velocity': round(vehicle2.velocity)
                          },
                'time': self.time.getRealISODateTime()
               }
        const.OUTPUT_DEVICE.writeData(data)
        self.deleteObject(vehicle1)
        self.deleteObject(vehicle2)
