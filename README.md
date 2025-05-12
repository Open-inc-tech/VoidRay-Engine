# 🔷 VOIDRAY ENGINE

A **modular 2.5D raycasting engine** inspired by *DOOM (1993)* — built entirely in **Python with Pygame**.  
Supports multiple floors, textured walls, gravity, jumping, dynamic JSON maps, and future mod support.

**Current Version:** `0.1.6V Alpha`  
**Created by:** Kitsune & Zuha

---

## 🧩 Features

-✅ **Classic 2.5D raycasting renderer (inspired by DOOM/Wolfenstein 3D)**

-✅ **Accurate depth-corrected raycasting**

-✅ **Multiple floor & ceiling heights with z-axis support**

-✅ **Jumping, gravity, and smooth vertical movement**

-✅ **Strafing and mouse look support (WASD + full mouse camera control)**

-✅ **Dynamic lighting and shading based on distance and direction**

-✅ **Texture support for walls and special tiles (walls, windows, transparent blocks)**

-✅ **Transparent walls and window rendering (render-through raycasting)**

-✅ **Interactive elements support (planned: doors, switches)**

-✅ **Modular & extensible codebase for easy hacking and expansion**

-✅ **Dynamic map loading using external .json files**

-✅ **Built-in map editor (optional/expandable)**

-✅ **Mod loading system (planned) – load custom content, textures, logic**

-✅ **Map saving and hot-reloading (F5 to save, F9 to reload)**

-✅ **Simple menu system with map selection**

-✅ **Performance-friendly rendering (scalable resolution/raycast count)**

-✅ **Debug overlay (FPS, player info) with toggle (F3)**

-✅ **Safe error handling and fallback mechanisms (e.g. missing maps)**

-✅ **Future-ready architecture (supports AI, enemies, scripting)**

-✅ **ASCII/console rendering version (optional, alternate rendering mode)**

---

## 🎮 Controls

| Key      | Action               |
|----------|----------------------|
| `W / S`  | Move forward / backward |
| `A / D`  | Strafe left / right  |
| `SPACE`  | Jump                 |
| `ENTER`  | Start from menu      |
| `ESC`    | Quit the game        |

---

## 🗺️ Map Format (`map.json`)

Maps are defined using a nested list of tiles:

json
[
  [[1, 0], [0, 0], [1, 0]],
  [[1, 0], [0, 1], [1, 0]]
]
Where:

1 = wall, 0 = empty

Second value = floor height (0 = ground, 1+ = elevation)

---

🛠️ Requirements
Python 3.8+

Pygame (no external libraries required)

Install Pygame:
pip install pygame

---

💬 Credits
Engine design and Code by Kitsune
Code and expansion by Zuha
