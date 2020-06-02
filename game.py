import const
from graphic_lib import Graphic
from objects import IDassigner
from gametime import Gametime
from roads import Road, Crossroad
from vehicles import Bus, Car
from UI import UI, EventHandler

# Everything is created here
class Game():
    # Creates window, inizializes time, id assigner
    def __init__(self):
        self.graphic_lib = Graphic(const.W_TITLE, const.W_WIDTH, const.W_HEIGHT, const.BACKGROUND_COLOR, const.ICON_PATH)

        self.idassigner = IDassigner()
        self.uiManager = UI(self)
        self.eventHandler = EventHandler(self, self.uiManager)

        self.time = Gametime(self.graphic_lib, const.TIME_SPEED)
        self.vehicles = []      # all active vehicles
        self.selectedVehicle = None

        # UI panels
        self.timePanel = self.uiManager.createPanel(self.time.getFormattedTime, const.MEDIUM)
        if const.SHOW_FPS:
            self.fpsPanel = self.uiManager.createPanel(lambda: 'FPS: ' + str(round(self.time.getFps(),2)), const.SMALL)
        self.vehicleCountPanel = self.uiManager.createPanel(lambda: 'Vehicle count: ' + str(len(self.vehicles)), const.SMALL)
        self.editStatsButton = self.uiManager.createPanel(lambda: '--Edit stats--', const.SMALL, True, lambda self: self.game.statsPanel.changeVisibility())
        self.statsPanel = self.uiManager.createPanel(lambda: 'All stats', const.SMALL, False)
        self.vehicleDetailsPanel = self.uiManager.createPanel(lambda: self.selectedVehicleDetails(), const.SMALL, False, lambda self: self.changeVisibility(), const.RIGHT)

        self.hourlyData = {
                           'vehicle_count': 0,
                           'accidents': 0
                          }

        self.currentHour = const.START_TIME//3600%24

        self.statusLights = None                            # it memorize the last update of traffic lights
        self.removeObjects = []                             # all vehicles to remove
        self.randomSpawn = self.getRandomSpawnTime()        # get time to wait until next spawn
        self.lastSpawn = 0                                  # when the last spawn happened
        self.currentTimeFromStart = self.time.getTime()
        self.count = self.time.getFps()/100                 # used to control framerate and vehicle movement


    # Inizializes roads and draws crossroad (the crossroad object call for every object it owns the draw method)
    def drawField(self):
        road_north = Road(self, (const.W_WIDTH/2,0), (const.W_WIDTH/2,const.W_HEIGHT/2), name='North')
        road_east = Road(self, (const.W_WIDTH,const.W_HEIGHT/2), (const.W_WIDTH/2,const.W_HEIGHT/2), name='East')
        road_south = Road(self, (const.W_WIDTH/2,const.W_HEIGHT), (const.W_WIDTH/2,const.W_HEIGHT/2), name='South')
        road_west = Road(self, (0,const.W_HEIGHT/2), (const.W_WIDTH/2,const.W_HEIGHT/2), name='West')

        # crossroad
        self.crossroad = Crossroad(self, (road_north, road_east, road_south, road_west))
        if len(const.SHUTDOWN_HOURS):
            if self.crossroad.entries[0].tLight.on and (self.currentHour in const.SHUTDOWN_HOURS):
                self.crossroad.turnOnTLights(False)
            elif not self.crossroad.entries[0].tLight.on and not (self.currentHour in const.SHUTDOWN_HOURS):
                self.crossroad.turnOnTLights()

    # Draws everything and update properties
    def updateField(self):
        # Draws background
        self.graphic_lib.screen.fill(const.BACKGROUND_COLOR)
        [o.draw() for o in self.idassigner.objects]

        self.graphic_lib.update()
        self.uiManager.updatePanels()

    # The repeated functions on each frame are here
    def loop(self):
        # Handle all user input events
        self.eventHandler.handleEvents(self.graphic_lib.graphic.event.get())

        self.currentTimeFromStart = self.time.getTime()

        # Every simulation hour
        if (self.currentTimeFromStart + const.START_TIME)//3600 %24 != self.currentHour:
            newHour = (self.currentTimeFromStart + const.START_TIME)//3600 %24
            if const.PEAK_TIMES[newHour] != const.PEAK_TIMES[self.currentHour]:
                # if hour changes and spawn probability is different we need to recalculate the next spawn
                self.randomSpawn = self.getRandomSpawnTime() - (self.currentTimeFromStart - self.lastSpawn)
            # power off tlights at a certain time
            if len(const.SHUTDOWN_HOURS):
                if self.crossroad.entries[0].tLight.on and (newHour in const.SHUTDOWN_HOURS):
                    self.crossroad.turnOnTLights(False)
                elif not self.crossroad.entries[0].tLight.on and not (newHour in const.SHUTDOWN_HOURS):
                    self.crossroad.turnOnTLights()

            # register hourly report
            data = {
                    'measurement': 'dati_per_ora',
                    'tags': {
                             'start_hour': self.currentHour,
                             'end_hour': newHour,
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
            self.currentHour = newHour

        # Controls all trafficlights
        if self.currentTimeFromStart//const.TL_DURATION % 10 != self.statusLights:
            self.statusLights = self.currentTimeFromStart//const.TL_DURATION % 10
            self.crossroad.updateTLights()

        # Necessary to upload object states
        self.updateField()
        self.moveVehicles()
        self.count += self.time.getFps()/100

    def spawnVehicle(self, entryL = None, exitL = None):
        if not entryL:
            entryL = self.crossroad.randomEntry()
        if not entryL:
            #print('I: Could not spawn vehicle right now')
            return
        if not exitL:
            exitL = self.crossroad.randomExit(entryL)
        if const.randint(0,101) > const.SPAWN_TYPE:
            newVehicle = Bus(self, self.crossroad, entryL)
        else:
            newVehicle = Car(self, self.crossroad, entryL)
        # For now we set that all cars do not turn
        newVehicle.setObjective(exitL)#self.crossroad.getOppositeLanes(newVehicle,const.LEFT)[0])#
        self.vehicles.append(newVehicle)
        self.hourlyData['vehicle_count'] += 1
        return newVehicle

    def selectedVehicleDetails(self):
        if not self.selectedVehicle:
            return 'Vehicle details:\n\n  Type:\n  Velocity:\n'
        return 'Vehicle details:\n\n  Type: %s\n  Velocity: %s\n'%(type(self.selectedVehicle).__name__, self.selectedVehicle.velocity)

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
                                   'total_time': self.time.getFormattedTimeDelta(obj.totalTime),
                                   'total_stop_time': self.time.getFormattedTimeDelta(obj.totalTimeStop),
                                   'min_vel(km/h)': round(obj.minVel),
                                   'max_vel(km/h)': round(obj.maxVel)
                                  },
                        'time': self.time.getRealISODateTime()
                       }
                const.OUTPUT_DEVICE.writeData(data)

    def moveVehicles(self):
        while self.count>0:
            # Random spawn
            if self.currentTimeFromStart > self.lastSpawn + self.randomSpawn:
                self.lastSpawn = self.currentTimeFromStart
                self.randomSpawn = self.getRandomSpawnTime()
                self.spawnVehicle()

            for i in self.vehicles:
                if i not in self.removeObjects:
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
            self.count -= 1

    def registerAccident(self, vehicle1, vehicle2):
        print('I: Accident between %i and %i' %(vehicle1.id, vehicle2.id))
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
                           'vehicle1_velocity(km/h)': round(vehicle1.velocity),
                           'vehicle2_velocity(km/h)': round(vehicle2.velocity)
                          },
                'time': self.time.getRealISODateTime()
               }
        self.deleteObject(vehicle1, True)
        self.deleteObject(vehicle2, True)
        const.OUTPUT_DEVICE.writeData(data)
        self.hourlyData['accidents'] += 1
