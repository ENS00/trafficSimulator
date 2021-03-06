from math import atan2, ceil, copysign, cos, degrees, hypot, pi, radians, sin, sqrt
from numpy import random as rndP
from random import gauss,randint, betavariate
import pygame
# for read configuration.ini
from configparser import ConfigParser
from os import path
import output_connections as out_conn
from numpy import random as rndP

pygame.init()
CONF_FILE_PATH = r'configuration.ini'
config = ConfigParser(allow_no_value=True)
# default values without using the file
config.read_dict({
                  'Window': {
                             'width': 800,
                             'height': 800,
                             'position_x': 350,
                             'position_y': 100
                            },
                  'Game': {
                           'speed': 2,
                           'green_light_duration': 25,
                           'yellow_light_duration': 5,
                           'red_light_duration': 40,
                           'spawn_rate': 2,
                           'spawn_type': 70,
                           'start_time_hours': 0,
                           'start_time_minutes': 0,
                           'poweroff_tl': False,
                           'poweroff_tl_time': 23,
                           'poweron_tl_time': 5,
                           'rain_probability': 0
                          },
                  'Driver': {
                             'drunkenness_probability': 0,
                             'seniority_probability': 0,
                             'tiredness_probability': 0,
                             'broken_brakes_probability': 0,
                             'tire_wear': 0
                            },
                  'Connection': {
                                 'db_name': '',
                                 'db_host': '',
                                 'db_port': 8086,
                                 'csv_path': './output/'
                                },
                  'Assets': {},
                  'Style':{
                           'background_color': '150,255,110'
                          }
                })
# update values read from the file
config.read(CONF_FILE_PATH)
windowConfiguration = dict(config.items('Window'))
gameConfiguration = dict(config.items('Game'))
driverConfiguration = dict(config.items('Driver'))
connectionConfiguration = dict(config.items('Connection'))
assetsConfiguration = dict(config.items('Assets'))
styleConfiguration = dict(config.items('Style'))


# fix wrong values
gameConfiguration['speed'] = int(gameConfiguration['speed'])
if gameConfiguration['speed'] < 1 or gameConfiguration['speed'] > 3:
    gameConfiguration['speed'] = 2
gameConfiguration['spawn_rate'] = int(gameConfiguration['spawn_rate'])
if gameConfiguration['spawn_rate'] < 1 or gameConfiguration['spawn_rate'] > 3:
    gameConfiguration['spawn_rate'] = 2

gameConfiguration['spawn_type'] = int(gameConfiguration['spawn_type'])
if gameConfiguration['spawn_type'] < 0:
    gameConfiguration['spawn_type'] = 0
if gameConfiguration['spawn_type'] > 100:
    gameConfiguration['spawn_type'] = 100

gameConfiguration['rain_probability'] = int(gameConfiguration['rain_probability'])
if gameConfiguration['rain_probability'] < 0:
    gameConfiguration['rain_probability'] = 0
if gameConfiguration['rain_probability'] > 100:
    gameConfiguration['rain_probability'] = 100

def FIX0100(var):
    driverConfiguration[var] = int(driverConfiguration[var])
    if driverConfiguration[var] < 0:
        driverConfiguration[var] = 0
    if driverConfiguration[var] > 100:
        driverConfiguration[var] = 100

FIX0100('drunkenness_probability')
FIX0100('seniority_probability')
FIX0100('tiredness_probability')
FIX0100('broken_brakes_probability')
FIX0100('tire_wear')
driverConfiguration['broken_brakes_probability']/=100

gameConfiguration['start_time_hours'] = int(gameConfiguration['start_time_hours'])
gameConfiguration['start_time_minutes'] = int(gameConfiguration['start_time_minutes'])

connectionConfiguration['db_port'] = int(connectionConfiguration['db_port'])

SHUTDOWN_HOURS = []

if gameConfiguration['poweroff_tl'] and gameConfiguration['poweroff_tl'].lower() != 'false':
    POWEROFF_TL_TIME = int(gameConfiguration['poweroff_tl_time'])
    POWERON_TL_TIME = int(gameConfiguration['poweron_tl_time'])
    if POWEROFF_TL_TIME > POWERON_TL_TIME:
        for i in range(POWEROFF_TL_TIME,24):
            SHUTDOWN_HOURS.append(i)
        for i in range(0,POWERON_TL_TIME):
            SHUTDOWN_HOURS.append(i)
    else:
        for i in range(POWEROFF_TL_TIME,POWERON_TL_TIME):
            SHUTDOWN_HOURS.append(i)

styleConfiguration['background_color'] = [int(i) for i in styleConfiguration['background_color'].split(',')]



# Functions
def ROTATE(side, pos, angle):
    rad = radians(angle)
    cosTh = cos(rad)
    sinTh = sin(rad)
    _x = (side[0]-pos[0]) * cosTh - (side[1]-pos[1]) * sinTh
    _y = (side[0]-pos[0]) * sinTh + (side[1]-pos[1]) * cosTh
    side[0] = _x + pos[0]
    side[1] = _y + pos[1]

# Gets a list of directions of a vector
def GETDIRECTION(pos1, pos2):
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
def GETCENTER(point_list):
    center = [0,0]
    count = len(point_list)
    if count>0:
        for p in point_list:
            center[0] = center[0] + p[0]
            center[1] = center[1] + p[1]
        center[0]/=count
        center[1]/=count
        return center

# Calculate the distance between two points [x,y]
def DISTANCE(p1, p2):
    return hypot(p1[0]-p2[0], p1[1]-p2[1])

# Calculate angle of inclination in radians of 2 points [x,y]
def GETRADIANS(p1, p2):
    return atan2(p2[1] - p1[1], p2[0] - p1[0])

# Is the projection of a point on a line A:B between points A and B?
def BETWEENPROJECTION(point, pos1, pos2):
    # projectionPoint = PROJECTION(point,pos1,pos2)
    # instead of calling a function used only in this scope, we directly do all calculations here

    if pos2[0] - pos1[0]:
        m = (pos2[1] - pos1[1]) / (pos2[0] - pos1[0])
        q = pos1[1] - pos1[0]*m
        if m:
            # y = mx + q
            m2 = -1/m
            q2 = point[1] - point[0]*m2
            # Solution
            pp0 = (q2-q)/(m-m2)
            pp1 = m*pp0 + q
        else:
            # y = c
            pp0,pp1 = point[0], pos1[1]
    else:
        # x = c
        pp0,pp1 = pos1[0], point[1]

    if (pp0 <= pos1[0] and pp0 >= pos2[0]) or (pp0 >= pos1[0] and pp0 <= pos2[0]):
        if pp1 <= pos1[1] and pp1 >= pos2[1]:
            return True
        if pp1 >= pos1[1] and pp1 <= pos2[1]:
            return True

# Calculates whether a point is in a rectangular area using the betweenProjection method
def GETCOLLISION(pos, points):
    return BETWEENPROJECTION(pos, points[0], points[1]) and BETWEENPROJECTION(pos, points[1], points[2])

# Calculates if there is a collision between two rectangles, using the betweenProjection method for every point
def GETRECTCOLLISION(points1, points2):
    p10,p11,p12,p13 = points1
    p20,p21,p22,p23 = points2
    case1 = BETWEENPROJECTION(p10, p20, p21) and BETWEENPROJECTION(p10, p21, p22)
    case2 = BETWEENPROJECTION(p11, p20, p21) and BETWEENPROJECTION(p11, p21, p22)
    case3 = BETWEENPROJECTION(p12, p20, p21) and BETWEENPROJECTION(p12, p21, p22)
    case4 = BETWEENPROJECTION(p13, p20, p21) and BETWEENPROJECTION(p13, p21, p22)

    case5 = BETWEENPROJECTION(p20, p10, p11) and BETWEENPROJECTION(p20, p11, p12)
    case6 = BETWEENPROJECTION(p21, p10, p11) and BETWEENPROJECTION(p21, p11, p12)
    case7 = BETWEENPROJECTION(p22, p10, p11) and BETWEENPROJECTION(p22, p11, p12)
    case8 = BETWEENPROJECTION(p23, p10, p11) and BETWEENPROJECTION(p23, p11, p12)
    return case1 or case2 or case3 or case4 or case5 or case6 or case7 or case8

# Highest common factor
def HCFNAIVE(a, b):
    if b==0:
        return a
    else:
        return HCFNAIVE(b, a%b)


# Set main constants
CONFIGURATION_SPEED = gameConfiguration['speed']
TIME_SPEED = 150*CONFIGURATION_SPEED   # REAL 1s = GAME (240+x)s
FPS = 100+25*CONFIGURATION_SPEED        # limit FPS
START_TIME = gameConfiguration['start_time_hours']*3600 + gameConfiguration['start_time_minutes']*60

# Variables
FLOAT_PRECISION = 5
SHOW_FPS = False
# Control spawn
SPAWN_FREQUENCY = 150-25*gameConfiguration['spawn_rate']       # every X simulated seconds
PEAK_TIMES = [10,5,5,5,5,10,30,60,60,30,30,30,70,70,45,45,45,60,60,30,30,30,20,20]
# PEAK_TIMES = [80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80]
SPAWN_TYPE = gameConfiguration['spawn_type']

# window position
W_POS_X = int(windowConfiguration['position_x'])
W_POS_Y = int(windowConfiguration['position_y'])

# window dimension
W_WIDTH = int(windowConfiguration['width'])
W_HEIGHT = int(windowConfiguration['height'])
W_TITLE = 'Traffico'
PROPORTION = round(sqrt(W_WIDTH*W_HEIGHT)/200,FLOAT_PRECISION)   # proportion used for other calcs
HALF_PROPORTION = PROPORTION/2
DOUBLE_PROPORTION = PROPORTION*2
TRIPLE_PROPORTION = PROPORTION*3
QUADRUPLE_PROPORTION = PROPORTION*4
SEXTUPLE_PROPORTION = PROPORTION*6
OCTUPLE_PROPORTION = PROPORTION*8
TWELVE_PROPORTION = PROPORTION*12
FIFTEEN_PROPORTION = PROPORTION*15
TWENTYTWO_PROPORTION = PROPORTION*22
THIRTY_PROPORTION = PROPORTION*30

TIMEPANEL_SIZE = max(round(W_WIDTH/24),16)
HALF_CAR_WIDTH = PROPORTION*15/4        # dimension of the car
HALF_CAR_HEIGHT = PROPORTION*9/4        # dimension of the car
CAR_WHEELS_POSITION = DOUBLE_PROPORTION # distance of wheel from the rear (or the front) of the car
HALF_BUS_WIDTH = PROPORTION*25/4        # dimension of the bus
HALF_BUS_HEIGHT = PROPORTION*9/4        # dimension of the bus
BUS_WHEELS_POSITION = PROPORTION*4      # distance of wheel from the rear (or the front) of the bus

ROAD_LINE_WIDTH = int(PROPORTION*11/2)  # width of the white line
ROAD_LINE_SIZE = int(DOUBLE_PROPORTION) # size of the white line
ROAD_LINE_THICKNESS = PROPORTION*200/11
STOPLINE_WIDTH = ROAD_LINE_SIZE + 2
VEHICLE_RENDER = PROPORTION/1600*CONFIGURATION_SPEED
VEHICLE_SPAWN_SPEED = 30
VEHICLE_FRICTION = 0.0002    # friction constant combined with car acceleration we get the maximum velocity of a vehicle
VEHICLE_ACCELERATION = 11
CAR_WEIGHT = 50
BUS_WEIGHT = 56

WEATHER_FORECAST = []

# Driver
DRUNKENNESS = 0
TIREDNESS = 1
SENIORITY = 2
TIRE_WEAR = 3
BROKEN_BRAKES = 4
ACCEPTABLE_TIRE_WEAR = 40
def DRIVER_PARAMETER(param=DRUNKENNESS):
    if param==DRUNKENNESS and randint(0,100)<driverConfiguration['drunkenness_probability']:
        return betavariate(2, 6)*100
    if param==TIREDNESS and randint(0,100)<driverConfiguration['tiredness_probability']:
        return betavariate(2, 6)*100
    if param==SENIORITY:
        return randint(0, 100)<driverConfiguration['seniority_probability']
    if param==TIRE_WEAR:
        if randint(0, 100)<driverConfiguration['tire_wear']:
            return randint(ACCEPTABLE_TIRE_WEAR, 100)
        else:
            return randint(0, ACCEPTABLE_TIRE_WEAR)
    if param==BROKEN_BRAKES:
        return randint(0, 100)<driverConfiguration['broken_brakes_probability']
    return 0

# max 60mm
def GETRAINQUANTITYPERDAY():
    if not gameConfiguration['rain_probability']:
        return [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    x = rndP.poisson(lam=rndP.randint(gameConfiguration['rain_probability']/7, gameConfiguration['rain_probability']/7*6), size=24)
    x = list(map(lambda element: (element-25)*6/5 if element < 75 else 60, x))
    return list(map(lambda element: element if element > 0 else 0,x))

def GETRAIN():
    global WEATHER_FORECAST
    if len(WEATHER_FORECAST):
        return WEATHER_FORECAST.pop()
    WEATHER_FORECAST = GETRAINQUANTITYPERDAY()
    return WEATHER_FORECAST.pop()

SHAPE_RECT = 0
SHAPE_CIRCLE = 1

# TrafficLight positions
TL_DIST_X = 12 + W_WIDTH/20
TL_DIST_Y = 15 + W_HEIGHT/30
TL_SIZE = PROPORTION*25/2
TL_LIGHT_SIZE = round(PROPORTION*5/2)
TL_DISTANCES = TL_LIGHT_SIZE*2

# TrafficLight states
TL_OFF = 3
TL_GREEN = 2
TL_YELLOW = 1
TL_RED = 0

# TrafficLight duration
GREEN_LIGHT_DURATION = int(gameConfiguration['green_light_duration'])*5
YELLOW_LIGHT_DURATION = int(gameConfiguration['yellow_light_duration'])*5
RED_LIGHT_DURATION = int(gameConfiguration['red_light_duration'])*5
TL_DURATION = GREEN_LIGHT_DURATION + YELLOW_LIGHT_DURATION + RED_LIGHT_DURATION
MIN_LIGHT_COUNT = HCFNAIVE(HCFNAIVE(GREEN_LIGHT_DURATION, YELLOW_LIGHT_DURATION), RED_LIGHT_DURATION)

# Colors
COLOR_ROAD = pygame.Color(128,128,128)
WHITE = pygame.Color(255,255,255)
GREEN_ON = pygame.Color(0,255,0)
GREEN_OFF = pygame.Color(0,112,0)
YELLOW_ON = pygame.Color(255,255,0)
YELLOW_OFF = pygame.Color(112,112,0)
RED_ON = pygame.Color(255,0,0)
RED_OFF = pygame.Color(112,0,0)
BLUE = pygame.Color(0,0,160)
BLACK = pygame.Color(0,0,0)
GRAY = pygame.Color(80,80,80)
DARK_GRAY = pygame.Color(64,64,64)
LIGHT_GRAY = pygame.Color(220,220,220)
ORANGE = pygame.Color(255,160,0)
LIGHT_GREEN = pygame.Color(160,255,0)
WHITE_SMOKE = pygame.Color(245,245,245)
TRANSPARENT = pygame.Color(0,0,0,0)

TL_COLORS = {
    TL_RED: (RED_OFF,RED_ON),
    TL_YELLOW: (YELLOW_OFF,YELLOW_ON),
    TL_GREEN: (GREEN_OFF,GREEN_ON),
}
BACKGROUND_COLOR = pygame.Color(*styleConfiguration['background_color'])
BACKGROUND_PANEL = LIGHT_GRAY

RANDOM_COLOR_LIST = (ORANGE,YELLOW_ON,BLACK,WHITE_SMOKE,GRAY,BLUE,RED_ON,LIGHT_GREEN)
def RANDOM_COLOR():
    random = round(gauss(len(RANDOM_COLOR_LIST)/2, len(RANDOM_COLOR_LIST)/6))
    if random < 0:
        random = 0
    if random >= len(RANDOM_COLOR_LIST):
        random = len(RANDOM_COLOR_LIST)-1
    return RANDOM_COLOR_LIST[random]

# UI panels
SMALL = int(TIMEPANEL_SIZE/2)
MEDIUM = int(TIMEPANEL_SIZE)

# Orientation
HORIZONTAL = 0
VERTICAL = 1
UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3
FORWARD = 1

# Images
if 'icon_path' in assetsConfiguration:
    ICON_PATH = assetsConfiguration['icon_path']
else:
    ICON_PATH = None

# Connection
OUTPUT_DEVICE = None
if connectionConfiguration['db_name'] and connectionConfiguration['db_host']:
    # connection string to the output influxdb
    OUTPUT_DEVICE = out_conn.DBOutput(connectionConfiguration['db_host'], connectionConfiguration['db_name'], connectionConfiguration['db_port'])
if (not OUTPUT_DEVICE or not OUTPUT_DEVICE.flagConnection) and connectionConfiguration['csv_path']:
    del OUTPUT_DEVICE
    # connection string to the output csv file
    OUTPUT_DEVICE = out_conn.CSVOutput(connectionConfiguration['csv_path'])

if not OUTPUT_DEVICE or not OUTPUT_DEVICE.flagConnection:
    print('W: No output specified, data won\'t be saved in this session')
    del OUTPUT_DEVICE
    # instantiate null output
    OUTPUT_DEVICE = out_conn.Output()
