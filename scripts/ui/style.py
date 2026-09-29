"""Primitivas vetoriais neon; nenhuma imagem externa é necessária."""
from functools import lru_cache
import pygame
from scripts.config import CYAN, WHITE, PURPLE, MUTED


@lru_cache(maxsize=32)
def font(size, bold=False):
    # Fonte incluída no Pygame: resultado consistente e execução offline.
    result = pygame.font.Font(None, size)
    result.set_bold(bold)
    return result


@lru_cache(maxsize=512)
def rendered_text(label,size,color,bold):
    return font(size,bold).render(label,True,color)


def text(surface, label, pos, size=24, color=WHITE, center=False, bold=False):
    rendered = rendered_text(label,size,tuple(color),bold)
    rect = rendered.get_rect(center=pos) if center else rendered.get_rect(topleft=pos)
    surface.blit(rendered, rect)
    return rect


def line(surface, color, start, end, width=2):
    pygame.draw.line(surface, tuple(c // 6 for c in color), start, end, width + 8)
    pygame.draw.line(surface, tuple(c // 3 for c in color), start, end, width + 4)
    pygame.draw.line(surface, color, start, end, width)


def panel(surface, rect, color=CYAN, fill=(13, 18, 38), width=2):
    r = pygame.Rect(rect)
    c = min(15, r.height // 4)
    pts = [(r.x + c, r.y), (r.right - c, r.y), (r.right, r.y + c),
           (r.right, r.bottom - c), (r.right - c, r.bottom),
           (r.x + c, r.bottom), (r.x, r.bottom - c), (r.x, r.y + c)]
    pygame.draw.polygon(surface, fill, pts)
    pygame.draw.polygon(surface, tuple(v // 4 for v in color), pts, width + 5)
    pygame.draw.polygon(surface, color, pts, width)


def button(surface, label, rect, selected):
    panel(surface, rect, CYAN if selected else PURPLE,
          (16, 40, 59) if selected else (18, 16, 42), 3 if selected else 2)
    text(surface, label, pygame.Rect(rect).center, 34, WHITE if selected else MUTED, True, True)
    if selected:
        text(surface, "›", (rect[0] + 23, rect[1] + rect[3] // 2), 34, CYAN, True)


@lru_cache(maxsize=8)
def shade_surface(size):
    overlay = pygame.Surface(size, pygame.SRCALPHA)
    overlay.fill((3, 5, 17, 200))
    return overlay


def shade(surface):
    surface.blit(shade_surface(surface.get_size()), (0, 0))
