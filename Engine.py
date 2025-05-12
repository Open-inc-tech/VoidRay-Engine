# pylint: disable=no-member

import pygame
import math
import sys
import os
import json
import importlib.util

# === BASIC SETTINGS ===
WIDTH, HEIGHT = 1280, 720
TILE = 50

# === RAYCASTING PARAMETERS ===
FOV = math.pi / 3
HALF_FOV = FOV / 2
NUM_RAYS = 160
DELTA_ANGLE = FOV / NUM_RAYS
DIST = NUM_RAYS / (2 * math.tan(HALF_FOV))
PROJ_COEFF = 3 * DIST * TILE
SCALE = WIDTH // NUM_RAYS

# === PLAYER PHYSICS ===
GRAVITY = 1.2
JUMP_POWER = 18
GROUND_LEVEL = 0

# === MAP SETTINGS ===
MAP_FILE = "map.json"
MAX_DEPTH = 20

# === TEXTURES ===
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

# Default map
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
    global MAP, current_map
    try:
        with open(MAP_FILE, 'r') as f:
            MAP = json.load(f)
            current_map = MAP_FILE
    except FileNotFoundError:
        save_map()
        current_map = "default"

load_map()

MAP_WIDTH = len(MAP[0]) * TILE
MAP_HEIGHT = len(MAP) * TILE

loaded_mods = []

def load_mods():
    global loaded_mods
    loaded_mods = []
    if not os.path.exists("mods"):
        os.mkdir("mods")
    for filename in os.listdir("mods"):
        if filename.endswith(".py"):
            path = os.path.join("mods", filename)
            spec = importlib.util.spec_from_file_location("mod", path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            loaded_mods.append(filename)

def draw_menu():
    screen.fill((20, 20, 20))

    title = font.render("VoidRay Engine", True, (255, 255, 255))
    version = font.render("Alpha 0.0.8V | made by Kitsune and Zuha", True, (180, 180, 180))
    info = font.render("[ENTER] Start project  |  [ESC] Exit", True, (150, 150, 150))

    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 5))
    screen.blit(version, (WIDTH // 2 - version.get_width() // 2, HEIGHT // 5 + 40))
    screen.blit(info, (WIDTH // 2 - info.get_width() // 2, HEIGHT // 2 - 40))

    controls = ["[WASD] Move", "[Space] Jump", "[Shift] Sprint", "[F3] Debug overlay"]
    for i, ctrl in enumerate(controls):
        text = font.render(ctrl, True, (100, 100, 100))
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + i * 20))

    if loaded_mods:
        mods_title = font.render("Loaded Mods:", True, (200, 200, 100))
        screen.blit(mods_title, (40, HEIGHT - 140))
        for i, mod in enumerate(loaded_mods[:3]):
            screen.blit(font.render(f"- {mod}", True, (150, 150, 150)), (60, HEIGHT - 120 + i * 20))

    map_text = font.render(f"Current Map: {current_map}", True, (150, 150, 150))
    screen.blit(map_text, (WIDTH - map_text.get_width() - 40, HEIGHT - 100))

    sysinfo = font.render(f"{WIDTH}x{HEIGHT} | {NUM_RAYS} rays", True, (80, 80, 80))
    screen.blit(sysinfo, (WIDTH - sysinfo.get_width() - 40, HEIGHT - 40))

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
            i, j = int(target_x / TILE), int(target_y / TILE)

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
    fps = int(clock.get_fps())
    lines = [
        f"FPS: {fps}",
        f"Pos: ({int(player_x)}, {int(player_y)})",
        f"Angle: {int(math.degrees(player_angle)) % 360}°",
        f"Floor: {MAP[int(player_y // TILE)][int(player_x // TILE)][1]}",
    ]
    for i, line in enumerate(lines):
        screen.blit(font.render(line, True, (120, 255, 120)), (10, 10 + i * 20))

# === MAIN LOOP ===
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
    if keys[pygame.K_LSHIFT]:
        speed = 2
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

    if not check_collision(player_x + dx, player_y):
        player_x += dx
    if not check_collision(player_x, player_y + dy):
        player_y += dy

    player_z += vertical_speed
    vertical_speed += GRAVITY
    if player_z >= GROUND_LEVEL:
        player_z = GROUND_LEVEL
        vertical_speed = 0
        is_jumping = False

    screen.fill((30, 30, 30))
    cast_rays()
    if keys[pygame.K_F3]:
        draw_fps()

    pygame.display.flip()
    clock.tick(30)
