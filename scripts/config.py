from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIDTH, HEIGHT = 1280, 720
FPS = 60
FIXED_DT = 1 / FPS
BACKGROUND = (12, 12, 29)
CYAN = (60, 200, 255)
PINK = (255, 65, 116)
PURPLE = (151, 73, 255)
GOLD = (255, 220, 60)
WHITE = (240, 240, 255)
MUTED = (140, 152, 188)
from scripts.balance import MOVEMENT
GRAVITY = MOVEMENT.gravity
SPEED = MOVEMENT.speed
JUMP_SPEED = MOVEMENT.jump_speed
INVULNERABILITY = MOVEMENT.invulnerability
