import pygame
from scripts.config import CYAN
from scripts.entities.fighter import Fighter


class Player(Fighter):
    def __init__(self, position):
        super().__init__(position, CYAN)

    def handle_event(self, event, weapon_drop):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.attack()
            return
        if event.type == pygame.MOUSEWHEEL:
            self.inventory.cycle(-event.y)
            self.events.append('slot_switch' if self.inventory.display_slots[self.inventory.selected] else 'slot_empty')
            return
        if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
            self.release_jump()
            return
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_SPACE:
            self.request_jump()
        elif event.key == pygame.K_q:
            self.inventory.cycle(-1)
            self.events.append('slot_switch' if self.inventory.display_slots[self.inventory.selected] else 'slot_empty')
        elif event.key == pygame.K_e:
            self.inventory.cycle(1)
            self.events.append('slot_switch' if self.inventory.display_slots[self.inventory.selected] else 'slot_empty')
        elif event.key == pygame.K_x:
            weapon_drop.discard(self)

    def read_input(self, keys):
        self.axis = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
