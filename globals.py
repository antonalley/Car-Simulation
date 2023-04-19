# Define constants


############## FEEL FREE TO CHANGE THESE (MUST DELETE world.pickle IF CHANGED) ###################
NUM_CARS = 25
NUM_BUILDINGS = 12


WIDTH = 800
HEIGHT = 800
BLOCK_SIZE = 16
GRID_SIZE = 50
ROAD_FREQUENCY = 8
# ROAD_PROBABILITY = 1.0

FPS = 30
FPD = 3 # Frames per decision


############################################################


############ DONT CHANGE THESE #############################


# Define colors
GRASS_COLOR = (0, 128, 0)
ROAD_COLOR = (128, 128, 128)
BUILDING_COLOR = (212,175,55)
PARKING_LOT_COLOR = (0,0,0)
CAR_COLOR = (200,20,20)
LINE_COLOR = (255,255,255)
CRASH_COLOR = (70,10,10)

# Color map
cmap = {
    0: GRASS_COLOR,
    1: ROAD_COLOR,
    2: BUILDING_COLOR,
    3: PARKING_LOT_COLOR,
    4: CRASH_COLOR,
    5: CAR_COLOR,
}

OFF_GRID = None
GRASS = 0
ROAD = 1
BUILDING = 2
PARKING_LOT = 3
CRASH = 4
CAR = 5

# UP = (0, -1)
# DOWN = (0,1)
# RIGHT = (1, 0)
# LEFT = (-1, 0)
UP = (-1,0)
DOWN = (1,0)
LEFT = (0,-1)
RIGHT = (0,1)
STAY = (0,0)

### For Value Iteration: 

REWARD_VALUES = {
    BUILDING: 2500,
    ROAD: -1,
    PARKING_LOT: 0,
    GRASS: -1000,
    CRASH: -1000,
    CAR: -1000
}

ACTIONS = [UP, DOWN, LEFT, RIGHT]

##########################################################




