"""Cenário de combate com estruturas, arquibancada e iluminação."""
import math
import random
import pygame
from scripts.config import WIDTH, HEIGHT, BACKGROUND, CYAN, PINK, PURPLE
from scripts.ui.style import line, panel, text


class ArenaArt:
    def __init__(self, platforms, signage=True):
        self.platforms = platforms
        self.signage = signage
        self.background = pygame.Surface((WIDTH, HEIGHT))
        self._build_background()

    def _build_background(self):
        s = self.background
        s.fill(BACKGROUND)
        for y in range(HEIGHT):
            pygame.draw.line(s, (10 + y // 110, 11 + y // 150, 26 + y // 45), (0, y), (WIDTH, y))
        rng = random.Random(71)
        for x in range(0, WIDTH, 43):
            h = rng.randrange(100, 340)
            pygame.draw.rect(s, (9, 12, 27), (x, 475 - h, 35, h))
            for yy in range(485 - h, 450, 25):
                if rng.random() < 0.6:
                    pygame.draw.rect(s, (25, 31, 65), (x + 8, yy, 4, 9))
        # Travessas e holofotes dão escala de arena fechada.
        for x in (100, 1180):
            pygame.draw.rect(s, (21, 24, 48), (x - 12, 90, 24, 550))
            for y in range(100, 620, 46):
                pygame.draw.line(s, (46, 38, 89), (x - 12, y), (x + 12, y + 40), 3)
        for y in (180, 285, 470):
            pygame.draw.lines(s, (38, 33, 76), False, [(0, y - 35), (250, y), (1030, y), (1280, y - 35)], 5)
        for x in range(20, 1280, 24):
            y = 475 + rng.randrange(-18, 18)
            pygame.draw.circle(s, (9, 9, 24), (x, y - 16), 7)
            pygame.draw.rect(s, (9, 9, 24), (x - 8, y - 9, 16, 29))
            if rng.random() < .5:
                pygame.draw.line(s, rng.choice((CYAN, PURPLE, PINK)), (x + 8, y - 4), (x + 13, y - 23), 2)
        for y in range(490, 720, 24):
            pygame.draw.line(s, (29, 26, 61), (0, y), (1280, y))
        for x in range(-700, 2000, 100):
            pygame.draw.line(s, (29, 26, 61), (640 + (x - 640) * .3, 475), (x, 720))
        if self.signage:
            panel(s, (535, 190, 210, 112), PURPLE, (13, 16, 39))
            text(s, "AR / 01", (640, 231), 48, CYAN, True, True)
            text(s, "RINGUE NEON", (640, 271), 22, PURPLE, True)

    def draw(self, surface, time):
        surface.blit(self.background, (0, 0))
        lights = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for x, color, phase in ((220, CYAN, 0), (1060, PINK, 2), (640, PURPLE, 4)):
            drift = math.sin(time * .4 + phase) * 90
            pygame.draw.polygon(lights, (*color, 13), [(x - 12, 105), (x + 12, 105),
                                                     (x + drift + 160, 550), (x + drift - 160, 550)])
            pygame.draw.rect(lights, (*color, 230), (x - 17, 97, 34, 8))
        surface.blit(lights, (0, 0))
        # Duas linhas traseiras e quatro postes; a frente fica livre para leitura.
        for y, color in ((470, CYAN), (505, PURPLE), (535, CYAN)):
            line(surface, color, (175, y), (1105, y), 2)
        for x, back in ((175, True), (1105, True), (145, False), (1135, False)):
            top = 450 if back else 470
            panel(surface, (x - 10, top, 20, 550 - top), PURPLE, (10, 14, 31))
            line(surface, CYAN if back else PINK, (x, top + 9), (x, 543), 3)
        for i, p in enumerate(self.platforms):
            color = CYAN if i == 0 else PURPLE
            pygame.draw.rect(surface, (9, 11, 26), p)
            line(surface, color, p.topleft, p.topright, 3)
            pygame.draw.line(surface, (49, 47, 92), p.bottomleft, p.bottomright, 2)
            for x in range(p.x + 12, p.right - 10, 42):
                pygame.draw.line(surface, (36, 38, 73), (x, p.y + 8), (x + 20, p.bottom - 3), 2)
            if i == 0:
                for x in (235, 1045):
                    pygame.draw.polygon(surface, (16, 19, 41), [(x - 28, p.bottom), (x + 28, p.bottom), (x + 55, 640), (x - 55, 640)])
                    line(surface, PURPLE, (x - 21, 589), (x + 21, 589), 3)
