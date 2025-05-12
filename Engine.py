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

MAP_FOLDER = "maps"
map_list = []
map_index = 0
current_map = "None"

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
    [(1,0), (0,0), (0,0), (0,0), (1,0), (2,0), (0,0), (1,0), (0,0), (2,0), (0,0), (1,0), (0,0), (0,0), (2,0), (1,0), (0,0), (0,0), (0,0), (1,0)],
    [(1,0), (0,0), (1,0), (0,0), (1,0), (1,0), (0,0), (1,0), (1,0), (0,0), (1,0), (1,0), (0,0), (1,0), (1,0), (1,0), (0,0), (1,0), (0,0), (1,0)],
    [(1,0), (0,0), (1,0), (0,0), (0,0), (0,0), (2,0), (0,0), (0,0), (2,1), (0,0), (0,0), (2,0), (0,0), (0,0), (1,0), (0,0), (1,0), (0,0), (1,0)],
    [(1,0), (0,0), (1,0), (1,0), (1,0), (0,0), (1,0), (1,0), (1,0), (1,0), (1,0), (1,0), (0,0), (1,0), (0,0), (1,0), (0,0), (1,0), (0,0), (1,0)],
    [(1,0), (0,0), (0,0), (0,0), (1,0), (2,1), (0,0), (2,0), (0,0), (2,1), (0,0), (2,0), (0,0), (1,0), (0,0), (0,0), (0,0), (0,0), (0,0), (1,0)],
    [(1,0), (0,0), (1,0), (1,0), (1,0), (1,0), (1,0), (1,0), (1,0), (1,0), (1,0), (1,0), (1,0), (1,0), (1,0), (1,0), (0,0), (1,0), (0,0), (1,0)],
    [(1,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (1,0)],
    [(1,0)] * 20,
]

def save_map():
    filename = os.path.join(MAP_FOLDER, current_map if current_map != "None" else "map.json")
    with open(filename, 'w') as f:
        json.dump(MAP, f)

def load_map(filename):
    global MAP, current_map, MAP_WIDTH, MAP_HEIGHT
    path = os.path.join(MAP_FOLDER, filename)
    try:
        with open(path, 'r') as f:
            MAP = json.load(f)
            current_map = filename
            MAP_WIDTH = len(MAP[0]) * TILE
            MAP_HEIGHT = len(MAP) * TILE
    except Exception as e:
        print(f"Failed to load map: {filename} - {e}")
        current_map = "error"


MAP_WIDTH = len(MAP[0]) * TILE
MAP_HEIGHT = len(MAP) * TILE

loaded_mods = []

def load_map_list():
    global map_list
    if not os.path.exists(MAP_FOLDER):
        os.makedirs(MAP_FOLDER)
    map_list = [f for f in os.listdir(MAP_FOLDER) if f.endswith(".json")]
    if not map_list:
        # fallback map if no maps exist
        with open(os.path.join(MAP_FOLDER, "default.json"), 'w') as f:
            json.dump(MAP, f)
        map_list = ["default.json"]


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
    version = font.render("Alpha 0.1.3V | made by Kitsune and Zuha", True, (180, 180, 180))
    info = font.render("[ENTER] Load map  |  [ESC] Exit  |  [↑/↓] Select Map", True, (150, 150, 150))

    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 5))
    screen.blit(version, (WIDTH // 2 - version.get_width() // 2, HEIGHT // 5 + 40))
    screen.blit(info, (WIDTH // 2 - info.get_width() // 2, HEIGHT // 5 + 80))

    # Draw map list
    map_list_start_y = HEIGHT // 2 - 40
    for i, name in enumerate(map_list):
        color = (255, 255, 0) if i == map_index else (150, 150, 150)
        label = font.render(f"> {name}", True, color)
        screen.blit(label, (WIDTH // 2 - label.get_width() // 2, map_list_start_y + i * 30))

    # Draw controls below map list
    controls = ["[WASD] Move", "[Space] Jump", "[Shift] Sprint", "[F3] Debug overlay"]
    controls_start_y = map_list_start_y + len(map_list) * 30 + 30
    for i, ctrl in enumerate(controls):
        text = font.render(ctrl, True, (100, 100, 100))
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, controls_start_y + i * 25))

    # Loaded mods
    if loaded_mods:
        mods_title = font.render("Loaded Mods:", True, (200, 200, 100))
        screen.blit(mods_title, (40, HEIGHT - 140))
        for i, mod in enumerate(loaded_mods[:3]):
            screen.blit(font.render(f"- {mod}", True, (150, 150, 150)), (60, HEIGHT - 120 + i * 20))

    # Current map name
    map_text = font.render(f"Current Map: {current_map}", True, (150, 150, 150))
    screen.blit(map_text, (WIDTH - map_text.get_width() - 40, HEIGHT - 100))

    # System info (resolution, rays)
    sysinfo = font.render(f"{WIDTH}x{HEIGHT} | {NUM_RAYS} rays", True, (80, 80, 80))
    screen.blit(sysinfo, (WIDTH - sysinfo.get_width() - 40, HEIGHT - 40))

    pygame.display.flip()

def check_collision(x, y):
    """Check if the position (x, y) collides with a solid tile."""
    tile_x, tile_y = int(x // TILE), int(y // TILE)

    if 0 <= tile_y < len(MAP) and 0 <= tile_x < len(MAP[0]):
        tile_type, _ = MAP[tile_y][tile_x]
        solid_tiles = {1, 3}  # Typy, které se počítají jako pevné (např. 1=zeď, 3=pevná rampa)
        return tile_type in solid_tiles

    # Mimo mapu = kolize
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

                if tile_type == 1:  # Wall
                    corrected_depth = depth * math.cos(player_angle - ray_angle)
                    wall_height = PROJ_COEFF / (corrected_depth + 0.0001)
                    wall_height = min(HEIGHT, wall_height)

                    # Depth-based shading: darker the further away the wall is
                    base_shade = max(30, 255 - int(corrected_depth * 2))  # Basic depth-based shading
                    
                    # "Sunlight" effect: light comes from a direction (e.g. player's view direction)
                    directional_light = math.cos(ray_angle - player_angle) * 0.2  # Adjust this for sun effect
                    final_shade = base_shade + int(base_shade * directional_light)

                    # Ensure shade is within the 0-255 range
                    final_shade = max(0, min(255, final_shade))

                    # Color tone based on the calculated shade
                    color = (final_shade, final_shade, final_shade)

                    # Calculate y position on the screen
                    y_offset = tile_height * 20
                    screen_y = HEIGHT // 2 - wall_height // 2 - y_offset

                    rect = pygame.Rect(ray * SCALE, screen_y, SCALE, wall_height)

                    # Draw the wall with the calculated shade
                    pygame.draw.rect(screen, color, rect)
                    break

                elif tile_type == 2:  # Window (hole in wall)
                    corrected_depth = depth * math.cos(player_angle - ray_angle)
                    wall_height = PROJ_COEFF / (corrected_depth + 0.0001)
                    wall_height = min(HEIGHT, wall_height)

                    # Render window as an empty space (lighter shade)
                    base_shade = 150  # Lighter shade for windows
                    directional_light = math.cos(ray_angle - player_angle) * 0.1  # Light direction effect
                    final_shade = base_shade + int(base_shade * directional_light)

                    final_shade = max(0, min(255, final_shade))

                    color = (final_shade, final_shade, final_shade)

                    y_offset = tile_height * 20
                    screen_y = HEIGHT // 2 - wall_height // 2 - y_offset

                    rect = pygame.Rect(ray * SCALE, screen_y, SCALE, wall_height)

                    pygame.draw.rect(screen, color, rect)
                    break

            else:
                break  # Out of bounds (non-existing tile)

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
load_map_list()  # <- přidej tuto řádku jako první

if not map_list:
    print("❌ No maps found! Creating default map...")
    save_map()
    load_map_list()

if map_index >= len(map_list):
    map_index = 0

load_map(map_list[map_index])


look_offset = 0  
MOUSE_SENSITIVITY = 0.002
VERTICAL_SENSITIVITY = 0.05
pygame.mouse.set_visible(False)
pygame.event.set_grab(True) 


while True:
    if menu:
        draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                elif event.key == pygame.K_RETURN:
                    load_map(map_list[map_index])
                    menu = False
                elif event.key == pygame.K_DOWN:
                    map_index = (map_index + 1) % len(map_list)
                elif event.key == pygame.K_UP:
                    map_index = (map_index - 1) % len(map_list)
        continue

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F5:
                save_map()
            elif event.key == pygame.K_F9 and current_map not in ["None", "error"]:
                load_map(current_map)

    
    mx, my = pygame.mouse.get_rel()
    player_angle += mx * MOUSE_SENSITIVITY
    look_offset += my * VERTICAL_SENSITIVITY
    look_offset = max(-100, min(100, look_offset))  

    keys = pygame.key.get_pressed()
    dx, dy = 0, 0
    speed = 1.0
    if keys[pygame.K_LSHIFT]:
        speed = 2.2

    
    sin_a = math.sin(player_angle)
    cos_a = math.cos(player_angle)
    if keys[pygame.K_w]:
        dx += cos_a * speed
        dy += sin_a * speed
    if keys[pygame.K_s]:
        dx -= cos_a * speed
        dy -= sin_a * speed
    if keys[pygame.K_a]:
        dx += sin_a * speed
        dy -= cos_a * speed
    if keys[pygame.K_d]:
        dx -= sin_a * speed
        dy += cos_a * speed
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
