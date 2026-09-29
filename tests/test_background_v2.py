import os
os.environ['SDL_VIDEODRIVER']='dummy'
os.environ['SDL_AUDIODRIVER']='dummy'
import unittest
from pathlib import Path
from unittest.mock import patch
import pygame
from scripts.game import Game
from scripts.config import FIXED_DT
from scripts.arena_layout import GROUND_Y,LEFT_EDGE,RIGHT_EDGE
from scripts.balance import MOVEMENT,COMBAT
from scripts.effects.image_arena import ImageArena,load_background
from scripts.entities.fighter import Fighter
from scripts.entities.separation import separate_fighters
from scripts.entities.poses import pose
from scripts.audio.manager import AudioManager
from scripts.settings import Settings
from scripts.combat.weapon import PAN


class ComboTests(unittest.TestCase):
    def setUp(self):
        self.a=Fighter((400,514),(5,235,255))
        self.b=Fighter((465,514),(255,24,79))
        self.floor=[pygame.Rect(134,514,1012,24)]
        self.a.grounded=self.b.grounded=True

    def wait_ready(self):
        for _ in range(25):
            self.a.update(FIXED_DT,self.floor)
            if self.a.cooldown==0 and self.a.recovery==0: return
        self.fail('Ataque não terminou no prazo')

    def test_three_clicks_damage_cooldown_and_alternating_arm(self):
        for i,damage,duration in ((1,7,.230),(2,8,.250),(3,13,.340)):
            self.assertTrue(self.a.attack())
            self.assertEqual(self.a.combo_index,i)
            self.assertEqual(self.a.punch_arm,int(i==2))
            self.assertEqual(self.a.attack_total,duration)
            self.assertFalse(self.a.resolve_attack(self.b))
            self.a.update(.08,self.floor)
            self.assertTrue(self.a.resolve_attack(self.b))
            self.assertEqual(self.b.health,100-damage)
            self.b.invulnerable=0
            self.assertFalse(self.a.resolve_attack(self.b))
            self.wait_ready()
            self.b.health=100
        self.assertTrue(self.a.strong_attack)
        self.assertEqual(COMBAT.strong_stop,.065)
        self.assertEqual(COMBAT.light_stop,.040)

    def test_combo_expires_and_never_continues_without_click(self):
        self.a.attack();self.wait_ready()
        for _ in range(30): self.a.update(FIXED_DT,self.floor)
        self.assertEqual(self.a.attack_time,0)
        self.assertEqual(self.a.combo_left,0)
        self.a.attack()
        self.assertEqual(self.a.combo_index,1)

    def test_late_click_is_buffered_once(self):
        self.a.attack()
        for _ in range(10): self.a.update(FIXED_DT,self.floor)
        self.assertFalse(self.a.attack())
        self.assertGreater(self.a.queued_click,0)
        for _ in range(7): self.a.update(FIXED_DT,self.floor)
        self.assertEqual(self.a.combo_index,2)
        self.assertEqual(self.a.queued_click,0)
        for _ in range(30): self.a.update(FIXED_DT,self.floor)
        self.assertEqual(self.a.combo_index,2)
        self.assertEqual(self.a.attack_time,0)

    def test_damage_cancels_queued_combo(self):
        self.a.attack()
        for _ in range(10): self.a.update(FIXED_DT,self.floor)
        self.a.attack();self.a.receive_damage(7,255,-1)
        self.assertEqual(self.a.queued_click,0)
        self.assertEqual(self.a.combo_left,0)

    def test_pan_keeps_separate_profile_and_hand_matches_hitbox(self):
        self.a.inventory.collect(PAN);self.a.set_aim((700,380));self.a.attack()
        self.a.update(.06,self.floor)
        self.assertEqual(self.a.combo_index,0)
        self.assertTrue(self.a.strong_attack)
        _,end=self.a.attack_segment()
        visible=self.a.pos+self.a.art.points['hand']+self.a.swing_vector()*22
        self.assertLess(visible.distance_to(end),.001)

    def test_second_punch_collision_tracks_back_hand(self):
        self.a.attack();self.wait_ready();self.a.attack();self.a.update(.05,self.floor)
        _,end=self.a.attack_segment()
        self.assertLess((self.a.pos+self.a.art.points['back_hand']).distance_to(end),.001)

    def test_smooth_separation_resolves_same_center_and_allows_jump_over(self):
        self.b.pos.x=self.a.pos.x
        for _ in range(4): separate_fighters(self.a,self.b,FIXED_DT)
        self.assertGreater(self.b.pos.x-self.a.pos.x,self.a.WIDTH)
        self.a.pos.update(400,380);self.b.pos.update(400,514)
        separate_fighters(self.a,self.b,FIXED_DT)
        self.assertEqual(self.a.pos.x,self.b.pos.x)

    def test_grounded_soles_and_distance_driven_stance(self):
        self.a.movement_state='parado'
        p=pose(self.a)
        self.assertEqual(p['foot_l'].y+4,0)
        self.a.movement_state='correndo';self.a.velocity.x=380
        self.a.stride_distance=10
        first=self.a.pos+pose(self.a)['foot_l']
        self.a.pos.x+=10;self.a.stride_distance+=10
        second=self.a.pos+pose(self.a)['foot_l']
        self.assertEqual(first,second)

    def test_requested_movement_parameters(self):
        self.assertEqual(MOVEMENT.speed,380)
        self.assertEqual(MOVEMENT.acceleration,2800)
        self.assertEqual(MOVEMENT.friction,3400)
        self.assertEqual(MOVEMENT.jump_speed,720)
        self.assertEqual(MOVEMENT.gravity,1900)
        self.assertAlmostEqual(MOVEMENT.gravity*MOVEMENT.fall_multiplier,2700)
        self.assertEqual(MOVEMENT.air_acceleration/MOVEMENT.acceleration,.65)

    def test_downward_guard_keeps_hand_beside_torso(self):
        self.a.set_aim((400,650))
        p=pose(self.a)
        self.assertGreater(p['hand'].x-p['hip'].x,20)
        self.a.attack();self.a.update(.06,self.floor)
        _,end=self.a.attack_segment()
        self.assertLess((self.a.pos+self.a.art.points['hand']).distance_to(end),.001)


class BackgroundTests(unittest.TestCase):
    def setUp(self):
        self.game=Game('ringue',audio_enabled=False)
        self.m=self.game.scene

    def tearDown(self):
        self.game.audio.stop();pygame.quit()

    def test_only_image_arena_and_one_visible_floor(self):
        self.assertIsInstance(self.m.art,ImageArena)
        self.assertTrue(self.m.art.image_found)
        self.assertEqual(len(self.m.platforms),1)
        floor=self.m.platforms[0]
        self.assertEqual(floor.top,round(720*GROUND_Y))
        self.assertEqual(floor.left,round(1280*LEFT_EDGE))
        self.assertEqual(floor.right,round(1280*RIGHT_EDGE))
        self.assertEqual(self.m.player.pos.y,floor.top)
        self.assertTrue(150<=self.m.player.HEIGHT<=175)

    def test_decoding_once_and_reuse_across_restarts(self):
        load_background.cache_clear()
        with patch('pygame.image.load',wraps=pygame.image.load) as read:
            a=ImageArena();b=ImageArena()
        self.assertEqual(read.call_count,1)
        self.assertIs(a.base,b.base)
        art=self.m.art
        self.game.start_match()
        self.assertIs(self.game.scene.art,art)

    def test_missing_image_has_safe_neutral_fallback(self):
        base,found=load_background(Path('assets/imagens/arquivo_inexistente.png'))
        self.assertFalse(found)
        self.assertEqual(base.get_size(),(1280,720))

    def test_overlay_moves_and_reacts_without_changing_base(self):
        a=self.m.art
        checksum=pygame.image.tobytes(a.base,'RGB')
        a.draw(self.game.screen)
        first=pygame.image.tobytes(self.game.screen,'RGB')
        a.update(.75);a.react(1,side=0);a.draw(self.game.screen)
        self.assertNotEqual(first,pygame.image.tobytes(self.game.screen,'RGB'))
        self.assertEqual(checksum,pygame.image.tobytes(a.base,'RGB'))
        self.assertGreater(a.damage[0],0)

    def test_corners_preserved_and_camera_crop_always_inside(self):
        base=self.m.art.base
        from scripts.arena_layout import BACKGROUND_PATH
        raw=pygame.image.load(str(BACKGROUND_PATH))
        self.assertLess(abs(raw.get_width()/raw.get_height()-16/9),.004)
        expected=pygame.transform.smoothscale(raw,(1280,720))
        for point in ((0,0),(1279,0),(0,719),(1279,719)):
            self.assertEqual(base.get_at(point),expected.get_at(point))
        for _ in range(30):
            self.m.camera.impulse(1,(1,-.2));self.m.camera.update(FIXED_DT,self.m.fighters)
            self.assertTrue(base.get_rect().contains(self.m.camera.view))

    def test_quality_levels_resize_fullscreen_and_debug(self):
        for quality in range(3):
            self.game.settings.particles=quality
            self.m.simulate(FIXED_DT);self.m.draw(self.game.screen)
            self.assertEqual(self.m.art.quality,quality)
            self.assertEqual(self.m.player.visual_quality,quality)
        for size in ((960,540),(1000,800),(1600,900)):
            self.game.settings.resolution=size;self.game.apply_display()
            self.game.viewport.present(self.game.screen,self.game.window)
            self.assertAlmostEqual(self.game.viewport.size[0]/self.game.viewport.size[1],16/9,places=2)
        self.game.settings.fullscreen=True;self.game.apply_display()
        self.game.viewport.present(self.game.screen,self.game.window)
        self.game.settings.fullscreen=False;self.game.apply_display()
        self.game.debug=True;self.m.draw(self.game.screen)

    def test_duck_envelope_safe_without_audio(self):
        a=AudioManager(Settings(),enabled=False)
        a.duck(.2);a.update(.05)
        self.assertLess(a.duck_gain,1)
        for _ in range(60): a.update(FIXED_DT)
        self.assertEqual(a.duck_gain,1)
        a.end_match();self.assertIsNone(a.music_name)

    def test_screen_glow_masks_do_not_paint_rectangle_corners(self):
        for _,patch in self.m.art.screens:
            self.assertEqual(patch.get_at((0,0)).a,0)
            self.assertEqual(patch.get_at((patch.get_width()-1,0)).a,0)
            self.assertGreater(patch.get_at((patch.get_width()//2,patch.get_height()//2)).a,0)


if __name__=='__main__': unittest.main()
