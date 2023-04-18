import random
from globals import *
import numpy as np

def is_valid_state(x, y):
    return 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE


def get_reward(x, y, world):
    return REWARD_VALUES[world[x][y]]

def get_next_state_reward(y, x, world, values, discount_factor):
    if world[y][x] in [BUILDING, GRASS, CRASH, CAR]:
        return get_reward(y, x, world)
    else:
        return get_reward(y, x, world) + discount_factor * values[y][x]
    
def next_pos(world, current, dir):
    p = (current[0] + dir[0], current[1] + dir[1])
    if p[0] < 0 or p[1] < 0 or p[0] > len(world) - 1 or p[1] > len(world[0]) - 1:
        return OFF_GRID
    return p

def next_spot(world, current, dir):
    try:
        p = next_pos(world, current, dir)
        if p == OFF_GRID: return OFF_GRID
        spot = world[p[0]][p[1]]
    except IndexError:
        return OFF_GRID
    
    return spot
    
def get_possible_moves(pos, world):
        possible_moves = []

        # Make sure not in parking lot before following normal rules
        if next_spot(world, pos, STAY) not in [BUILDING, PARKING_LOT]:
            # Check which direction you can go if you are in a lane, else if you are in an intersection randomly choose
            if next_spot(world, pos, UP) in [OFF_GRID, GRASS, BUILDING, PARKING_LOT] and next_spot(world, pos, LEFT) is not None:
                possible_moves.append(LEFT)
                # Check if on top edge intersection:
                if next_spot(world, pos, (2, 0)) == ROAD and next_spot(world, pos, (2, -1)) == GRASS:
                    possible_moves.append(DOWN)
            elif next_spot(world, pos, DOWN) in [OFF_GRID, GRASS, BUILDING, PARKING_LOT] and next_spot(world, pos, RIGHT) is not None:
                possible_moves.append(RIGHT)
                # Check if on bottom edge intersection:
                if next_spot(world, pos, (-2, 0)) == ROAD and next_spot(world, pos, (-2, 1)) == GRASS:
                    possible_moves.append(UP)
            elif next_spot(world, pos, RIGHT) in [OFF_GRID, GRASS, BUILDING, PARKING_LOT] and next_spot(world, pos, UP) is not None:
                possible_moves.append(UP)
                # Check if on right edge intersection:
                if next_spot(world, pos, (0, -2)) == ROAD and next_spot(world, pos, (-1, -2)) == GRASS:
                    possible_moves.append(LEFT)
            elif next_spot(world, pos, LEFT) in [OFF_GRID, GRASS, BUILDING, PARKING_LOT] and next_spot(world, pos, DOWN) is not None:
                possible_moves.append(DOWN)
                # Check if on left edge intersection:
                if next_spot(world, pos, (0, 2)) == ROAD and next_spot(world, pos, (1, 2)) == GRASS:
                    possible_moves.append(RIGHT)

            else:
                #Check in the intersection what directions it can go
                if next_spot(world, pos, (-1,-1)) in [GRASS, BUILDING, PARKING_LOT]:
                    # If its in the bottom right corner
                    if next_spot(world, pos, (2, 0)) == OFF_GRID:
                        possible_moves = [LEFT]
                    else:
                        possible_moves = [DOWN, LEFT]
                elif next_spot(world, pos, (1, -1)) in [GRASS, BUILDING, PARKING_LOT]:
                    # if its in the top right corner
                    if next_spot(world, pos, (0, -2)) == OFF_GRID:
                        possible_moves = [DOWN]
                    else:
                        possible_moves = [DOWN, RIGHT]
                elif next_spot(world, pos, (1,1)) in [GRASS, BUILDING, PARKING_LOT]:
                    # If its in the top left corner, only can go right
                    if next_spot(world, pos, (-2, 0)) == OFF_GRID:
                        possible_moves = [RIGHT]
                    else:
                        possible_moves = [RIGHT, UP]
                elif next_spot(world, pos, (-1, 1)) in [GRASS, BUILDING, PARKING_LOT]:
                    # if its in the bottom left corner
                    if next_spot(world, pos, (0, 2)) == OFF_GRID:
                        possible_moves = [UP]
                    else:
                        possible_moves = [UP, LEFT]
                else:
                    possible_moves = [UP, DOWN, LEFT, RIGHT]

        # Add ability to go into parking lot
        for dir in [UP, DOWN, RIGHT, LEFT]:
            if next_spot(world, pos, dir) in [PARKING_LOT, BUILDING]:
                possible_moves.append(dir)
            if next_spot(world, pos, STAY) == PARKING_LOT:
                if next_spot(world, pos, dir) == ROAD:
                    possible_moves.append(dir)
        
        # TODO add this
        # possible_moves.append(STAY)
        return possible_moves
    

def value_iteration(world, discount_factor=0.99, epsilon=0.0001):
    values = np.zeros((GRID_SIZE, GRID_SIZE))
    new_values = np.zeros((GRID_SIZE, GRID_SIZE))

    terminal_states = [BUILDING, GRASS, CRASH, CAR]

    for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if world[y][x] in terminal_states:
                    values[y][x] = get_reward(y, x, world)
                    new_values[y][x] = get_reward(y, x, world)

    while True:
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if world[y][x] not in terminal_states:              
                    max_value = float('-inf')
                    for action in get_possible_moves((y,x), world):
                        new_y, new_x = y + action[0], x + action[1]
                        if is_valid_state(new_y, new_x):
                            value = get_next_state_reward(new_y, new_x, world, values, discount_factor)
                            max_value = max(max_value, value)
                    new_values[y][x] = max_value

        diff = np.abs(values - new_values).max()
        if diff < epsilon:
            break
        values = np.copy(new_values)

    return values


class Car:
    def __init__(self, pos, world):
        self.pos = pos
        self.prev_pos = pos
        self.state = "moving" # Can be moving, crashed, or finished
        # self.accel = 1
        # self.speed = 0
        self.og_values = value_iteration(world)

    @property
    def x(self):
        return self.pos[1]
    
    @property
    def y(self):
        return self.pos[0]
    

    def move(self, world):
        if self.state != "moving":
            self.prev_pos = self.pos
            return self.pos
        
        legal_moves = get_possible_moves(self.pos, world)
        
        # values = value_iteration(world)
        values = self.og_values
        best_move = STAY
        best_score = -np.inf
        for dir in legal_moves: # [UP, DOWN, RIGHT, LEFT, STAY]:
            spot = next_spot(values, self.pos, dir)
            if spot != OFF_GRID and spot > best_score:
                best_move = dir
                best_score = spot

        # make the move
        self.prev_pos = self.pos
        self.pos = (self.pos[0] + best_move[0], self.pos[1] + best_move[1])

        return self.pos

    def move_random_legal(self, world):
        """
        
        """
        if self.state != "moving":
            self.prev_pos = self.pos
            return self.pos
        
        possible_moves = get_possible_moves(self.pos, world)

        done = False
        self.prev_pos = self.pos
        og_moves = possible_moves
        while not done:
            m = random.choice(possible_moves)
            p = next_pos(world, self.pos, m)
            if p != OFF_GRID:
                self.pos = p
                done = True
            else:
                print(f"Stuck: pos({self.pos}), moves: {og_moves}")
                m = (0,0)
                done = True

        # if self.speed < 1 and self.speed > -1:
        #     self.speed += self.accel
        # else:
        #     self.accel = 0
        return self.pos