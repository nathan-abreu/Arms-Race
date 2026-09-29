import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import unittest
import pygame
from scripts.game import Game
from scripts.config import FIXED_DT
from scripts.combat.weapon import PAN, FISTS
from scripts.effects.neon import GOLD


class PresentationTests(unittest.TestCase):
    def setUp(self):
        self.game = Game("ringue")
        self.m = self.game.scene
        self.m.flow.phase="fight"
        for f,x in zip(self.m.fighters,(390,850)):
            f.pos.update(x,self.m.platforms[0].top)
            f.grounded=True

    def tearDown(self):
        pygame.quit()

    def test_windup_cannot_hit_then_active_window_can(self):
        a,b=self.m.fighters
        b.pos.x=a.pos.x+48
        a.attack()
        self.assertFalse(a.resolve_attack(b))
        a.update(.05,self.m.platforms)
        self.assertTrue(a.resolve_attack(b))
        for _ in range(8):
            a.update(FIXED_DT,self.m.platforms)
        self.assertEqual(a.attack_time,0)
        self.assertGreater(a.recovery,0)

    def test_pan_short_fast_low_damage_moderate_impulse(self):
        self.assertEqual(PAN.name,"Panela")
        self.assertLess(PAN.damage,12)
        self.assertLess(PAN.cooldown,.4)
        self.assertLess(PAN.reach,60)
        self.assertGreater(PAN.knockback,FISTS.knockback)
        self.assertLess(PAN.knockback,400)

    def test_safe_warning_points_avoid_platforms_and_edges(self):
        for _ in range(20):
            self.m.drop.state="waiting"
            self.m.drop.timer=0
            self.m.drop.update(FIXED_DT,self.m.fighters,self.m.platforms)
            x=self.m.drop.x
            self.assertTrue(250<x<1030)
            self.assertFalse(any(p.left-35<x<p.right+35 for p in self.m.platforms[1:]))

    def test_sky_hit_once_and_ground_impact_once(self):
        d=self.m.drop
        a=self.m.player
        a.pos.x=640
        d.state,d.x,d.y,d.vy="falling",640,420,500
        d.update(FIXED_DT,self.m.fighters,self.m.platforms)
        self.assertEqual(a.health,92)
        self.assertNotEqual(a.velocity.x,0)
        impacts=0
        for _ in range(80):
            a.invulnerable=0
            d.update(FIXED_DT,self.m.fighters,self.m.platforms)
            impacts += d.impact_event is not None
        self.assertEqual(a.health,92)
        self.assertEqual(impacts,1)
        self.assertEqual(d.state,"available")

    def test_landing_delays_collection_and_emits_feedback(self):
        d=self.m.drop
        d.state,d.x,d.y,d.vy="falling",640,self.m.platforms[0].top-21,300
        self.m.simulate(FIXED_DT)
        self.assertEqual(d.state,"available")
        self.m.player.pos.x=640
        self.assertFalse(d.try_collect(self.m.player))
        self.assertGreater(self.m.hit_stop,0)
        self.assertGreater(self.m.shake,0)
        self.assertTrue(self.m.impacts.waves)
        self.assertGreater(self.m.camera.trauma,0)
        d.update(.13,self.m.fighters,self.m.platforms)
        self.assertTrue(d.try_collect(self.m.player))

    def test_cpu_retreats_from_warning_then_collects(self):
        e,d=self.m.enemy,self.m.drop
        d.state,d.x="warning",640
        e.pos.x=645
        e.decide(FIXED_DT,self.m.player,d,self.m.platforms)
        self.assertEqual(e.state,"desviar de item")
        self.assertEqual(e.axis,1)
        d.state,d.y="available",self.m.platforms[0].top-10
        e.pos.x=745
        e.decide(FIXED_DT,self.m.player,d,self.m.platforms)
        self.assertEqual(e.state,"buscar arma")
        self.assertEqual(e.axis,-1)
        for _ in range(90):
            self.m.simulate(FIXED_DT)
        self.assertIn(PAN,e.inventory.slots)

    def test_cpu_low_health_can_decline_distant_weapon(self):
        e,d=self.m.enemy,self.m.drop
        d.state,d.x="warning",580
        e.health=10
        e.pos.x=1000
        self.m.player.pos.x=580
        e.decide(FIXED_DT,self.m.player,d,self.m.platforms)
        self.assertEqual(e.state,"aproximar")

    def test_health_lag_and_camera_are_time_based(self):
        p=self.m.player
        p.health=60
        self.m.hud.update(FIXED_DT,self.m.fighters)
        self.assertEqual(self.m.hud.delayed[0],100)
        for _ in range(90):
            self.m.hud.update(FIXED_DT,self.m.fighters)
        self.assertEqual(self.m.hud.delayed[0],60)
        p.pos.x=180
        p.velocity.x=-300
        self.m.camera.impulse(.4)
        self.m.camera.update(.1,self.m.fighters)
        self.assertTrue(1<self.m.camera.zoom<=1.065)

    def test_effect_limits_and_audio_contract(self):
        for _ in range(200):
            self.m.impacts.emit((640,550),GOLD)
            self.m.particles.burst((640,550),GOLD)
        self.assertLessEqual(len(self.m.particles.items),180)
        self.assertLessEqual(len(self.m.impacts.waves),16)
        self.assertLessEqual(len(self.m.impacts.audio_events),24)
        self.assertTrue(self.m.impacts.drain_audio_events())
        self.assertFalse(self.m.impacts.audio_events)

    def test_hit_stop_freezes_physics_and_result_allows_celebration(self):
        self.m.hit_stop=.04
        before=self.m.player.pos.copy()
        self.m.simulate(FIXED_DT)
        self.assertEqual(self.m.player.pos,before)
        self.m.impacts.emit((640,550),GOLD)
        self.m.enemy.health=0
        self.m.check_result()
        self.m.simulate(.1)
        self.assertGreater(self.m.impacts.waves[0][1],0)
        self.assertEqual(self.m.enemy.health,0)
        self.assertTrue(self.m.player.celebrating)


if __name__=="__main__":
    unittest.main()
