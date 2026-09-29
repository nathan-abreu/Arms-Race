import os
os.environ["SDL_VIDEODRIVER"]="dummy"
os.environ["SDL_AUDIODRIVER"]="dummy"
import unittest
from unittest.mock import patch
from collections import defaultdict
import pygame
from scripts.entities.player import Player
from scripts.entities.enemy import Enemy
from scripts.entities.fighter import Fighter
from scripts.combat.weapon import PAN,WeaponDrop
from scripts.balance import MOVEMENT,AI
from scripts.config import FIXED_DT
from scripts.settings import Settings
from scripts.audio.manager import AudioManager
from scripts.data import load_level
from scripts.game import Game
from scripts.scenes.pausa import Pausa
from scripts.scenes.options import Options,Controls
from scripts.viewport import Viewport
import random


class MovementTests(unittest.TestCase):
    def setUp(self):
        self.f=Player((400,550))
        self.floor=[pygame.Rect(160,550,960,30)]
        self.f.grounded=True
        self.drop=WeaponDrop(load_level(),random.Random(1))

    def tick(self,n=1):
        for _ in range(n): self.f.update(FIXED_DT,self.floor)

    def test_space_only_jumps_w_has_no_action(self):
        self.f.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_w),self.drop)
        self.assertEqual(self.f.velocity.y,0)
        self.f.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_SPACE),self.drop)
        self.assertLess(self.f.velocity.y,0)
        self.assertEqual(self.f.attack_time,0)

    def test_left_mouse_attack_and_wheel(self):
        self.f.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1),self.drop)
        self.assertGreater(self.f.windup,0)
        self.assertEqual(self.f.velocity.y,0)
        self.f.handle_event(pygame.event.Event(pygame.MOUSEWHEEL,y=1),self.drop)
        self.assertEqual(self.f.inventory.selected,2)

    def test_coyote_window_120ms_and_expiry(self):
        self.f.pos.x=1200
        self.tick()
        self.assertFalse(self.f.grounded)
        self.tick(5)
        self.assertTrue(self.f.jump())
        self.assertFalse(self.f.jump())
        other=Player((1200,550));other.grounded=True
        for _ in range(10): other.update(FIXED_DT,self.floor)
        self.assertFalse(other.jump())

    def test_jump_buffer_just_before_landing(self):
        self.f.grounded=False
        self.f.pos.y=535
        self.f.velocity.y=300
        self.assertFalse(self.f.request_jump())
        self.tick(4)
        self.assertLess(self.f.velocity.y,0)
        self.assertTrue(self.f.jump_consumed)

    def test_expired_buffer_does_not_jump(self):
        self.f.grounded=False
        self.f.pos.y=180
        self.f.request_jump()
        self.tick(80)
        self.assertTrue(self.f.grounded)
        self.assertEqual(self.f.velocity.y,0)

    def test_release_space_shortens_jump(self):
        high=Player((400,550));high.grounded=True;high.jump()
        self.f.jump()
        self.tick(3)
        self.f.handle_event(pygame.event.Event(pygame.KEYUP,key=pygame.K_SPACE),self.drop)
        low_min=high_min=550
        for _ in range(50):
            self.tick();high.update(FIXED_DT,self.floor)
            low_min=min(low_min,self.f.pos.y);high_min=min(high_min,high.pos.y)
        self.assertGreater(low_min-high_min,60)

    def test_acceleration_speed_limit_and_friction(self):
        self.f.axis=1
        self.tick()
        self.assertGreater(self.f.velocity.x,0)
        self.assertLess(self.f.velocity.x,MOVEMENT.speed)
        self.tick(15)
        self.assertEqual(self.f.velocity.x,MOVEMENT.speed)
        self.f.axis=0
        self.tick(7)
        self.assertEqual(self.f.velocity.x,0)

    def test_air_control_lower_and_turnaround_fast(self):
        self.f.axis=1
        self.tick()
        ground_v=self.f.velocity.x
        self.f.velocity.x=0
        self.f.grounded=False
        self.f.pos.y=300
        self.tick()
        self.assertLess(self.f.velocity.x,ground_v)
        self.f.pos.y=550;self.f.grounded=True;self.f.velocity.x=370;self.f.axis=-1
        self.tick(5)
        self.assertLess(self.f.velocity.x,0)

    def test_fall_gravity_greater_than_ascent(self):
        self.f.grounded=False;self.f.pos.y=200;self.f.velocity.y=-100
        self.tick();up_delta=self.f.velocity.y+100
        self.f.velocity.y=100;self.tick();down_delta=self.f.velocity.y-100
        self.assertGreater(down_delta,up_delta)

    def test_solid_wall_and_ceiling(self):
        wall=pygame.Rect(440,100,30,450)
        self.f.axis=1
        for _ in range(20): self.f.update(FIXED_DT,self.floor,[wall])
        self.assertLessEqual(self.f.rect.right,440)
        self.f.pos.update(390,510);self.f.velocity.y=-500;self.f.grounded=False
        ceiling=pygame.Rect(300,280,200,50)
        for _ in range(10): self.f.update(FIXED_DT,self.floor,[ceiling])
        self.assertGreaterEqual(self.f.rect.top,330)

    def test_directional_aim_deadzone_and_vertical_attack(self):
        self.f.set_aim((100,470))
        self.assertEqual(self.f.facing,-1)
        self.f.set_aim((404,440))
        self.assertEqual(self.f.facing,-1)
        self.f.set_aim((400,300))
        self.f.attack();self.tick(3)
        a,b=self.f.attack_segment()
        self.assertLess(b.y,a.y)
        target=Fighter((400,450),(255,0,0))
        self.assertTrue(self.f.resolve_attack(target))
        self.assertFalse(self.f.resolve_attack(target))

    def test_knockback_hitstun_then_control_recovers(self):
        self.f.receive_damage(10,390,pygame.Vector2(-.8,-.6))
        self.assertGreater(self.f.stun,0)
        self.assertFalse(self.f.attack())
        self.assertFalse(self.f.receive_damage(10,390,1))
        self.f.axis=1;self.tick(30)
        self.assertEqual(self.f.stun,0)
        self.assertGreater(self.f.velocity.x,0)
        self.assertEqual(self.f.health,90)

    def test_hit_cancels_attack_but_inventory_does_not(self):
        self.f.inventory.collect(PAN);self.f.attack()
        self.f.inventory.cycle(1)
        self.assertEqual(self.f.attack_weapon,PAN)
        self.f.receive_damage(7,255,-1)
        self.assertEqual(self.f.attack_time,0)
        self.assertEqual(self.f.windup,0)


class ExperienceTests(unittest.TestCase):
    def setUp(self):
        self.game=Game("ringue",audio_enabled=False)
        self.m=self.game.scene

    def tearDown(self):
        self.game.audio.stop()
        pygame.quit()

    def test_intro_blocks_inputs_and_can_skip_only_after_seen(self):
        self.m.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_SPACE))
        self.m.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=(800,450)))
        self.assertEqual(self.m.player.velocity.y,0)
        self.assertEqual(self.m.player.attack_time,0)
        self.assertFalse(self.m.flow.skip())
        for _ in range(245): self.m.simulate(FIXED_DT)
        self.assertEqual(self.m.flow.phase,"fight")
        self.assertTrue(self.game.intro_seen)
        self.game.start_match()
        self.assertTrue(self.game.scene.flow.skip())

    def test_pause_controls_options_and_volumes(self):
        self.m.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE))
        self.assertIsInstance(self.game.scene,Pausa)
        pause=self.game.scene
        pause.selected=2;pause.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RETURN))
        self.assertIsInstance(self.game.scene,Controls)
        self.game.scene.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE))
        pause.selected=3;pause.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RETURN))
        options=self.game.scene
        self.assertIsInstance(options,Options)
        for _ in range(20): options.adjust(-1)
        self.assertEqual(self.game.settings.master,0)
        options.selected=4
        for _ in range(10): options.adjust(-1)
        self.assertEqual(self.game.settings.shake,0)

    def test_resize_mouse_inverse_mapping(self):
        self.game.process_event(pygame.event.Event(pygame.VIDEORESIZE,w=1000,h=800))
        v=self.game.viewport
        center=(v.offset[0]+v.size[0]/2,v.offset[1]+v.size[1]/2)
        self.assertEqual(v.to_logical(center),pygame.Vector2(640,360))
        self.m.camera.update(.2,self.m.fighters)
        p=pygame.Vector2(390,470)
        self.assertLess(p.distance_to(self.m.camera.to_world(self.m.camera.to_screen(p))),.001)
        self.game.scene.draw(self.game.screen)
        v.present(self.game.screen,self.game.window)

    def test_debug_defaults_off_and_toggles(self):
        self.assertFalse(self.game.debug)
        self.game.process_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_F3))
        self.assertTrue(self.game.debug)
        self.m.draw(self.game.screen)

    def test_camera_shake_off_and_bounds(self):
        c=self.m.camera
        self.game.settings.shake=0
        c.impulse(10)
        for _ in range(40):
            c.update(FIXED_DT,self.m.fighters,self.m.drop)
            self.assertTrue(pygame.Rect(0,0,1280,720).contains(c.view))

    def test_pan_never_spawns_inside_body_at_top(self):
        d=self.m.drop;d.state="warning";d.timer=0;d.x=640
        self.m.player.pos.update(640,20)
        d.update(FIXED_DT,self.m.fighters,self.m.platforms)
        self.assertEqual(d.state,"warning")
        self.m.player.pos.update(390,550)
        d.update(.11,self.m.fighters,self.m.platforms)
        self.assertEqual(d.state,"opening")
        d.update(.13,self.m.fighters,self.m.platforms)
        self.assertEqual(d.state,"falling")

    def test_cpu_reaction_does_not_attack_outside_reach(self):
        e,p=self.m.enemy,self.m.player
        p.pos.x=390;e.pos.x=900
        for _ in range(60): e.decide(FIXED_DT,p,self.m.drop,self.m.platforms)
        self.assertEqual(e.attack_time,0)
        e.pos.x=440;e.brain.timer=.18
        e.decide(.05,p,self.m.drop,self.m.platforms)
        self.assertEqual(e.attack_time,0)
        self.assertGreater(e.brain.timer,0)

    def test_restart_resets_inventory_health_and_flow(self):
        self.m.player.inventory.collect(PAN);self.m.player.health=0;self.m.check_result()
        self.m.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_r))
        self.assertEqual(self.game.scene.player.health,100)
        self.assertTrue(all(x is None for x in self.game.scene.player.inventory.slots))
        self.assertEqual(self.game.scene.flow.phase,"intro")

    def test_poses_differ_for_run_jump_fall_brake_and_damage(self):
        from scripts.entities.poses import pose
        f=self.m.player
        signatures=[]
        for state,velocity in (("parado",(0,0)),("correndo",(300,0)),("pulando",(200,-500)),("caindo",(200,500)),("freando",(300,0)),("dano",(-300,-100))):
            f.movement_state=state;f.velocity.update(velocity);f.animation_time=.1
            signatures.append(tuple((round(v.x,2),round(v.y,2)) for v in pose(f).values()))
        self.assertEqual(len(set(signatures)),6)


class AudioTests(unittest.TestCase):
    def tearDown(self):
        pygame.mixer.quit()

    def test_missing_device_fails_safely(self):
        pygame.mixer.quit()
        with patch("pygame.mixer.init",side_effect=pygame.error("no device")):
            audio=AudioManager(Settings())
        self.assertFalse(audio.enabled)
        audio.play("hit");audio.set_music("ringue");audio.update(.1)

    def test_volume_clamp_mute_and_music_not_restarted(self):
        s=Settings();s.set_volume("master",8);s.set_volume("effects",-1)
        self.assertEqual(s.master,1);self.assertEqual(s.effects,0)
        a=AudioManager(s)
        self.assertTrue(a.enabled)
        a.set_music("ringue");starts=a.music_starts
        a.set_music("ringue",True);a.update(.5)
        self.assertEqual(a.music_starts,starts)
        self.assertGreater(a.music_levels["critical"],0)
        s.mute=True;a.update(.1)
        self.assertEqual(pygame.mixer.Channel(1).get_volume(),0)

    def test_missing_file_uses_generated_sound(self):
        a=AudioManager(Settings())
        with patch("pathlib.Path.exists",return_value=False):
            self.assertIsNotNone(a.load("warning"))

    def test_no_audio_game_headless(self):
        g=Game(audio_enabled=False)
        self.assertFalse(g.audio.enabled)
        g.run(3)

    def test_original_music_loops_have_matching_duration_and_safe_seam(self):
        import wave
        from array import array
        from scripts.audio.synth import MUSIC,path_for,RATE
        sizes=[]
        for name in MUSIC:
            with wave.open(str(path_for(name)),"rb") as wav:
                self.assertEqual(wav.getframerate(),RATE)
                self.assertEqual(wav.getnchannels(),2)
                self.assertEqual(wav.getsampwidth(),2)
                sizes.append(wav.getnframes())
                samples=array('h',wav.readframes(wav.getnframes()))
                self.assertLess(max(abs(v) for v in samples),32767)
                self.assertLess(abs(samples[-2]-samples[0]),500)
        self.assertEqual(sizes,[RATE*8]*3)


if __name__=="__main__": unittest.main()
