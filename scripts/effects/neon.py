"""Paleta da arena e glows em superfícies locais reutilizáveis."""
from functools import lru_cache
import pygame

BLUE = (25, 90, 255)
CYAN = (5, 235, 255)
PINK = (255, 24, 79)
PURPLE = (164, 44, 255)
GOLD = (255, 220, 45)


def glow_line(surface, color, start, end, width=2):
    margin = width + 16
    x, y = min(start[0], end[0]) - margin, min(start[1], end[1]) - margin
    w, h = abs(end[0] - start[0]) + margin * 2, abs(end[1] - start[1]) + margin * 2
    layer = pygame.Surface((int(w) + 1, int(h) + 1), pygame.SRCALPHA)
    a, b = (start[0] - x, start[1] - y), (end[0] - x, end[1] - y)
    for extra, alpha in ((24, 12), (14, 24), (6, 65), (0, 240)):
        pygame.draw.line(layer, (*color, alpha), a, b, width + extra)
    surface.blit(layer, (x, y))
    pygame.draw.line(surface, tuple(min(255, c + 75) for c in color), start, end, max(1, width // 2))


@lru_cache(maxsize=24)
def halo(color, radius):
    s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    for r in range(radius, 0, -3):
        alpha = int(26 * (1 - r / radius) ** 1.4)
        pygame.draw.circle(s, (*color, alpha), (radius, radius), r)
    return s


def pan(surface, center, angle=0, scale=1, color=GOLD):
    from scripts.effects.pan_art import pan as draw_pan
    return draw_pan(surface,center,angle,scale,color)


@lru_cache(maxsize=8)
def pan_sprite(color):
    s = pygame.Surface((100, 66), pygame.SRCALPHA)
    glow_line(s, color, (58, 33), (92, 42), 7)
    pygame.draw.ellipse(s, (78, 66, 22), (19, 18, 48, 33))
    pygame.draw.ellipse(s, color, (17, 13, 52, 29), 3)
    pygame.draw.ellipse(s, (12, 14, 29), (21, 16, 44, 21))
    pygame.draw.arc(s, (255, 249, 158), (22, 17, 40, 19), .1, 2.8, 2)
    pygame.draw.lines(s, color, False, [(22, 22), (10, 18), (6, 29), (20, 34)], 3)
    return s
