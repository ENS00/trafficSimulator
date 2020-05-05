from math import atan2, ceil, copysign, cos, degrees, fabs, hypot, pi, radians, sin, sqrt
from random import gauss,randint
import pygame
# for read configuration.ini
from configparser import ConfigParser
from os import path

pygame.init()
CONF_FILE_PATH = r'configuration.ini'
config = ConfigParser()
# default values without using the file
config.read_dict({'Window': {'width': 800,
                             'height': 800,
                             'position_x': 350,
                             'position_y': 100
                            },
                  'Game': {'speed': 2,
                           'traffic_light_duration': 60
                          },
                  'Assets': {}
                })
# update values read from the file
config.read(CONF_FILE_PATH)
windowConfiguration = dict(config.items('Window'))
gameConfiguration = dict(config.items('Game'))
assetsConfiguration = dict(config.items('Assets'))


# fix wrong values
gameConfiguration['speed'] = int(gameConfiguration['speed'])
if gameConfiguration['speed'] < 1 or gameConfiguration['speed'] > 3:
    gameConfiguration['speed'] = 2

CONFIGURATION_SPEED = gameConfiguration['speed']
TIME_SPEED = 240*(CONFIGURATION_SPEED-1)   # REAL 1s = GAME (240+x)s
FPS = 300

# Variables
FLOAT_PRECISION = 5

# window position
W_POS_X = int(windowConfiguration['position_x'])
W_POS_Y = int(windowConfiguration['position_y'])

# window dimension
W_WIDTH = int(windowConfiguration['width'])
W_HEIGHT = int(windowConfiguration['height'])
W_TITLE = 'Traffico'
PROPORTION = round(sqrt(W_WIDTH*W_HEIGHT)/200,FLOAT_PRECISION)   # proportion used for other calcs
DOUBLE_PROPORTION = PROPORTION*2
QUADRUPLE_PROPORTION = PROPORTION*4
OCTUPLE_PROPORTION = PROPORTION*8
TEN_PROPORTION = PROPORTION*10
FIFTEEN_PROPORTION = PROPORTION*15
TWENTYTWO_PROPORTION = PROPORTION*22
THIRTY_PROPORTION = PROPORTION*30
TIMEPANEL_SIZE = max(round(W_WIDTH/22.5),16)
HALF_CAR_WIDTH = PROPORTION*15/4      # dimension of the car
HALF_CAR_HEIGHT = PROPORTION*9/4      # dimension of the car
CAR_WHEELS_POSITION = PROPORTION*2    # distance of wheel from the rear (or the front) of the car
HALF_BUS_WIDTH = PROPORTION*25/4      # dimension of the bus 
HALF_BUS_HEIGHT = PROPORTION*9/4      # dimension of the bus
BUS_WHEELS_POSITION = PROPORTION*4    # distance of wheel from the rear (or the front) of the bus
# TRUCK_WIDTH = PROPORTION*11         # dimension of the truck
# TRUCK_HEIGHT = PROPORTION*13        # dimension of the truck
# TRAILER_WIDTH = PROPORTION*20       # dimension of the trailer of the truck
# TRAILER_HEIGHT = PROPORTION*11      # dimension of the trailer of the truck

ROAD_LINE_WIDTH = int(PROPORTION*11/2)  # width of the white line
ROAD_LINE_SIZE = int(DOUBLE_PROPORTION) # size of the white line
ROAD_LINE_THICKNESS = PROPORTION*200/11
STOPLINE_WIDTH = ROAD_LINE_SIZE + 2
VEHICLE_RENDER = PROPORTION/800
VEHICLE_SPAWN_SPEED = 30
VEHICLE_FRICTION = 0.0004    # friction constant combined with car acceleration we get the maximum velocity of a vehicle
CAR_ACCELERATION = 10        # this number permits to have a maximum velocity of 90
CAR_WEIGHT = 50
BUS_WEIGHT = 56

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
TL_DURATION = int(gameConfiguration['traffic_light_duration'])*10

# Colors
BACKGROUND_COLOR = pygame.Color(255,255,112)
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
ORANGE = pygame.Color(255,160,0)
LIGHT_GREEN = pygame.Color(160,255,0)
WHITE_SMOKE = pygame.Color(245,245,245)
TRANSPARENT = pygame.Color(0,0,0,0)
RANDOM_COLOR_LIST = (ORANGE,YELLOW_ON,BLACK,WHITE_SMOKE,GRAY,BLUE,RED_ON,LIGHT_GREEN)
RANDOM_COLOR = lambda: RANDOM_COLOR_LIST[int(gauss(len(RANDOM_COLOR_LIST)/2, len(RANDOM_COLOR_LIST)/8))]
TL_COLORS = {
    TL_RED: (RED_OFF,RED_ON),
    TL_YELLOW: (YELLOW_OFF,YELLOW_ON),
    TL_GREEN: (GREEN_OFF,GREEN_ON),
}

# Orientation
HORIZONTAL = 0
VERTICAL = 1
UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3
FORWARD = 1

# Functions
def ROTATE(side, pos, angle):
    rad = radians(angle)
    cosTh = cos(rad)
    sinTh = sin(rad)
    _x = (side[0]-pos[0]) * cosTh - (side[1]-pos[1]) * sinTh
    _y = (side[0]-pos[0]) * sinTh + (side[1]-pos[1]) * cosTh
    side[0] = _x + pos[0]
    side[1] = _y + pos[1]

# Images
if 'icon_path' in assetsConfiguration:
    ICON_PATH = assetsConfiguration['icon_path']
else:
    ICON_PATH = None