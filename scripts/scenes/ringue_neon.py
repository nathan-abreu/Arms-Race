import random
import pygame
from scripts.config import WIDTH, HEIGHT, CYAN, PINK, GOLD, WHITE, MUTED
from scripts.data import load_level
from scripts.scenes.base import Scene
from scripts.entities.player import Player
from scripts.entities.enemy import Enemy
from scripts.combat.weapon import WeaponDrop
from scripts.effects.image_arena import ImageArena
from scripts.entities.separation import separate_fighters
from scripts.effects.impact import ImpactEffects
from scripts.effects.neon import CYAN as RING_CYAN, PINK as RING_PINK
from scripts.effects.particles import Particles
from scripts.effects.camera import Camera
from scripts.effects.feedback import Feedback
from scripts.audio.manager import AudioManager
from scripts.settings import Settings
from scripts.match_flow import MatchFlow
from scripts.ui.debug import DebugOverlay
from scripts.ui.hud import HUD
from scripts.ui.style import panel, text, shade


class RingueNeon(Scene):
    def __init__(self, game, seed=None):
        super().__init__(game)
        self.level = load_level()
        self.settings=game.settings if game else Settings()
        self.audio=game.audio if game else AudioManager(self.settings,False)
        self.flow=MatchFlow(enabled=game is not None,can_skip=bool(game and game.intro_seen))
        self.platforms = [pygame.Rect(p) for p in self.level["platforms"]]
        self.player = Player(self.level["player_spawn"])
        self.enemy = Enemy(self.level["enemy_spawn"])
        self.fighters = (self.player, self.enemy)
        for f in self.fighters:
            f.pos.y=self.platforms[0].top
            f.grounded=True
        self.player.color, self.enemy.color = RING_CYAN, RING_PINK
        self.rng = random.Random(seed)
        self.drop = WeaponDrop(self.level, self.rng)
        self.particles = Particles()
        if game and game.arena_art:
            self.art=game.arena_art
        else:
            self.art = ImageArena()
            if game: game.arena_art=self.art
        self.art.reaction=0
        self.art.damage=[0.0,0.0]
        self.art.rope_pulse=0
        self.art.configure(self.fighters,self.drop,self.settings)
        self.impacts = ImpactEffects()
        self.camera=Camera(self.settings)
        self.feedback=Feedback(self.audio)
        self.debug_overlay=DebugOverlay()
        self.foot_timer = 0.0
        self.hud = HUD()
        self.world = pygame.Surface((WIDTH, HEIGHT))
        self.time = self.shake = self.hit_stop = 0.0
        self.shake_offset = (0, 0)
        self.result = None
        self.result_reason = ""
        self.result_frame = None
        self.transition=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)

    def handle_event(self, event):
        key=event.key if event.type==pygame.KEYDOWN else None
        if key==pygame.K_F4:
            self.player.inventory.toggle_preview()
            self.audio.play('slot_switch',variation=False)
            return
        if self.result:
            if key == pygame.K_r:
                self.game.start_match()
            elif key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_ESCAPE):
                self.game.show_menu()
            return
        if key == pygame.K_ESCAPE:
            from scripts.scenes.pausa import Pausa
            self.audio.play("pause",variation=False)
            self.player.release_jump()
            self.game.change_scene(Pausa(self.game, self))
            return
        if self.flow.phase!="fight":
            if key==pygame.K_RETURN: self.flow.skip()
            return
        if event.type in (pygame.MOUSEMOTION,pygame.MOUSEBUTTONDOWN) and hasattr(event,"pos"):
            point=self.game.viewport.to_logical(event.pos) if self.game else event.pos
            self.player.set_aim(self.camera.to_world(point))
        self.player.handle_event(event, self.drop)

    def _ropes(self, fighter, previous_x):
        base = self.platforms[0]
        # Cordas só devolvem quem cruza na altura do ringue. Saltos altos
        # podem passar por cima e causar eliminação ao cair fora da arena.
        if fighter.rope_cooldown > 0 or not base.top - self.level["rope_height"] < fighter.pos.y <= base.top + 8:
            return
        left, right = base.left + 12, base.right - 12
        direction = 1 if previous_x >= left > fighter.pos.x else -1 if previous_x <= right < fighter.pos.x else 0
        if direction:
            fighter.pos.x = left if direction == 1 else right
            fighter.velocity.x = direction * self.level["rope_impulse"]
            fighter.velocity.y = -145
            fighter.stun = .18
            fighter.rope_cooldown = .35
            self.art.react(.4)
            self.particles.burst((fighter.pos.x, fighter.pos.y - 30), CYAN, 9)

    def check_result(self):
        if self.result:
            return
        # Empate por eliminação simultânea conta como derrota do jogador.
        if not self.player.alive:
            self.result = "DERROTA"
            self.result_reason = "Você caiu da arena." if self.player.health > 0 else "Sua vida chegou a zero."
        elif not self.enemy.alive:
            self.result = "VITÓRIA"
            self.result_reason = "O oponente caiu da arena." if self.enemy.health > 0 else "O oponente foi derrotado."
        if self.result:
            self.shake_offset = (0, 0)
            self.flow.finish()
            self.feedback.result(self)

    def update(self, dt):
        if self.game and self.flow.phase=="fight" and not self.result:
            self.player.set_aim(self.camera.to_world(self.game.viewport.to_logical(pygame.mouse.get_pos())))
        self.simulate(dt, pygame.key.get_pressed())

    def simulate(self, dt, keys=None):
        """Passo fixo também utilizado por testes, sem entrada real obrigatória."""
        self.particles.limit=self.settings.particle_limit
        self.art.configure(self.fighters,self.drop,self.settings)
        for f in self.fighters:
            f.visual_quality=self.settings.particles
            f.visual_ground=self.platforms[0].top
        self.flow.update(dt,self.audio)
        self.art.update(dt)
        if self.flow.phase in ("intro","countdown"):
            self.camera.update(dt,self.fighters,intro=True)
            for f in self.fighters:
                f.animation_time+=dt
                f.animate(dt)
            return
        if self.game: self.game.intro_seen=True
        if self.result:
            self.camera.update(dt,self.fighters)
            if self.flow.phase=="finish" and self.flow.result_age>=.055:
                loser=self.enemy if self.result=="VITÓRIA" else self.player
                loser.axis=0
                progress=min(1,(self.flow.result_age-.055)/.4)
                loser.update(dt*(.18+.82*progress**3),self.platforms)
            for f in self.fighters:
                f.animation_time+=dt
                f.animate(dt)
            self.particles.update(dt)
            self.impacts.update(dt,self.fighters,self.platforms[0])
            self.hud.update(dt,self.fighters)
            return
        self.check_result()
        if self.result:
            return
        if self.hit_stop > 0:
            self.hit_stop = max(0, self.hit_stop - dt)
            for f in self.fighters: f.flash_time=max(0,f.flash_time-dt)
            self.camera.update(dt,self.fighters,self.drop)
            self.particles.update(dt)
            self.impacts.update(dt,self.fighters,self.platforms[0])
            self.hud.update(dt,self.fighters)
            return
        self.time += dt
        self.audio.set_music("ringue",intense=min(f.health for f in self.fighters)<=28 or self.time>45)
        if keys is not None:
            self.player.read_input(keys)
        self.enemy.decide(dt, self.player, self.drop, self.platforms)
        for fighter in self.fighters:
            previous_x = fighter.pos.x
            fighter.update(dt, self.platforms)
            self._ropes(fighter, previous_x)
        separate_fighters(self.player,self.enemy,dt)
        for attacker, target in ((self.player, self.enemy), (self.enemy, self.player)):
            if attacker.resolve_attack(target):
                self.feedback.hit(self,attacker,target)
        previous_drop=self.drop.state
        self.drop.update(dt, self.fighters, self.platforms)
        if self.drop.state=="warning" and previous_drop!="warning": self.audio.play("warning",variation=False,x=self.drop.x)
        if self.drop.state=='opening' and previous_drop!='opening': self.audio.play('beam',x=self.drop.x)
        if self.drop.state in ('warning','opening'): self.art.react(.12)
        if self.drop.impact_event:
            self.feedback.drop_impact(self)
        for target in self.drop.damage_events:
            self.particles.burst(target.rect.center,GOLD,12)
        # O mais próximo tem prioridade quando ambos disputam no mesmo quadro.
        for fighter in sorted(self.fighters, key=lambda f: abs(f.pos.x - self.drop.x)):
            if self.drop.try_collect(fighter):
                self.feedback.collect(self,fighter)
        self.particles.update(dt)
        self.impacts.update(dt,self.fighters,self.platforms[0])
        self.hud.update(dt,self.fighters)
        self.camera.update(dt,self.fighters,self.drop)
        self.feedback.tick(self,dt)
        self.shake = max(0, self.shake - dt)
        amplitude = max(1,round(self.shake*28))
        self.shake_offset = (self.rng.randint(-amplitude,amplitude),self.rng.randint(-amplitude,amplitude)) if self.shake else (0,0)
        self.check_result()

    def draw(self, surface):
        debug=bool(self.game and self.game.debug)
        self.art.configure(self.fighters,self.drop,self.settings)
        self.art.draw(self.world, self.time)
        self.drop.draw(self.world, self.time)
        for fighter in sorted(self.fighters,key=lambda f:(f.attack_time>0 and f.windup<=0,f.inventory.weapon.name=='Panela')):
            fighter.draw(self.world)
        self.drop.art.draw_collection(self.world,self.drop)
        self.particles.draw(self.world)
        self.impacts.draw(self.world)
        self.art.draw_foreground(self.world)
        if debug: self.debug_overlay.draw_world(self.world,self)
        self.camera.present(self.world,surface)
        if self.flow.phase=="intro":
            self.transition.fill((3,6,22,round(180*max(0,1-self.flow.elapsed/.65))))
            surface.blit(self.transition,(0,0))
        self.hud.draw(surface, self.player, self.enemy, self.level["name"], self.drop)
        if self.flow.label:
            panel(surface,(338,260,604,140),CYAN)
            text(surface,self.flow.label,(640,318),40 if self.flow.phase=="intro" else 80,CYAN,True,True)
            if self.flow.can_skip: text(surface,"ENTER  pular apresentação",(640,373),22,MUTED,True)
        if self.result and self.flow.phase=="result":
            shade(surface)
            if self.result=="DERROTA":
                self.transition.fill((90,0,20,50))
                surface.blit(self.transition,(0,0))
            else:
                self.particles.draw(surface)
            color = CYAN if self.result == "VITÓRIA" else PINK
            panel(surface, (361, 218, 558, 281), color)
            text(surface, self.result, (640, 281), 66, color, True, True)
            text(surface, self.result_reason, (640, 344), 28, WHITE, True)
            text(surface, "R  reiniciar     ENTER  voltar ao menu", (640, 420), 27, WHITE, True)
            text(surface, "MARCO 1  /  DUELO ENCERRADO", (640, 466), 20, MUTED, True)
        if debug: self.debug_overlay.draw(surface,self,self.game.clock.get_fps())
