import pygame
from scripts.scenes.menu import Menu
from scripts.ui.style import text, button, panel, shade
from scripts.config import GOLD, MUTED, PURPLE


class Loja(Menu):
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER):
            self.game.show_menu()

    def draw(self, surface):
        self.art.draw(surface, self.time)
        shade(surface)
        panel(surface, (365, 196, 550, 331), PURPLE)
        text(surface, "LOJA", (640, 249), 54, GOLD, True, True)
        text(surface, "Em desenvolvimento", (640, 326), 34, center=True)
        text(surface, "Novos visuais chegarão em outro marco.", (640, 369), 23, MUTED, True)
        button(surface, "VOLTAR", (475, 427, 330, 62), True)
