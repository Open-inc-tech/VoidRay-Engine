import pygame
import math
import sys
import os
import json
import importlib.util

# === BASIC SETTINGS ===
WIDTH, HEIGHT = 800, 600            # Screen resolution
TILE = 50                           # Size of one tile in pixels

# === RAYCASTING PARAMETERS ===
FOV = math.pi / 3                   # Field of view (60 degrees)
HALF_FOV = FOV / 2
NUM_RAYS = 160                      # Number of rays cast
DELTA_ANGLE = FOV / NUM_RAYS
DIST = NUM_RAYS / (2 * math.tan(HALF_FOV))
PROJ_COEFF = 3 * DIST * TILE        # Wall projection size coefficient
SCALE = WIDTH // NUM_RAYS           # Width of a single vertical ray column

# === PLAYER PHYSICS ===
GRAVITY = 1.2                       # Gravity strength
JUMP_POWER = 18                     # Jump height
GROUND_LEVEL = 0                    # Y level of the ground

# === MAP SETTINGS ===
MAP_FILE = "map.json"               # JSON file to store map data
MAX_DEPTH = 20                      # Max ray depth (in tiles)

TEXTURE_WALL = pygame.image.load("wall.png") if os.path.exists("wall.png") else None
TEXTURE_FLOOR = pygame.image.load("floor.png") if os.path.exists("floor.png") else None

# --- Initialization ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("VoidRay Engine")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 20)

player_x, player_y = 100, 100
player_angle = 0
player_z = GROUND_LEVEL
vertical_speed = 0
is_jumping = False

# Default map: [(type, height)]
MAP = [
    [(1,0)] * 20,
    [(1,0), (0,0), (0,0), (0,0), (1,0), (0,1), (0,0), (1,0), (0,0), (0,0), (0,1), (1,0), (0,0), (0,0), (0,1), (1,0), (0,0), (0,0), (0,0), (1,0)],
    [(1,0), (0,0), (1,0), (0,0), (1,0), (1,0), (0,0), (1,0), (1,0), (0,0), (1,0), (1,0), (0,0), (1,0), (1,0), (1,0), (0,0), (1,0), (0,0), (1,0)],
    [(1,0), (0,0), (1,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (1,0), (0,0), (1,0), (0,0), (1,0)],
    [(1,0), (0,0), (1,0), (1,0), (1,0), (0,0), (1,0), (1,0), (1,0), (1,0), (1,0), (1,0), (0,0), (1,0), (0,0), (1,0), (0,0), (1,0), (0,0), (1,0)],
    [(1,0), (0,0), (0,0), (0,0), (1,0), (0,1), (0,0), (0,1), (0,0), (0,1), (0,0), (0,1), (0,0), (1,0), (0,0), (0,0), (0,0), (0,0), (0,0), (1,0)],
    [(1,0), (0,0), (1,0), (1,0), (1,0), (1,0), (1,0), (1,0), (1,0), (1,0), (1,0), (1,0), (1,0), (1,0), (1,0), (1,0), (0,0), (1,0), (0,0), (1,0)],
    [(1,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (1,0)],
    [(1,0)] * 20,
]

def save_map():
    with open(MAP_FILE, 'w') as f:
        json.dump(MAP, f)

def load_map():
    global MAP
    try:
        with open(MAP_FILE, 'r') as f:
            MAP = json.load(f)
    except FileNotFoundError:
        save_map()

load_map()
MAP_WIDTH = len(MAP[0]) * TILE
MAP_HEIGHT = len(MAP) * TILE

def draw_menu():
    screen.fill((20, 20, 20))
    title = font.render("VoidRay Engine", True, (255, 255, 255))
    version = font.render("Alpha 0.0.5V | made by Kitsune and Zuha", True, (180, 180, 180))
    info = font.render("[ENTER] Start | [ESC] Exit", True, (150, 150, 150))

    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3))
    screen.blit(version, (WIDTH // 2 - version.get_width() // 2, HEIGHT // 3 + 40))
    screen.blit(info, (WIDTH // 2 - info.get_width() // 2, HEIGHT // 2))

    pygame.display.flip()

def check_collision(x, y):
    i, j = int(x / TILE), int(y / TILE)
    if 0 <= j < len(MAP) and 0 <= i < len(MAP[0]):
        return MAP[j][i][0] == 1
    return True

def cast_rays():
    start_angle = player_angle - HALF_FOV
    for ray in range(NUM_RAYS):
        ray_angle = start_angle + ray * DELTA_ANGLE
        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)

        for depth in range(1, MAX_DEPTH * 10):
            target_x = player_x + cos_a * depth
            target_y = player_y + sin_a * depth
            i = int(target_x / TILE)
            j = int(target_y / TILE)

            if 0 <= j < len(MAP) and 0 <= i < len(MAP[0]):
                tile_type, tile_height = MAP[j][i]
                if tile_type == 1:
                    corrected_depth = depth * math.cos(player_angle - ray_angle)
                    wall_height = PROJ_COEFF / (corrected_depth + 0.0001)
                    wall_height = min(HEIGHT, wall_height)

                    y_offset = tile_height * 20
                    screen_y = HEIGHT // 2 - wall_height // 2 - y_offset

                    shade = max(30, 255 - int(corrected_depth * 2))
                    color = (shade, shade, shade)

                    rect = pygame.Rect(ray * SCALE, screen_y, SCALE, wall_height)

                    if TEXTURE_WALL:
                        texture = pygame.transform.scale(TEXTURE_WALL, (SCALE, int(wall_height)))
                        screen.blit(texture, rect)
                    else:
                        pygame.draw.rect(screen, color, rect)
                    break
            else:
                break

def draw_fps():
    # FPS
    fps = int(clock.get_fps())
    overlay = [
        f"FPS: {fps}",
        f"Position: ({int(player_x)}, {int(player_y)})",
        f"Angle: {int(math.degrees(player_angle)) % 360}°",
        f"Height: {int(player_height) if 'player_height' in globals() else 'N/A'}",
        f"Floor level: {MAP[int(player_y // TILE)][int(player_x // TILE)][1]}",
        f"Rays: {NUM_RAYS}",
        f"Screen: {WIDTH}x{HEIGHT}",
    ]

def load_mods():
    if not os.path.exists("mods"):
        os.mkdir("mods")
    for filename in os.listdir("mods"):
        if filename.endswith(".py"):
            path = os.path.join("mods", filename)
            spec = importlib.util.spec_from_file_location("mod", path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

# --- Game loop ---
menu = True
load_mods()

while True:
    if menu:
        draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                menu = False
        continue

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F5:
                save_map()
            elif event.key == pygame.K_F9:
                load_map()

    keys = pygame.key.get_pressed()
    dx, dy = 0, 0
    speed = 1
    if keys[pygame.K_w]:
        dx += math.cos(player_angle) * speed
        dy += math.sin(player_angle) * speed
    if keys[pygame.K_s]:
        dx -= math.cos(player_angle) * speed
        dy -= math.sin(player_angle) * speed
    if keys[pygame.K_a]:
        player_angle -= 0.05
    if keys[pygame.K_d]:
        player_angle += 0.05
    if keys[pygame.K_SPACE] and not is_jumping:
        vertical_speed = -JUMP_POWER
        is_jumping = True
        
    # Collision check
    if not check_collision(player_x + dx, player_y):
        player_x += dx
    if not check_collision(player_x, player_y + dy):
        player_y += dy

    # Gravity & jump
    player_z += vertical_speed
    vertical_speed += GRAVITY
    if player_z >= GROUND_LEVEL:
        player_z = GROUND_LEVEL
        vertical_speed = 0
        is_jumping = False

    screen.fill((30, 30, 30))
    cast_rays()
    draw_fps()
    pygame.display.flip()
    clock.tick(60)
