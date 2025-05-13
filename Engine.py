# pylint: disable=no-member

import pygame
import math
import sys
import os
import json
import importlib.util
import logging

WIDTH, HEIGHT = 1280, 720
TILE = 50

FOV = math.pi / 3
HALF_FOV = FOV / 2
NUM_RAYS = 160
DELTA_ANGLE = FOV / NUM_RAYS
DIST = NUM_RAYS / (2 * math.tan(HALF_FOV))
PROJ_COEFF = 3 * DIST * TILE
SCALE = WIDTH // NUM_RAYS

GRAVITY = 1.2
JUMP_POWER = 18
GROUND_LEVEL = 0

MAP_FILE = "map.json"
MAX_DEPTH = 20

MAP_FOLDER = "maps"
map_list = []
map_index = 0
current_map = "None"

TEXTURE_WALL = pygame.image.load("wall.png") if os.path.exists("wall.png") else None
TEXTURE_FLOOR = pygame.image.load("floor.png") if os.path.exists("floor.png") else None

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
pygame.display.set_caption("VoidRay Engine")
clock = pygame.time.Clock()

font = pygame.font.SysFont("consolas", 20)
small_font = pygame.font.SysFont("consolas", 14)

player_x = 100
player_y = 100
player_angle = 0
player_z = GROUND_LEVEL
player_height = 32  
player_speed = 3    
player_turn_speed = 0.05  

vertical_speed = 0
gravity = 1.2
jump_force = -12
is_jumping = False
is_falling = False
on_ground = True

show_fps = True
debug_mode = True

COLOR_SKY = (40, 40, 80)
COLOR_GROUND = (30, 30, 30)
COLOR_PLAYER = (255, 255, 0)

frame_count = 0
game_running = True

MAP = [
    [[1,0],[1,0],[1,0]],
    [[1,0],[0,0],[1,0]],
    [[1,0],[1,0],[1,0]]
]

def save_map():
    filename = os.path.join(MAP_FOLDER, current_map if current_map != "None" else "map.json")
    with open(filename, 'w') as f:
        json.dump(MAP, f)

def load_map(filename):
    global MAP, current_map, MAP_WIDTH, MAP_HEIGHT
    global player_x, player_y  
    path = os.path.join(MAP_FOLDER, filename)
    try:
        with open(path, 'r') as f:
            MAP = json.load(f)
            current_map = filename
            MAP_WIDTH = len(MAP[0]) * TILE
            MAP_HEIGHT = len(MAP) * TILE

            for y, row in enumerate(MAP):
                for x, cell in enumerate(row):
                    tile_type, _ = cell
                    if tile_type == "P":
                        player_x = x * TILE + TILE // 2
                        player_y = y * TILE + TILE // 2
                        MAP[y][x][0] = 0  
                        print(f"Player spawn set to: ({x}, {y})")
                        break

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
        with open(os.path.join(MAP_FOLDER, "default.json"), 'w') as f:
            json.dump(MAP, f)
        map_list = ["default.json"]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_mods():
    global loaded_mods
    loaded_mods = []

    mods_folder = "mods"
    if not os.path.exists(mods_folder):
        try:
            os.mkdir(mods_folder)
            logger.info(f"Vytvořena složka '{mods_folder}'.")
        except OSError as e:
            logger.error(f"Chyba při vytváření složky '{mods_folder}': {e}")
            return

    for filename in os.listdir(mods_folder):
        if filename.endswith(".py"):
            mod_path = os.path.join(mods_folder, filename)
            
            if filename in loaded_mods:
                logger.info(f"Modul '{filename}' již byl načten.")
                continue
            
            try:
                spec = importlib.util.spec_from_file_location(filename, mod_path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                loaded_mods.append(filename)
                logger.info(f"Modul '{filename}' byl úspěšně načten.")
            except Exception as e:
                logger.error(f"Chyba při načítání modulu '{filename}': {e}")

    logger.info(f"Načtené moduly: {loaded_mods}")

def draw_menu():
    screen.fill((20, 20, 20))

    title = font.render("VoidRay Engine", True, (255, 255, 255))
    title_shadow = font.render("VoidRay Engine", True, (50, 50, 50))
    screen.blit(title_shadow, (WIDTH // 2 - title.get_width() // 2 + 2, HEIGHT // 5 + 2))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 5))

    version = font.render("Alpha 0.1.6V | made by Kitsune and Zuha", True, (180, 180, 180))
    version_shadow = font.render("Alpha 0.1.3V | made by Kitsune and Zuha", True, (50, 50, 50))
    screen.blit(version_shadow, (WIDTH // 2 - version.get_width() // 2 + 2, HEIGHT // 5 + 40 + 2))
    screen.blit(version, (WIDTH // 2 - version.get_width() // 2, HEIGHT // 5 + 40))

    info = font.render("[ENTER] Load map  |  [ESC] Exit  |  [↑/↓] Select Map", True, (150, 150, 150))
    info_glow = font.render("[ENTER] Load map  |  [ESC] Exit  |  [↑/↓] Select Map", True, (200, 200, 200))
    screen.blit(info_glow, (WIDTH // 2 - info.get_width() // 2 + 2, HEIGHT // 5 + 80 + 2))
    screen.blit(info, (WIDTH // 2 - info.get_width() // 2, HEIGHT // 5 + 80))

    map_list_start_y = HEIGHT // 2 - 40
    for i, name in enumerate(map_list):
        if i == map_index:
            label = font.render(f"> {name}", True, (255, 255, 0))
            label_shine = font.render(f"> {name}", True, (255, 255, 80))
            screen.blit(label_shine, (WIDTH // 2 - label.get_width() // 2 + 1, map_list_start_y + i * 30 + 1))
        else:
            label = font.render(f"> {name}", True, (150, 150, 150))
        screen.blit(label, (WIDTH // 2 - label.get_width() // 2, map_list_start_y + i * 30))

    controls = ["[WASD] Move", "[Space] Jump", "[Shift] Sprint", "[F3] Debug overlay"]
    controls_start_y = map_list_start_y + len(map_list) * 30 + 30
    for i, ctrl in enumerate(controls):
        text = font.render(ctrl, True, (100, 100, 100))
        text_glow = font.render(ctrl, True, (180, 180, 180))  
        screen.blit(text_glow, (WIDTH // 2 - text.get_width() // 2 + 1, controls_start_y + i * 25 + 1))
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, controls_start_y + i * 25))

    if loaded_mods:
        mods_title = font.render("Loaded Mods:", True, (200, 200, 100))
        mods_title_glow = font.render("Loaded Mods:", True, (255, 255, 150))
        screen.blit(mods_title_glow, (40, HEIGHT - 140 + 1))
        screen.blit(mods_title, (40, HEIGHT - 140))

        for i, mod in enumerate(loaded_mods[:3]):
            mod_text = font.render(f"- {mod}", True, (150, 150, 150))
            screen.blit(mod_text, (60, HEIGHT - 120 + i * 20))

    map_text = font.render(f"Current Map: {current_map}", True, (150, 150, 150))
    map_text_highlight = font.render(f"Current Map: {current_map}", True, (255, 255, 255))
    screen.blit(map_text_highlight, (WIDTH - map_text.get_width() - 40 + 1, HEIGHT - 100 + 1))
    screen.blit(map_text, (WIDTH - map_text.get_width() - 40, HEIGHT - 100))

    sysinfo = font.render(f"{WIDTH}x{HEIGHT} | {NUM_RAYS} rays", True, (80, 80, 80))
    sysinfo_shadow = font.render(f"{WIDTH}x{HEIGHT} | {NUM_RAYS} rays", True, (50, 50, 50))
    screen.blit(sysinfo_shadow, (WIDTH - sysinfo.get_width() - 40 + 1, HEIGHT - 40 + 1))
    screen.blit(sysinfo, (WIDTH - sysinfo.get_width() - 40, HEIGHT - 40))

    pygame.display.flip()

def check_collision(x, y):
    """Check if the position (x, y) collides with a solid tile."""
    tile_x, tile_y = int(x // TILE), int(y // TILE)

    if 0 <= tile_y < len(MAP) and 0 <= tile_x < len(MAP[0]):
        tile_type, _ = MAP[tile_y][tile_x]
        solid_tiles = {1, 3}  
        return tile_type in solid_tiles

    return True
    
def cast_rays():
    start_angle = player_angle - HALF_FOV
    ambient_light = 25
    sun_intensity = 1.2
    fog_density = 0.015

    for ray in range(NUM_RAYS):
        ray_angle = start_angle + ray * DELTA_ANGLE
        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)
        cos_fov_diff = math.cos(ray_angle - player_angle)

        for depth in range(1, MAX_DEPTH * 10):
            target_x = player_x + cos_a * depth
            target_y = player_y + sin_a * depth
            i, j = int(target_x // TILE), int(target_y // TILE)

            if 0 <= j < len(MAP) and 0 <= i < len(MAP[0]):
                tile_type, tile_height = MAP[j][i]

                corrected_depth = depth * cos_fov_diff
                if corrected_depth <= 0:
                    continue

                wall_height = PROJ_COEFF / corrected_depth
                wall_height = min(HEIGHT * 2, wall_height)
                y_offset = tile_height * 20
                screen_y = HEIGHT // 2 - wall_height // 2 - y_offset

                fog = math.exp(-fog_density * corrected_depth)
                light_angle = max(0.1, cos_fov_diff)  
                brightness = fog * (ambient_light + sun_intensity * 255 * light_angle)
                brightness = max(ambient_light, min(255, brightness))

                if tile_type == 1:
                    r = brightness
                    g = brightness * 0.92
                    b = brightness * 0.85
                    color = (int(r), int(g), int(b))
                    pygame.draw.rect(screen, color, pygame.Rect(ray * SCALE, screen_y, SCALE, wall_height))
                    break
            else:
                break 

def draw_fps():
    fps = int(clock.get_fps())
    px, py = int(player_x), int(player_y)
    tile_x, tile_y = int(player_x // TILE), int(player_y // TILE)
    angle_deg = int(math.degrees(player_angle)) % 360
    floor_height = MAP[tile_y][tile_x][1] if 0 <= tile_y < len(MAP) and 0 <= tile_x < len(MAP[0]) else 0

    lines = [
        f"FPS: {fps}",
        f"Pos: ({px}, {py})",
        f"Angle: {angle_deg}°",
        f"Tile: ({tile_x}, {tile_y})",
        f"Height: {player_z:.1f}",
        f"Floor height: {floor_height}",
        f"Speed: {round(math.hypot(dx, dy), 2)}",
        f"Jumping: {'Yes' if is_jumping else 'No'}",
        f"Map: {current_map}",
        f"Block: {MAP[tile_y][tile_x][0] if 0 <= tile_y < len(MAP) and 0 <= tile_x < len(MAP[0]) else 'None'}",
    ]

    for i, line in enumerate(lines):
        surface = font.render(line, True, (120, 255, 120))
        screen.blit(surface, (10, 10 + i * 20))

menu = True
load_mods()
load_map_list()  

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
