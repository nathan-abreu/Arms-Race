import math
import pygame
from scripts.config import CYAN, PINK, PURPLE, MUTED
from scripts.data import load_level
from scripts.effects.arena import ArenaArt
from scripts.entities.fighter import Fighter
from scripts.scenes.base import Scene
from scripts.ui.style import text, button, line


class Menu(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.selected = 0
        self.time = 0.0
        self.art = ArenaArt([pygame.Rect(p) for p in load_level()["platforms"]], signage=False)
        self.decorations = [Fighter((235, 550), CYAN), Fighter((1045, 550), PINK)]
        self.decorations[1].facing = -1
        for fighter in self.decorations:
            fighter.grounded = True
            fighter.legacy_art = True

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_UP, pygame.K_w):
            self.selected = (self.selected - 1) % 3
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.selected = (self.selected + 1) % 3
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            if self.selected == 0:
                self.game.start_match()
            elif self.selected == 1:
                from scripts.scenes.loja import Loja
                self.game.change_scene(Loja(self.game))
            else:
                self.game.running = False
        elif event.key == pygame.K_ESCAPE:
            self.game.running = False

    def update(self, dt):
        self.time += dt
        for fighter in self.decorations:
            fighter.animation_time += dt

    def draw(self, surface):
        self.art.draw(surface, self.time)
        veil = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        veil.fill((5, 5, 19, 95))
        surface.blit(veil, (0, 0))
        for fighter in self.decorations:
            fighter.draw(surface)
        text(surface, "ARMS", (640, 165), 132, CYAN, True, True)
        text(surface, "RACE", (640, 260), 132, PINK, True, True)
        offset = math.sin(self.time) * 12
        line(surface, CYAN, (427 + offset, 103), (560 + offset, 103))
        line(surface, PINK, (724 - offset, 310), (862 - offset, 310))
        text(surface, "ADAPTE-SE. DISPUTE. SOBREVIVA.", (640, 329), 21, MUTED, True)
        for i, label in enumerate(("JOGAR", "LOJA", "SAIR")):
            button(surface, label, (475, 367 + i * 76, 330, 59), i == self.selected)
        text(surface, "SETAS / W S   navegar       ENTER   confirmar       ESC   sair", (640, 640), 23, MUTED, True)
        text(surface, "MARCO 1   /   RINGUE NEON", (640, 688), 20, PURPLE, True)
