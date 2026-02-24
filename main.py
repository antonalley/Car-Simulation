## CS 470 Project 4
import pygame
import random
import pickle
from car import Car
from globals import *
from world import World
import pygame_gui


def is_button_press(event, button):
    """Handle pygame_gui <0.6 button press events (posted as pygame.USEREVENT)."""
    return (event.type == pygame.USEREVENT and
            hasattr(event, 'user_type') and
            event.user_type == pygame_gui.UI_BUTTON_PRESSED and
            event.ui_element == button)


def draw_block(pos, color, screen):
    pygame.draw.rect(screen, color, (pos[0] * BLOCK_SIZE, pos[1] * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))


def draw_world(world, screen, building_locations, *cars, transition=1, label_font=None):
    for y, row in enumerate(world):
        for x, block in enumerate(row):
            if block == BUILDING:
                continue  # Buildings are drawn separately with per-building colors
            color = cmap[block]
            draw_block((x, y), color, screen)

    # Draw buildings with distinct per-building destination colors
    for i, (by, bx) in enumerate(building_locations):
        color = BUILDING_COLORS[i % len(BUILDING_COLORS)]
        draw_block((bx, by), color, screen)
        if label_font is not None:
            label = label_font.render(str(i + 1), True, (0, 0, 0))
            screen.blit(label, (bx * BLOCK_SIZE + 2, by * BLOCK_SIZE + 1))

    for y, row in enumerate(world):
        for x, block in enumerate(row):
            if block == ROAD:
                if x - 1 <= 0 or world[y][x - 1] != ROAD:
                    draw_lines(screen, (x, y))
                if y - 1 <= 0 or world[y - 1][x] != ROAD:
                    draw_lines(screen, (x, y))

    for c in cars:
        if c.state in ["moving", "crashed"]:
            draw_car(screen, c, transition)


def draw_car(screen, car, transition):
    amount = BLOCK_SIZE * transition
    t = (
        (car.pos[0] - car.prev_pos[0]) * amount,
        (car.pos[1] - car.prev_pos[1]) * amount
    )
    if car.state == "moving":
        color = BUILDING_COLORS[car.building_num % len(BUILDING_COLORS)]
    else:
        color = CRASH_COLOR
    pygame.draw.rect(screen, color, (
        (car.prev_pos[1] * BLOCK_SIZE) + t[1],
        (car.prev_pos[0] * BLOCK_SIZE) + t[0],
        BLOCK_SIZE, BLOCK_SIZE
    ))


def place_car(world):
    while True:
        y = random.randint(0, GRID_SIZE - 1)
        x = random.randint(0, GRID_SIZE - 1)

        if world.world[y][x] == ROAD:
            return (y, x)


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


def utility(car: Car, goal) -> float:
    """Returns distance from car to goal; lower is better."""
    return ((car.pos[0] - goal[0]) ** 2 + (car.pos[1] - goal[1]) ** 2) ** 0.5


def init_cars(world):
    positions = []
    cars = []
    for i in range(NUM_CARS):
        while True:
            p = place_car(world)
            if p not in positions:
                building_num = i % NUM_BUILDINGS
                cars.append(Car(p, building_num, world.get_possible_moves(building_num), world.get_initial_value_iteration(building_num)))
                break

        positions.append(p)
    return cars

def main(world: World = None):
    # Initialize pygame
    pygame.init()

    # Create the game window
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Cars finding a destination with traffic")

    # Initialize clock
    clock = pygame.time.Clock()

    # Create the UI manager
    ui_manager = pygame_gui.UIManager((WIDTH, HEIGHT))

    # Create buttons
    reset_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WIDTH - 95, HEIGHT - 30, 90, 25)),
        text='Restart',
        manager=ui_manager
    )
    random_reset_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WIDTH - 195, HEIGHT - 30, 95, 25)),
        text='Randomize',
        manager=ui_manager
    )
    pause_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WIDTH - 285, HEIGHT - 30, 85, 25)),
        text='Pause',
        manager=ui_manager
    )

    cars = init_cars(world)

    # Main game loop
    running = True
    paused = False
    frame = 0
    stat_font = pygame.font.Font(None, 24)
    legend_font = pygame.font.Font(None, 20)
    label_font = pygame.font.Font(None, BLOCK_SIZE + 4)

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                paused = not paused
                pause_button.set_text('Resume' if paused else 'Pause')
            elif is_button_press(event, reset_button):
                cars = init_cars(world)
                paused = False
                pause_button.set_text('Pause')
                frame = 0
            elif is_button_press(event, random_reset_button):
                world = World()
                cars = init_cars(world)
                paused = False
                pause_button.set_text('Pause')
                frame = 0
            elif is_button_press(event, pause_button):
                paused = not paused
                pause_button.set_text('Resume' if paused else 'Pause')

            ui_manager.process_events(event)

        screen.fill((20, 20, 20))

        transition = 1 if frame % FPD == 0 else frame % FPD / FPD
        draw_world(world.get_world_and_building(), screen, world.building_locations, *cars, transition=transition, label_font=label_font)

        # Draw status bar background
        pygame.draw.rect(screen, (40, 40, 40), (0, HEIGHT - 60, WIDTH, 60))

        # Count car states
        states = [car.state for car in cars]
        moving = states.count('moving')
        finished = states.count('finished')
        crashed = states.count('crashed')

        # Stats text
        stats_text = stat_font.render(
            f"Moving: {moving}   Finished: {finished}   Crashed: {crashed}",
            True, (220, 220, 220)
        )
        screen.blit(stats_text, (10, HEIGHT - 55))

        # Building color legend
        legend_x = 10
        legend_y = HEIGHT - 38
        for i in range(NUM_BUILDINGS):
            color = BUILDING_COLORS[i % len(BUILDING_COLORS)]
            pygame.draw.rect(screen, color, (legend_x, legend_y, 14, 14))
            num_label = legend_font.render(str(i + 1), True, (0, 0, 0))
            screen.blit(num_label, (legend_x + 3, legend_y + 1))
            legend_x += 20
        dest_label = legend_font.render("← destinations", True, (180, 180, 180))
        screen.blit(dest_label, (legend_x + 4, legend_y + 1))

        if paused:
            pause_text = stat_font.render("PAUSED", True, (255, 220, 50))
            screen.blit(pause_text, (WIDTH // 2 - 35, HEIGHT - 38))

        ui_manager.update(1 / FPS)
        ui_manager.draw_ui(screen)

        pygame.display.flip()

        if not paused and frame % FPD == 0:
            new_poss = []
            for car in cars:
                pos = car.move(world.get_world_and_cars(cars, car.building_num), world.get_possible_moves(car.building_num))
                if pos == world.building_locations[car.building_num]:
                    car.state = "finished"
                elif world.world[pos[0]][pos[1]] == CRASH:
                    car.state = "crashed"
                    car.pos = car.prev_pos
                elif pos in new_poss:
                    # Both cars involved in a collision crash
                    cars[new_poss.index(pos)].state = "crashed"
                    car.state = "crashed"
                    car.pos = car.prev_pos
                new_poss.append(pos)

        if not paused:
            frame += 1

    # Quit pygame
    pygame.quit()


if __name__ == '__main__':

    # To open saved world:
    # world = World.open()

    # Generate new world (overwrites saved world):
    world = World()

    main(world=world)
