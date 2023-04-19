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
    
 

def value_iteration(world, possible_moves, discount_factor=0.99, epsilon=0.01):
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
                    for action in possible_moves[(y,x)]:
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
    def __init__(self, pos, building_num, world, possible_moves):
        self.pos = pos
        self.prev_pos = pos
        self.state = "moving" # Can be moving, crashed, or finished
        # self.accel = 1
        # self.speed = 0
        self.og_values = value_iteration(world, possible_moves=possible_moves)
        self.possible_moves = possible_moves
        self.building_num = building_num

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
        
        # legal_moves = get_possible_moves(self.pos, world)
        
        # values = value_iteration(world)
        values = self.og_values
        best_move = STAY
        best_score = -np.inf
        for dir in self.possible_moves[self.pos]: # [UP, DOWN, RIGHT, LEFT, STAY]:
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
        
        # possible_moves = get_possible_moves(self.pos, world)

        done = False
        self.prev_pos = self.pos
        og_moves = self.possible_moves[self.pos]
        while not done:
            m = random.choice(self.possible_moves[self.pos])
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