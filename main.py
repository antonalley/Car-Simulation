## CS 470 Poject 4
import pygame
import random
from car import Car

# Define constants
WIDTH = 800
HEIGHT = 800
BLOCK_SIZE = 16
GRID_SIZE = 50
FPS = 120
FPD = FPS // 10 # Frames per decision
ROAD_FREQUENCY = 8
# ROAD_PROBABILITY = 1.0

# Define colors
GRASS_COLOR = (0, 128, 0)
ROAD_COLOR = (128, 128, 128)
BUILDING_COLOR = (212,175,55)
PARKING_LOT_COLOR = (0,0,0)
CAR_COLOR = (200,20,20)
LINE_COLOR = (255,255,255)

# Color map
cmap = {
    0: GRASS_COLOR,
    1: ROAD_COLOR,
    2: BUILDING_COLOR,
    3: PARKING_LOT_COLOR
}

def generate_world():
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

    
    placed_building = False
    while not placed_building:
        y = random.randint(1, GRID_SIZE - 2)
        x = random.randint(1, GRID_SIZE - 2)

        if world[y][x] == 0 and any([world[y+dy][x+dx] == 1 for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]]):
            world[y][x] = 2
            for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1,-1), (1,1), (-1,1),(1,-1)]:
                if world[y+dy][x+dx] == 0:
                    world[y+dy][x+dx] = 3
            placed_building = True

    return world

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
        draw_car(screen, c, transition)
    

def draw_car(screen, car, transition):
    amount = BLOCK_SIZE * transition
    t = (
        (car.pos[0] - car.prev_pos[0]) * amount,
        (car.pos[1] - car.prev_pos[1]) * amount
    )
    t = (0,0)
    pygame.draw.rect(screen, CAR_COLOR, ((car.pos[0] * BLOCK_SIZE) + t[0], (car.pos[1] * BLOCK_SIZE) + t[1], BLOCK_SIZE, BLOCK_SIZE))

def place_car(world):
    while True:
        y = random.randint(0, GRID_SIZE - 1)
        x = random.randint(0, GRID_SIZE - 1)

        if world[y][x] == 1:
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


def main():
    # Initialize pygame
    pygame.init()

    # Create the game window
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Cars finding a destination with traffic")

    # Initialize clock
    clock = pygame.time.Clock()

    # Generate a random 2D block world
    world = generate_world()

    cars = [Car(place_car(world)) for i in range(100)]

    # Main game loop
    running = True
    frame = 0
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((255, 255, 255))
        # if frame%FPD == 0:
        #     transition = 1
        # else:
        #     transition = frame%FPD / FPD
        transition = 1
        draw_world(world, screen, *cars, transition=transition)
        pygame.display.flip()

        if frame % FPD == 0:
            for car in cars:
                car.move(world)

        frame += 1


    # Quit pygame
    pygame.quit()


if __name__ == '__main__':
    main()