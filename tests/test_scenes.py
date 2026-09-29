import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import unittest
import pygame
from scripts.game import Game
from scripts.scenes.menu import Menu
from scripts.scenes.loja import Loja
from scripts.scenes.pausa import Pausa
from scripts.scenes.ringue_neon import RingueNeon


class SceneTests(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def tearDown(self):
        pygame.quit()

    def key(self, key):
        self.game.scene.handle_event(pygame.event.Event(pygame.KEYDOWN, key=key))

    def test_menu_shop_back_play_pause_resume_restart_menu_exit(self):
        self.game.scene.draw(self.game.screen)
        self.key(pygame.K_DOWN)
        self.key(pygame.K_RETURN)
        self.assertIsInstance(self.game.scene, Loja)
        self.game.scene.draw(self.game.screen)
        self.key(pygame.K_ESCAPE)
        self.assertIsInstance(self.game.scene, Menu)
        self.key(pygame.K_RETURN)
        match = self.game.scene
        self.assertIsInstance(match, RingueNeon)
        self.key(pygame.K_ESCAPE)
        self.assertIsInstance(self.game.scene, Pausa)
        self.game.scene.draw(self.game.screen)
        time_before = match.time
        self.game.scene.update(5)
        self.assertEqual(match.time, time_before)
        self.key(pygame.K_ESCAPE)
        self.assertIs(self.game.scene, match)
        match.player.health = 7
        self.key(pygame.K_ESCAPE)
        self.key(pygame.K_DOWN)
        self.key(pygame.K_RETURN)
        self.assertIsNot(self.game.scene, match)
        self.assertEqual(self.game.scene.player.health, 100)
        self.key(pygame.K_ESCAPE)
        self.key(pygame.K_DOWN)
        self.key(pygame.K_DOWN)
        self.key(pygame.K_DOWN)
        self.key(pygame.K_DOWN)
        self.key(pygame.K_RETURN)
        self.assertIsInstance(self.game.scene, Menu)
        self.key(pygame.K_UP)
        self.key(pygame.K_RETURN)
        self.assertFalse(self.game.running)

    def test_result_restart_and_return(self):
        self.key(pygame.K_RETURN)
        self.game.scene.enemy.health = 0
        self.game.scene.check_result()
        self.key(pygame.K_r)
        self.assertIsNone(self.game.scene.result)
        self.game.scene.player.health = 0
        self.game.scene.check_result()
        self.key(pygame.K_RETURN)
        self.assertIsInstance(self.game.scene, Menu)

    def test_headless_loop(self):
        self.game.run(max_frames=3)
        self.assertFalse(self.game.running)
