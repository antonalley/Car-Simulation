## CS 470 Poject 4
import pygame
import random
import pickle
from car import Car
from globals import *
from world import World

def draw_block(pos, color, screen):
    pygame.draw.rect(screen, color, (pos[0] * BLOCK_SIZE, pos[1] * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

def draw_world(world, screen, *cars, transition=1):
    for y, row in enumerate(world):
        for x, block in enumerate(row):
            color = cmap[block]
            draw_block((x, y), color, screen)

    for y, row in enumerate(world):
        for x, block in enumerate(row):
            if block == 1:
                if x-1 <= 0 or world[y][x - 1] != 1:
                    draw_lines(screen, (x,y))
                if y-1 <= 0 or world[y-1][x] != 1:
                    draw_lines(screen, (x,y)) 

    for c in cars:
        if c.state == "moving":
            draw_car(screen, c, transition)
    

def draw_car(screen, car, transition):
    # For acceleration:
    # amount = transition * (car.speed + (car.speed-car.accel))
    amount = BLOCK_SIZE * transition
    t = (
        (car.pos[0] - car.prev_pos[0]) * amount,
        (car.pos[1] - car.prev_pos[1]) * amount
    )
    # t = (0,0)
    pygame.draw.rect(screen, CAR_COLOR, ((car.prev_pos[1] * BLOCK_SIZE) + t[1], (car.prev_pos[0] * BLOCK_SIZE) + t[0], BLOCK_SIZE, BLOCK_SIZE))

def place_car(world):
    while True:
        y = random.randint(0, GRID_SIZE - 1)
        x = random.randint(0, GRID_SIZE - 1)

        if world.world[y][x] == ROAD:
            return (x, y)
        
def draw_lines(screen, pos):
    if pos[1] % ROAD_FREQUENCY < 2 and pos[0] % ROAD_FREQUENCY < 2:
        # Intersection
        pass
    elif pos[1] % ROAD_FREQUENCY == 0:  # Horizontal road
        for i in range(0, BLOCK_SIZE, 4):
            pygame.draw.rect(screen, LINE_COLOR, (pos[0] * BLOCK_SIZE + i, (pos[1] + 1) * BLOCK_SIZE, 2, 1))
    elif pos[0] % ROAD_FREQUENCY == 0:  # Vertical road
        for i in range(0, BLOCK_SIZE, 4):
            pygame.draw.rect(screen, LINE_COLOR, ((pos[0] + 1) * BLOCK_SIZE, pos[1] * BLOCK_SIZE + i, 1, 2))


def utility(car: Car, goal) -> int:
    """ Returns a score 0.0 - 1.0 for the car based on how close it is to the goal, and if it's not crashed
    """
    distance = ((car.pos[0] - goal[0]) **2 + (car.pos[1] - goal[1])**2)**0.5
    # if distance == 0: return 1
    # else: return 1.0 / distance
    return distance


def main(world:World=None):
    # Initialize pygame
    pygame.init()

    # Create the game window
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Cars finding a destination with traffic")

    # Initialize clock
    clock = pygame.time.Clock()

    # place_car(world)
    positions = []
    cars = []
    for i in range(NUM_CARS):
        while True:
            p = place_car(world)
            # p = building_location[0]+1, building_location[1]+1
            if p not in positions:
                building_num = i % NUM_BUILDINGS
                cars.append(Car(p, building_num, world.get_world_and_building(building_num), world.get_possible_moves(building_num)))
                break

        positions.append(p)

    # Main game loop
    running = True
    frame = 0
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((255, 255, 255))
        if frame%FPD == 0:
            transition = 1
        else:
            transition = frame%FPD / FPD
        # transition = 1
        draw_world(world.get_world_and_building(), screen, *cars, transition=transition)
        pygame.display.flip()

        if frame % FPD == 0:
            new_poss = []
            for car in cars:
                pos = car.move(world)
                if pos == world.building_locations[car.building_num]:
                    car.state = "finished"
                # elif world[pos[0]][pos[1]] == 4:
                #     car.state = "crashed"
                #     world[car.prev_pos[0]][car.prev_pos[1]] = 4
                # elif pos in new_poss:
                #     # Make sure both cars change to crashed
                #     cars[new_poss.index(pos)].state = "crashed"
                #     car.state = "crashed"
                #     world[car.prev_pos[0]][car.prev_pos[1]] = 4
                new_poss.append(pos)

                # score = utility(car, building_location)
                # print(f"Car Score: {score}")
                # print("pos", car.pos)

        frame += 1


    # Quit pygame
    pygame.quit()


if __name__ == '__main__':
    # To Open Saved World
    # world = World.open()
    # To Generate New World and overwrite save:
    world = World()
    main(world=world)