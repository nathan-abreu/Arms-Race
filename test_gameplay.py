import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import random
import unittest
import pygame
from scripts.combat.weapon import PAN, FISTS, Inventory, WeaponDrop
from scripts.config import CYAN, PINK, FIXED_DT
from scripts.data import load_level
from scripts.entities.fighter import Fighter
from scripts.scenes.ringue_neon import RingueNeon


class CombatTests(unittest.TestCase):
    def setUp(self):
        self.a = Fighter((400, 550), CYAN)
        self.b = Fighter((445, 550), PINK)

    def test_damage_knockback_and_unique_hit(self):
        self.assertTrue(self.a.attack())
        self.a.update(.045, [])
        self.assertTrue(self.a.resolve_attack(self.b))
        self.assertEqual(self.b.health, 93)
        self.assertGreater(self.b.velocity.x, 0)
        self.assertLess(self.b.velocity.y, 0)
        self.b.invulnerable = 0
        self.assertFalse(self.a.resolve_attack(self.b))
        self.assertEqual(self.b.health, 93)

    def test_cooldown_and_expiration(self):
        self.a.attack()
        self.a.update(.045, [])
        self.assertFalse(self.a.attack())
        for _ in range(10):
            self.a.update(FIXED_DT, [])
        self.assertEqual(self.a.attack_time, 0)
        self.assertFalse(self.a.resolve_attack(self.b))
        for _ in range(12):
            self.a.update(FIXED_DT, [])
        self.assertTrue(self.a.attack())
        self.a.update(.045, [])

    def test_invulnerability_and_health_clamp(self):
        self.assertTrue(self.b.receive_damage(10, 200, -1))
        self.assertLess(self.b.velocity.x, 0)
        self.assertFalse(self.b.receive_damage(10, 200, -1))
        self.b.update(.31, [])
        self.assertTrue(self.b.receive_damage(999, 200, -1))
        self.assertEqual(self.b.health, 0)
        self.assertFalse(self.b.alive)

    def test_pan_range_damage_and_attack_snapshot(self):
        self.b.pos.x = 494
        self.a.attack()
        self.a.update(.045, [])
        self.assertFalse(self.a.resolve_attack(self.b))
        self.a.cooldown = 0
        self.a.inventory.collect(PAN)
        self.a.attack()
        self.a.update(.085, [])
        self.a.inventory.cycle(1)
        self.assertTrue(self.a.resolve_attack(self.b))
        self.assertEqual(self.b.health, 100-PAN.damage)
        self.assertEqual(self.b.velocity.x, PAN.knockback)
        self.assertGreater(PAN.knockback, FISTS.knockback)

    def test_left_attack_and_out_of_vertical_range(self):
        self.a.facing = -1
        self.b.pos.x = 355
        self.a.attack()
        self.a.update(.045, [])
        self.assertTrue(self.a.resolve_attack(self.b))
        self.assertLess(self.b.velocity.x, 0)
        self.a.cooldown = 0
        self.a.attack()
        self.a.update(.045, [])
        self.b.pos.y -= 150
        self.assertFalse(self.a.resolve_attack(self.b))

    def test_platform_jump_landing_and_air_jump_block(self):
        platform = pygame.Rect(160, 550, 960, 30)
        for _ in range(3):
            self.a.update(FIXED_DT, [platform])
        self.assertTrue(self.a.grounded)
        self.assertTrue(self.a.jump())
        self.assertFalse(self.a.jump())
        for _ in range(100):
            self.a.update(FIXED_DT, [platform])
        self.assertEqual(self.a.pos.y, 550)
        self.assertTrue(self.a.grounded)

    def test_suspended_platform_and_falling_outside(self):
        platforms = [pygame.Rect(160, 550, 960, 30), pygame.Rect(310, 430, 200, 18)]
        self.a.grounded = True
        self.a.jump()
        for _ in range(70):
            self.a.update(FIXED_DT, platforms)
        self.assertEqual(self.a.pos.y, 430)
        self.a.pos.x = 1200
        for _ in range(90):
            self.a.update(FIXED_DT, platforms)
        self.assertFalse(self.a.alive)


class InventoryTests(unittest.TestCase):
    def test_three_slots_cycle_full_and_discard(self):
        inv = Inventory()
        inv.cycle(-1)
        self.assertEqual(inv.selected, 2)
        inv.cycle(1)
        self.assertEqual(inv.selected, 0)
        for _ in range(3):
            self.assertTrue(inv.collect(PAN))
        self.assertTrue(inv.full)
        before = list(inv.slots)
        self.assertFalse(inv.collect(PAN))
        self.assertEqual(inv.slots, before)
        self.assertEqual(inv.discard(), PAN)
        self.assertIs(inv.weapon, FISTS)
        self.assertIsNone(inv.discard())

    def test_drop_warning_fall_collect_unique_and_discard(self):
        level = load_level()
        platforms = [pygame.Rect(p) for p in level["platforms"]]
        drop = WeaponDrop(level, random.Random(0))
        a, b = Fighter((640, 550), CYAN), Fighter((640, 550), PINK)
        drop.update(6.01, (a, b), platforms)
        self.assertEqual(drop.state, "warning")
        self.assertFalse(drop.try_collect(a))
        drop.update(.7, (a, b), platforms)
        self.assertEqual(drop.state, "warning")
        for _ in range(180):
            drop.update(FIXED_DT, (a, b), platforms)
        self.assertEqual(drop.state, "available")
        a.pos.x = b.pos.x = drop.x
        self.assertTrue(drop.try_collect(a))
        self.assertFalse(drop.try_collect(b))
        drop.update(100, (a, b), platforms)
        self.assertEqual(drop.state, "held")
        self.assertTrue(drop.discard(a))
        self.assertNotIn(PAN, a.inventory.slots)
        for _ in range(30):
            drop.update(FIXED_DT, (a, b), platforms)
        a.pos.x = b.pos.x = drop.x
        self.assertEqual(drop.state, "available")
        self.assertFalse(drop.try_collect(a))
        self.assertTrue(drop.try_collect(b))

    def test_full_inventory_blocks_ground_pickup(self):
        drop = WeaponDrop(load_level(), random.Random(0))
        fighter = Fighter((640, 550), CYAN)
        fighter.inventory.slots = [FISTS, FISTS, FISTS]
        drop.state, drop.x, drop.y = "available", 640, 540
        self.assertFalse(drop.try_collect(fighter))
        self.assertEqual(drop.state, "available")

    def test_lost_pan_respawns_with_new_warning(self):
        level = load_level()
        platforms = [pygame.Rect(p) for p in level["platforms"]]
        drop = WeaponDrop(level, random.Random(1))
        fighter = Fighter((1200, 550), CYAN)
        fighter.inventory.collect(PAN)
        drop.discard(fighter)
        for _ in range(120):
            drop.update(FIXED_DT, (fighter,), platforms)
        self.assertEqual(drop.state, "waiting")
        # Aguarda o próximo aviso, sem supor a duração da queda descartada.
        for _ in range(360):
            drop.update(FIXED_DT, (fighter,), platforms)
            if drop.state=='warning': break
        self.assertEqual(drop.state, "warning")


class MatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.display.init()
        pygame.font.init()
        pygame.display.set_mode((1280, 720))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.match = RingueNeon(None, seed=2)

    def test_victory_health_and_freeze(self):
        self.match.enemy.health = 0
        self.match.simulate(FIXED_DT)
        self.assertEqual(self.match.result, "VITÓRIA")
        before = (self.match.time, self.match.player.pos.copy(), self.match.drop.timer)
        for _ in range(100):
            self.match.simulate(FIXED_DT)
        self.assertEqual(before, (self.match.time, self.match.player.pos, self.match.drop.timer))

    def test_lethal_pan_hit_triggers_victory_in_simulation(self):
        player, enemy = self.match.fighters
        player.pos.update(600, 550)
        enemy.pos.update(675, 550)
        enemy.health = PAN.damage
        enemy.cooldown = 1
        player.inventory.collect(PAN)
        player.attack()
        for _ in range(4):
            self.match.simulate(FIXED_DT)
        self.assertEqual(enemy.health, 0)
        self.assertEqual(self.match.result, "VITÓRIA")
        self.assertGreater(enemy.velocity.x, 0)
        self.assertGreater(self.match.shake, 0)
        self.assertTrue(self.match.particles.items)

    def test_player_keyboard_inventory_attack_jump_and_movement(self):
        from collections import defaultdict
        p = self.match.player
        p.grounded = True
        for key in (pygame.K_SPACE,):
            p.handle_event(pygame.event.Event(pygame.KEYDOWN, key=key), self.match.drop)
        p.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1), self.match.drop)
        self.assertLess(p.velocity.y, 0)
        self.assertGreater(p.attack_time, 0)
        p.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_q), self.match.drop)
        self.assertEqual(p.inventory.selected, 2)
        p.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e), self.match.drop)
        self.assertEqual(p.inventory.selected, 0)
        p.inventory.collect(PAN)
        p.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_x), self.match.drop)
        self.assertNotIn(PAN, p.inventory.slots)
        keys = defaultdict(bool, {pygame.K_a: True})
        p.read_input(keys)
        p.update(FIXED_DT, self.match.platforms)
        self.assertEqual(p.facing, -1)
        self.assertLess(p.velocity.x, 0)

    def test_fall_victory_and_both_defeats(self):
        self.match.enemy.pos.y = 810
        self.match.simulate(FIXED_DT)
        self.assertEqual(self.match.result, "VITÓRIA")
        for health, y in ((0, 550), (100, 810)):
            match = RingueNeon(None)
            match.player.health, match.player.pos.y = health, y
            match.simulate(FIXED_DT)
            self.assertEqual(match.result, "DERROTA")

    def test_enemy_pursues_attacks_and_ends_idle_match(self):
        start = self.match.enemy.pos.x
        for _ in range(60):
            self.match.simulate(FIXED_DT)
        self.assertLess(self.match.enemy.pos.x, start)
        for _ in range(60 * 45):
            self.match.simulate(FIXED_DT)
        self.assertEqual(self.match.result, "DERROTA")

    def test_enemy_targets_weapon_jumps_and_avoids_edge(self):
        enemy, player, drop = self.match.enemy, self.match.player, self.match.drop
        enemy.pos.update(850, 550)
        player.pos.update(1000, 550)
        drop.state, drop.x, drop.y = "available", 640, 540
        enemy.decide(FIXED_DT, player, drop, self.match.platforms)
        self.assertEqual(enemy.state, "buscar arma")
        self.assertEqual(enemy.axis, -1)
        drop.state = "waiting"
        player.pos.update(800, 395)
        enemy.grounded = True
        enemy.decide(.25, player, drop, self.match.platforms)
        self.assertLess(enemy.velocity.y, 0)
        enemy.pos.x = self.match.platforms[0].right-5
        enemy.decide(FIXED_DT, player, drop, self.match.platforms)
        self.assertEqual(enemy.axis, -1)

    def test_rope_bounce_and_escape_above_rope(self):
        p = self.match.player
        floor=self.match.platforms[0]
        p.pos.update(floor.left+5, floor.top-5)
        self.match._ropes(p, floor.left+20)
        self.assertGreater(p.velocity.x, 0)
        p.rope_cooldown = 0
        p.velocity.x = -300
        p.pos.update(floor.left+5, floor.top-140)
        self.match._ropes(p, floor.left+20)
        self.assertEqual(p.velocity.x, -300)

    def test_render_active_warning_weapon_and_result(self):
        screen = pygame.display.get_surface()
        for state in ("waiting", "warning", "falling", "available", "held"):
            self.match.drop.state = state
            self.match.draw(screen)
        self.match.enemy.health = 0
        self.match.check_result()
        self.match.draw(screen)


if __name__ == "__main__":
    unittest.main()
