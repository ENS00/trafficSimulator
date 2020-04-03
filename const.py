from math import atan2, ceil, copysign, cos, degrees, fabs, pi, radians, sin, sqrt
from random import gauss,randint
import pygame

pygame.init()

# here there are all constants
# CAR_WH_RATIO
# CAR_DIM=36
TIME_SPEED = 200  # REAL 1s = GAME 200s
FPS = 60


# Variables
FLOAT_PRECISION = 5

# window dimension
W_WIDTH = 800
W_HEIGHT = 800
W_TITLE = 'Traffico'
PROPORTION = round(sqrt(W_WIDTH*W_HEIGHT)/200,FLOAT_PRECISION)   # proportion used for other calcs
DOUBLE_PROPORTION = PROPORTION*2
OCTUPLE_PROPORTION = PROPORTION*8
TWELVE_PROPORTION = PROPORTION*12
TIMEPANEL_SIZE = max(round(W_WIDTH/22.5),16)
HALF_CAR_WIDTH = PROPORTION*15/4      # dimension of the car
HALF_CAR_HEIGHT = PROPORTION*9/4      # dimension of the car
CAR_WHEELS_POSITION = PROPORTION*2    # distance of wheel from the rear (or the front) of the car
HALF_BUS_WIDTH = PROPORTION*25/4      # dimension of the bus 
HALF_BUS_HEIGHT = PROPORTION*9/4      # dimension of the bus
BUS_WHEELS_POSITION = PROPORTION*4    # distance of wheel from the rear (or the front) of the bus
TRUCK_WIDTH = PROPORTION*11         # dimension of the truck
TRUCK_HEIGHT = PROPORTION*13        # dimension of the truck
TRAILER_WIDTH = PROPORTION*20       # dimension of the trailer of the truck
TRAILER_HEIGHT = PROPORTION*11      # dimension of the trailer of the truck

ROAD_LINE_WIDTH = int(PROPORTION*11/2)  # width of the white line
ROAD_LINE_SIZE = int(DOUBLE_PROPORTION) # size of the white line
ROAD_LINE_THICKNESS = PROPORTION*200/11
STOPLINE_WIDTH = ROAD_LINE_SIZE+2
VEHICLE_RENDER = PROPORTION*TIME_SPEED/20000
VEHICLE_SPAWN_SPEED = 40
VEHICLE_FRICTION = 0.0004    # friction constant combined with car acceleration we get the maximum velocity of a vehicle
CAR_ACCELERATION = 10        # this number permits to have a maximum velocity of 90
CAR_WEIGHT = 50
BUS_WEIGHT = 56

SHAPE_RECT = 0
SHAPE_CIRCLE = 1

# TrafficLight positions
TL_DIST_X = 12+W_WIDTH/20
TL_DIST_Y = 15+W_HEIGHT/30
TL_SIZE = PROPORTION*25/2
TL_LIGHT_SIZE = round(PROPORTION*5/2)
TL_DISTANCES = TL_LIGHT_SIZE*2

# TrafficLight states
TL_OFF = 3
TL_GREEN = 2
TL_YELLOW = 1
TL_RED = 0

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
RANDOM_COLOR = lambda: RANDOM_COLOR_LIST[int(gauss(len(RANDOM_COLOR_LIST)/2,len(RANDOM_COLOR_LIST)/7))]
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
ICON_PATH = 'icon.ico'

# Font
FONT_PATH = 'C:\\Windows\\Fonts\\'
FONT_EXT = '.ttf'