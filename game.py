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

        self.time = Gametime(self.graphic_lib)
        self.vehicles = []      # all active vehicles
        self.rain = const.GETRAIN()
        self.selectedVehicle = None

        # UI panels
        self.timePanel = self.uiManager.createPanel(self.time.getFormattedTime, const.MEDIUM)
        if const.SHOW_FPS:
            self.fpsPanel = self.uiManager.createPanel(lambda: 'FPS: ' + str(round(self.time.getFps() ,1)), const.SMALL)
        self.vehicleCountPanel = self.uiManager.createPanel(lambda: 'Current Speed: %i\nVehicle count: %i\nRain: %i mm          '%(self.time.speed, len(self.vehicles), self.rain), const.SMALL)
        self.increaseSpeedButton = self.uiManager.createPanel(lambda: 'Increase Speed', const.SMALL, True, lambda self: self.game.time.increaseSpeed())
        self.decreaseSpeedButton = self.uiManager.createPanel(lambda: 'Decrease Speed', const.SMALL, True, lambda self: self.game.time.decreaseSpeed())
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
        else:
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
            self.rain = const.GETRAIN()

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
        if self.currentTimeFromStart//const.TL_DURATION != self.statusLights:
            self.statusLights = self.currentTimeFromStart//const.TL_DURATION
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
        if const.randint(0,100) >= const.SPAWN_TYPE:
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
            return ('Vehicle details:\n\n  Type:\n  Velocity: 00.0 km/h\n\n'+
                    'Driver details:\n\n  Drunkenness: 0.00 %\n  Tiredness: 0.00 %\n  Senior: False\n  Tire Wear: 0.00 %\n  BROKEN BRAKES'
                   )
        str= ('Vehicle details:\n\n  Type: %s\n  Velocity: %s km/h\n\n'+
               'Driver details:\n\n  Drunkenness: %s %%\n  Tiredness: %s %%\n  Senior: %s\n  Tire Wear: %s %%'
               )%(type(self.selectedVehicle).__name__, round(self.selectedVehicle.velocity, 1),
                 round(self.selectedVehicle.drunkenness, 1), round(self.selectedVehicle.tiredness, 1),
                 self.selectedVehicle.senior, round(self.selectedVehicle.tire_wear, 1))
        if self.selectedVehicle.broken_brakes:
            return str + '\n  BROKEN BRAKES'
        return str

    def getRandomSpawnTime(self):
        time = const.SPAWN_FREQUENCY
        while const.randint(0,100) > const.PEAK_TIMES[self.currentHour]:
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
                                 'objective_direction': obj.objectiveDirection,
                                 'drunkenness': round(obj.drunkenness, 1),
                                 'tiredness': round(obj.tiredness, 1),
                                 'senior': obj.senior or 'False',
                                 'tire_wear': round(obj.tire_wear, 1),
                                 'broken_brakes': obj.broken_brakes,
                                 'rain_quantity': self.rain
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
                           'hours': self.time.getHours(),
                           'minutes': self.time.getMinutes(),
                           'vehicle1_position_x': vehicle1.position[0],
                           'vehicle1_position_y': vehicle1.position[1],
                           'vehicle2_position_x': vehicle2.position[0],
                           'vehicle2_position_y': vehicle2.position[1],
                           'vehicle1_degrees': round(vehicle1.degrees),
                           'vehicle2_degrees': round(vehicle2.degrees),
                           'vehicle1_velocity(km/h)': round(vehicle1.velocity),
                           'vehicle2_velocity(km/h)': round(vehicle2.velocity),
                           'vehicle1_drunkenness': round(vehicle1.drunkenness),
                           'vehicle2_drunkenness': round(vehicle2.drunkenness),
                           'vehicle1_tiredness': round(vehicle1.tiredness),
                           'vehicle2_tiredness': round(vehicle2.tiredness),
                           'vehicle1_senior': vehicle1.senior,
                           'vehicle2_senior': vehicle2.senior,
                           'vehicle1_tire_wear': round(vehicle1.tire_wear),
                           'vehicle2_tire_wear': round(vehicle2.tire_wear),
                           'vehicle1_broken_brakes': vehicle1.broken_brakes,
                           'vehicle2_broken_brakes': vehicle2.broken_brakes,
                           'rain_quantity': self.rain
                          },
                'time': self.time.getRealISODateTime()
               }
        self.deleteObject(vehicle1, True)
        self.deleteObject(vehicle2, True)
        const.OUTPUT_DEVICE.writeData(data)
        self.hourlyData['accidents'] += 1
