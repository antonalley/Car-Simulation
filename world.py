import pickle
import random
from copy import deepcopy

from car import next_pos, next_spot
from globals import *


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
            if next_spot(world, pos, dir) == PARKING_LOT:
                possible_moves.append(dir)
            if next_spot(world, pos, STAY) == PARKING_LOT:
                if next_spot(world, pos, dir) in [ROAD, BUILDING]:
                    possible_moves.append(dir)
        
        possible_moves.append(STAY)
        return possible_moves
   


class World:
    def __init__(self, save_file="world.pickle"):
        self.world, self.building_locations = self.generate_world()

        self.cache = {} # Keep a record of frequent function calls to improve performance
        self.save_file = save_file
        self.save()

    def generate_world(self):
        world = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if x % ROAD_FREQUENCY == 0 or y % ROAD_FREQUENCY == 0:
                    # if random.random() < ROAD_PROBABILITY:
                    world[y][x] = 1
                    if y + 1 < GRID_SIZE:
                        world[y + 1][x] = 1
                    if x + 1 < GRID_SIZE:
                        world[y][x + 1] = 1

        
        placed_buildings = 0
        building_locations = []
        while placed_buildings < NUM_BUILDINGS:
            y = random.randint(1, GRID_SIZE - 2)
            x = random.randint(1, GRID_SIZE - 2)

            if world[y][x] == 0 and any([world[y+dy][x+dx] == 1 for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]]):
                building_locations.append((y, x))
                placed_buildings += 1

        return world, building_locations
    

    def get_world_and_building(self, building_num='all'):
        if f"get_world_and_building({building_num})" not in self.cache:
            locs =  self.building_locations if building_num == 'all' else [self.building_locations[building_num]]             
            mod_world = deepcopy(self.world)
            for loc in locs:
                mod_world[loc[0]][loc[1]] = BUILDING
                for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1,-1), (1,1), (-1,1),(1,-1)]:
                    if mod_world[loc[0]+dy][loc[1]+dx] == GRASS:
                            mod_world[loc[0]+dy][loc[1]+dx] = PARKING_LOT

            self.cache[f"get_world_and_building({building_num})"] = mod_world
            self.save()
            return mod_world
        else:
            return self.cache[f"get_world_and_building({building_num})"]
    
    def get_world_and_crashes(self):
        # TODO
        return self.world
    
    def get_world_and_cars(self):
        # TODO
        return self.world
    
    def get_possible_moves(self, building_num):
        if f"get_possible_moves({building_num})" not in self.cache:
            moves_dict = {}
            mod_world = self.get_world_and_building(building_num)
            for i in range(len(mod_world)):
                for j in range(len(mod_world[i])):
                    pos = (i,j)
                    moves = get_possible_moves(pos, mod_world)
                    moves_dict[pos] = moves
            self.cache[f"get_possible_moves({building_num})"] = moves_dict
            self.save()
            return moves_dict
        else:
            return self.cache[f"get_possible_moves({building_num})"]
        

    def save(self):
        with open(self.save_file, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def open(save_file='world.pickle'):
        try:
            with open(save_file, 'rb') as f:
                return pickle.load(f)
        except:
            return World()