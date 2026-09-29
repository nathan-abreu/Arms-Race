import os
os.environ['SDL_VIDEODRIVER']='dummy'
os.environ['SDL_AUDIODRIVER']='dummy'
import math
import unittest
from array import array
from unittest.mock import patch
import pygame
from scripts.game import Game
from scripts.config import FIXED_DT
from scripts.balance import DELIVERY,COMBAT
from scripts.combat.weapon import PAN,FISTS
from scripts.entities.fighter import Fighter
from scripts.entities.separation import separate_fighters
from scripts.effects.pan_art import pan,pan_surface,PAN_PIVOT
from scripts.ui.weapon_icons import weapon_icon
from scripts.ui.inventory_view import SLOT_X,SLOT_Y,SLOT_W,SLOT_H,GAP
from scripts.audio.manager import AudioManager,GROUPS
from scripts.audio.layers import CUES,pcm_cue,Layer
from scripts.settings import Settings


class PremiumVisualTests(unittest.TestCase):
    def setUp(self):
        self.game=Game('ringue',audio_enabled=False)
        self.m=self.game.scene;self.m.flow.phase='fight'

    def tearDown(self):
        self.game.audio.stop();pygame.quit()

    def test_connected_silhouette_in_all_poses_and_both_directions(self):
        f=self.m.player;f.visual_quality=0
        for direction in (-1,1):
            for state,velocity in (('parado',(0,0)),('correndo',(380,0)),('freando',(-300,0)),
                                   ('pulando',(200,-500)),('caindo',(-120,500)),('pousando',(0,0)),('dano',(250,-100))):
                with self.subTest(state=state,direction=direction):
                    f.movement_state=state;f.velocity.update(velocity);f.facing=direction
                    f.aim.update(direction,0);f.aim_locked=True;f.art=None
                    f.landing_time=.08 if state=='pousando' else 0
                    f.animate(1);f.draw(self.game.screen)
                    mask=pygame.mask.from_surface(f.art.sprite)
                    self.assertEqual(len(mask.connected_components(10)),1)
                    self.assertTrue(pygame.Rect(1,1,298,268).contains(mask.get_bounding_rects()[0]))
        for dead,celebrating in ((False,True),(True,False)):
            f.health=0 if dead else 100;f.celebrating=celebrating
            f.art=None;f.animate(1);f.draw(self.game.screen)
            self.assertEqual(len(pygame.mask.from_surface(f.art.sprite).connected_components(10)),1)

    def test_pose_transitions_and_front_parts_cover_back_parts(self):
        f=self.m.player;f.visual_quality=0
        for angle in (-85,-40,0,40,85,160):
            f.set_aim(f.shoulder+pygame.Vector2(150,0).rotate(angle))
            for _ in range(5):
                f.animate(FIXED_DT);f.draw(self.game.screen)
                self.assertEqual(len(pygame.mask.from_surface(f.art.sprite).connected_components(10)),1)
            hip=f.art.points['hip']+pygame.Vector2(150,218)
            self.assertEqual(f.art.sprite.get_at((round(hip.x),round(hip.y)))[:3],f.color)
        self.assertLess(f.art.draw_order.index('back_limbs'),f.art.draw_order.index('torso'))
        self.assertLess(f.art.draw_order.index('head'),f.art.draw_order.index('weapon'))

    def test_both_punches_and_finisher_remain_connected_through_animation(self):
        f=self.m.player;f.visual_quality=0
        for angle in (-70,0,70,180):
            for combo in (1,2,3):
                f.cooldown=f.recovery=f.stun=0
                f.combo_left=1;f.combo_index=combo-1
                f.set_aim(f.shoulder+pygame.Vector2(200,0).rotate(angle))
                f.attack()
                for _ in range(22):
                    f.update(FIXED_DT,self.m.platforms);f.draw(self.game.screen)
                    with self.subTest(angle=angle,combo=combo,phase=f.attack_phase):
                        self.assertEqual(len(pygame.mask.from_surface(f.art.sprite).connected_components(10)),1)

    def test_main_capsules_separate_and_allow_jump_over(self):
        a,b=self.m.fighters
        a.pos.x=b.pos.x=640
        for _ in range(10): separate_fighters(a,b,FIXED_DT)
        self.assertAlmostEqual(b.pos.x-a.pos.x,COMBAT.body_spacing,places=3)
        a.pos.update(640,375);b.pos.update(640,514)
        separate_fighters(a,b,FIXED_DT)
        self.assertEqual(a.pos.x,b.pos.x)
        b.set_aim(a.shoulder+(80,0));self.assertEqual(b.facing,1)

    def test_contact_precedes_effects_and_miss_has_no_burst(self):
        a,b=self.m.fighters
        a.set_aim(b.shoulder);a.attack()
        self.assertFalse(a.resolve_attack(b))
        self.assertFalse(self.m.particles.items)
        a.pos.x=560;b.pos.x=644;b.set_aim(a.shoulder)
        a.set_aim(b.shoulder)
        for f in (a,b): f.animate(1)
        for _ in range(6):
            a.update(FIXED_DT,self.m.platforms)
            if a.resolve_attack(b):
                _,hand=a.attack_segment()
                self.assertLess(a.attack_contact.distance_to(hand),23)
                self.m.feedback.hit(self.m,a,b)
                break
        self.assertLess(b.health,100)
        self.assertTrue(self.m.particles.items)
        before=b.health;b.invulnerable=0
        self.assertFalse(a.resolve_attack(b));self.assertEqual(before,b.health)

    def test_pan_pivot_does_not_orbit_when_rotating(self):
        self.assertEqual(pan_surface().get_rect().center,PAN_PIVOT)
        target=(300,250)
        for angle in range(0,360,15):
            self.game.screen.fill((80,80,80))
            rect=pan(self.game.screen,target,angle)
            self.assertEqual(rect.center,target)
            self.assertLess(sum(self.game.screen.get_at(target)[:3]),180)

    def test_icons_unique_and_inventory_geometry_within_window(self):
        pictures=[pygame.image.tobytes(weapon_icon(name),'RGBA') for name in ('panela','machado','rifle','lancador')]
        self.assertEqual(len(set(pictures)),4)
        self.assertEqual(SLOT_X+3*SLOT_W+2*GAP,1280-25)
        self.assertEqual(SLOT_Y+SLOT_H+6+20,720-18)

    def test_f4_is_off_and_does_not_inject_fake_weapons_into_match(self):
        inv=self.m.player.inventory
        self.assertIsNone(inv.preview)
        inv.collect(PAN);before=inv.slots.copy()
        self.m.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_F4))
        self.assertEqual(len([w for w in inv.display_slots if w]),3)
        self.assertEqual(inv.slots,before)
        self.assertIs(inv.weapon,PAN)
        self.m.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_F4))
        self.assertIsNone(inv.preview);self.assertEqual(inv.slots,before)

    def test_q_e_wheel_and_discard_have_inventory_animation(self):
        p=self.m.player;inv=p.inventory
        inv.collect(PAN);self.m.hud.update(.01,self.m.fighters)
        self.assertGreater(self.m.hud.inventory_view.name_time,0)
        for event,expected in ((pygame.event.Event(pygame.KEYDOWN,key=pygame.K_e),1),
                               (pygame.event.Event(pygame.KEYDOWN,key=pygame.K_q),0),
                               (pygame.event.Event(pygame.MOUSEWHEEL,y=1),2)):
            p.handle_event(event,self.m.drop);self.assertEqual(inv.selected,expected)
            self.m.hud.update(.01,self.m.fighters)
            self.assertGreater(self.m.hud.inventory_view.pulses[expected],0)
        inv.cycle(1)
        point=p.weapon_center
        p.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_x),self.m.drop)
        self.m.hud.update(.01,self.m.fighters)
        self.assertNotIn(PAN,inv.slots)
        self.assertTrue(self.m.hud.inventory_view.flights)
        self.assertLess(pygame.Vector2(self.m.drop.x,self.m.drop.y).distance_to(point),.001)

    def test_full_delivery_warning_open_fall_impact_collect(self):
        d=self.m.drop;d.timer=0
        d.update(FIXED_DT,self.m.fighters,self.m.platforms)
        self.assertEqual(d.state,'warning');self.assertEqual(d.timer,.9)
        for _ in range(53): d.update(FIXED_DT,self.m.fighters,self.m.platforms)
        self.assertEqual(d.state,'warning')
        for _ in range(2): d.update(FIXED_DT,self.m.fighters,self.m.platforms)
        self.assertEqual(d.state,'opening')
        while d.state=='opening': d.update(FIXED_DT,self.m.fighters,self.m.platforms)
        fall=0
        while d.state=='falling':
            d.update(FIXED_DT,self.m.fighters,self.m.platforms);fall+=FIXED_DT
        self.assertTrue(.6<=fall<=.8)
        self.assertEqual(d.state,'available');self.assertGreater(d.beam_fade,0)
        self.assertIsNotNone(d.impact_event)
        d.update(.13,self.m.fighters,self.m.platforms)
        self.assertEqual(d.beam_fade,0)
        self.m.player.pos.x=d.x
        self.assertTrue(d.try_collect(self.m.player))
        self.assertEqual(d.state,'held');self.assertIsNotNone(d.collection)
        self.assertGreater(self.m.player.pickup_time,0)
        d.update(DELIVERY.pickup_flight,self.m.fighters,self.m.platforms)
        self.assertIsNone(d.collection);self.assertEqual(self.m.player.pickup_time,0)

    def test_beam_is_a_gradient_not_an_opaque_rectangle(self):
        beam=self.m.drop.art.beams[0];y=100
        center=beam.get_at((66,y));column=beam.get_at((82,y));edge=beam.get_at((0,y))
        self.assertGreater(center.a,column.a);self.assertGreater(column.a,edge.a)
        self.assertLess(center.a,255);self.assertLess(edge.a,10)
        self.assertGreater(center.b,column.b)

    def test_pan_hitstop_flash_and_camera_magnitude(self):
        a,b=self.m.fighters
        a.pos.x=560;b.pos.x=644
        a.inventory.collect(PAN);a.set_aim(b.shoulder);b.set_aim(a.shoulder)
        for f in (a,b): f.animate(1)
        a.attack();a.update(.105,self.m.platforms)
        self.assertTrue(a.resolve_attack(b));self.m.feedback.hit(self.m,a,b)
        self.assertEqual(self.m.hit_stop,.080)
        self.assertEqual(b.flash_time,.050)
        self.assertEqual(self.m.camera.shake_pixels,8)
        before=a.pos.copy();self.m.simulate(.03)
        self.assertEqual(a.pos,before)
        self.assertLess(b.flash_time,.050)


class PremiumAudioTests(unittest.TestCase):
    def tearDown(self): pygame.mixer.quit()

    def test_composed_impacts_have_layers_and_safe_peaks(self):
        for name in ('hit','heavy_hit','metal_impact','drop_impact'):
            self.assertGreaterEqual(len(CUES[name].layers),4)
            samples=array('h',pcm_cue(name))
            self.assertLessEqual(max(abs(v) for v in samples),round(.73*32767))
            self.assertLess(abs(samples[-1]),400)
        self.assertNotEqual(pcm_cue('metal_impact'),pcm_cue('drop_impact'))

    def test_separate_groups_and_voice_repeat_limit(self):
        audio=AudioManager(Settings())
        for _ in range(10):
            audio.time+=.1;audio.play('metal_impact')
            audio.play('crowd');audio.play('step_l');audio.play('select')
        self.assertEqual(pygame.mixer.get_num_channels(),17)
        self.assertLessEqual(sum(e[0]=='metal_impact' for e in audio.active.values()),2)
        self.assertLessEqual(len(audio.active),14)
        for index,(name,_,_) in audio.active.items():
            self.assertIn(index,GROUPS[CUES[name].group])

    def test_stereo_pan_center_and_sides(self):
        l,r=AudioManager.stereo_pan(0);self.assertGreater(l,r)
        l,r=AudioManager.stereo_pan(1280);self.assertGreater(r,l)
        l,r=AudioManager.stereo_pan(640);self.assertAlmostEqual(l,r)
        self.assertAlmostEqual(l*l+r*r,1)

    def test_music_layers_share_headroom_during_crossfade(self):
        audio=AudioManager(Settings(master=1,music=1))
        audio.music_levels={name:1.0 for name in audio.music_levels}
        audio.music_name='ringue';audio.intense=True
        audio.update(.01)
        self.assertLessEqual(sum(pygame.mixer.Channel(i).get_volume() for i in range(3)),.301)

    def test_duck_four_db_and_restoration_without_audio(self):
        audio=AudioManager(Settings(),enabled=False)
        audio.duck(.15);audio.update(.05)
        self.assertAlmostEqual(audio.duck_gain,10**(-4/20))
        for _ in range(50): audio.update(FIXED_DT)
        self.assertEqual(audio.duck_gain,1)

    def test_missing_device_and_runtime_layer_registration(self):
        pygame.mixer.quit()
        with patch('pygame.mixer.init',side_effect=pygame.error('sem dispositivo')):
            audio=AudioManager(Settings())
        self.assertFalse(audio.enabled)
        audio.register_layers('test_custom',(Layer('noise',.04,.5,1000),Layer('sub',.08,.3,60)))
        audio.play('test_custom',x=40);audio.update(.1)
        CUES.pop('test_custom')


if __name__=='__main__': unittest.main()
