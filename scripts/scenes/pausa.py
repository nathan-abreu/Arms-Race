import pygame
from scripts.scenes.base import Scene
from scripts.ui.style import text, button, shade, panel
from scripts.config import CYAN, MUTED


class Pausa(Scene):
    def __init__(self, game, match):
        super().__init__(game)
        self.match = match
        self.selected = 0

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_ESCAPE:
            self.match.player.release_jump()
            self.game.change_scene(self.match)
        elif event.key in (pygame.K_UP, pygame.K_w):
            self.selected = (self.selected - 1) % 5
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.selected = (self.selected + 1) % 5
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            if self.selected == 0:
                self.match.player.release_jump()
                self.game.change_scene(self.match)
            elif self.selected == 1:
                self.game.start_match()
            elif self.selected in (2,3):
                from scripts.scenes.options import Controls,Options
                self.game.change_scene((Controls if self.selected==2 else Options)(self.game,self))
            else:
                self.game.show_menu()

    def draw(self, surface):
        self.match.draw(surface)
        shade(surface)
        panel(surface, (402, 126, 476, 489), CYAN)
        text(surface, "PAUSADO", (640, 177), 52, CYAN, True, True)
        for i, label in enumerate(("Continuar", "Reiniciar", "Controles", "Configurações", "Voltar ao menu")):
            button(surface, label, (453, 219 + i * 67, 374, 54), self.selected == i)
        text(surface, "ENTER  confirmar    ESC  continuar", (640, 584), 22, MUTED, True)
