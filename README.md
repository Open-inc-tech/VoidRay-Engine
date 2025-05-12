# 🔷 VOIDRAY ENGINE

A **modular 2.5D raycasting engine** inspired by *DOOM (1993)* — built entirely in **Python with Pygame**.  
Supports multiple floors, textured walls, gravity, jumping, dynamic JSON maps, and future mod support.

**Current Version:** `0.1.3V Alpha`  
**Created by:** Kitsune & Zuha

---

## 🧩 Features

- ✅ **Classic 2.5D raycasting engine**
- ✅ **Modular and extensible codebase**
- ✅ **Multiple floor height support**
- ✅ **Gravity and jumping physics**
- ✅ **Raycasting with depth correction**
- ✅ **Dynamic map loading (JSON format)**
- ✅ **Texture support for walls**
- ✅ **Mod loading system** *(planned)*
- ✅ **Engine ready for expansion** (enemies, items, editors)

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
