"""Ataques direcionais em arco. Desenho e colisão usam a mesma trajetória."""
import math
import pygame
from scripts.balance import COMBAT, MOVEMENT
from scripts.combat.weapon import FISTS
from scripts.arena_layout import SHOULDER_HEIGHT
from scripts.combat.contact import capsule_contact


class Melee:
    def init_melee(self):
        self.aim = pygame.Vector2(1, 0)
        self.aim_point = self.pos + (200,-80)
        self.aim_locked = False
        self.attack_direction = pygame.Vector2(1,0)
        self.attack_contact = self.pos.copy()
        self.denied_time = 0.0
        self.connected = False
        self.combo_index = 0
        self.combo_left = 0.0
        self.queued_click = 0.0
        self.attack_duration = FISTS.duration
        self.attack_total = FISTS.cooldown
        self.attack_damage = FISTS.damage
        self.attack_knockback = FISTS.knockback
        self.attack_recovery = COMBAT.recovery
        self.strong_attack = False
        self.punch_arm = 0

    @property
    def shoulder(self):
        return self.pos + (0,-SHOULDER_HEIGHT)

    def set_aim(self, point):
        self.aim_point = pygame.Vector2(point)
        delta = self.aim_point-self.shoulder
        self.aim_locked = True
        if delta.length_squared()>16:
            self.aim = delta.normalize()
        if abs(delta.x)>COMBAT.aim_deadzone:
            self.facing = 1 if delta.x>0 else -1

    @property
    def attack_phase(self):
        return "preparação" if self.windup>0 else "ativo" if self.attack_time>0 else "recuperação" if self.recovery>0 else "guarda"

    def swing_vector(self, progress=None):
        if progress is None:
            progress = 1-self.attack_time/max(.001,self.attack_duration)
        # Fists are straight; the Panela traverses a short arc about the aim.
        arc = COMBAT.pan_arc if self.attack_weapon is not FISTS else (32 if self.strong_attack else 12)
        return self.attack_direction.rotate((progress-.5)*arc*self.attack_facing)

    def attack_segment(self, progress=None):
        direction=self.swing_vector(progress)
        reach=self.strike_reach(progress)
        # Volume na luva/bojo, não no braço inteiro nem dentro do tronco.
        return self.shoulder+direction*(reach-20), self.shoulder+direction*reach

    def strike_reach(self,progress=None):
        if progress is None: progress=1-self.attack_time/max(.001,self.attack_duration)
        extension=.55+.45*max(0,min(1,progress/.30))
        return (self.attack_weapon.reach+20)*extension

    @property
    def attack_rect(self):
        a,b = self.attack_segment()
        radius = 14 if self.attack_weapon is not FISTS else 10
        return pygame.Rect(min(a.x,b.x)-radius,min(a.y,b.y)-radius,abs(a.x-b.x)+radius*2,abs(a.y-b.y)+radius*2)

    def attack(self):
        if self.cooldown>0 or self.stun>0 or self.recovery>0 or not self.alive:
            self.denied_time = .12
            if self.stun<=0 and self.alive and 0<self.cooldown<=COMBAT.combo_buffer:
                self.queued_click=COMBAT.combo_buffer
            return False
        self.attack_weapon = self.inventory.weapon
        unarmed=self.attack_weapon is FISTS
        self.combo_index=(self.combo_index%3+1) if unarmed and self.combo_left>0 else (1 if unarmed else 0)
        self.punch_arm=1 if self.combo_index==2 else 0
        self.strong_attack=not unarmed or self.combo_index==3
        self.attack_total=COMBAT.combo_durations[self.combo_index-1] if unarmed else self.attack_weapon.cooldown
        self.attack_duration=COMBAT.combo_active[self.combo_index-1] if unarmed else self.attack_weapon.duration
        self.attack_damage=COMBAT.combo_damage[self.combo_index-1] if unarmed else self.attack_weapon.damage
        self.attack_knockback=COMBAT.combo_knockback[self.combo_index-1] if unarmed else self.attack_weapon.knockback
        self.attack_recovery=self.attack_total-COMBAT.preparation-self.attack_duration
        self.combo_left=self.attack_total+COMBAT.combo_window
        self.queued_click=0
        self.attack_direction = self.aim.copy() if self.aim_locked else pygame.Vector2(self.facing,0)
        self.attack_facing = 1 if self.attack_direction.x>=0 else -1
        self.cooldown = self.attack_total
        self.windup = COMBAT.preparation
        self.attack_time = self.attack_duration
        self.recovery = 0
        self.hit_targets.clear()
        self.connected = False
        self.events.append('metal_swing' if not unarmed else "air_attack" if not self.grounded else "swing")
        self.animate(.012)  # antecipação visível já no quadro do clique
        return True

    def tick_attack(self,dt):
        self.denied_time = max(0,self.denied_time-dt)
        self.cooldown=max(0,self.cooldown-dt)
        self.combo_left=max(0,self.combo_left-dt)
        self.recovery=max(0,self.recovery-dt)
        remaining=dt
        if self.windup>0:
            remaining=max(0,dt-self.windup)
            self.windup = max(0,self.windup-dt)
        if self.windup<=0 and self.attack_time>0:
            overflow=max(0,remaining-self.attack_time)
            self.attack_time = max(0,self.attack_time-remaining)
            if self.attack_time==0:
                self.recovery = max(0,self.attack_recovery-overflow)
                if not self.connected:
                    self.events.append("miss")
        if self.queued_click>0:
            if self.cooldown<=0 and self.recovery<=.001 and self.stun<=0:
                self.attack()
            else:
                self.queued_click=max(0,self.queued_click-dt)

    def resolve_attack(self,target):
        if self.attack_time<=0 or self.windup>0 or target in self.hit_targets or not self.alive:
            return False
        progress = 1-self.attack_time/self.attack_duration
        # Sweep the previous fixed step too, avoiding gaps in a fast arc.
        # Luva/bojo alcançam o membro visível antes de emitir qualquer efeito.
        _,end=self.attack_segment(progress)
        _,previous=self.attack_segment(max(0,progress-.18))
        radius=22 if self.attack_weapon is not FISTS else 7
        contact=capsule_contact(previous,end,radius,target.hurt_capsules())
        if contact is not None:
            self.hit_targets.add(target)
            self.attack_contact=contact
            if target.receive_damage(self.attack_damage,self.attack_knockback,self.attack_direction):
                self.connected=True
                return True
        return False

    def receive_damage(self,damage,knockback,direction):
        if self.invulnerable>0 or not self.alive:
            return False
        self.health = max(0,self.health-damage)
        vector=pygame.Vector2(direction,0) if isinstance(direction,(int,float)) else pygame.Vector2(direction)
        if vector.length_squared()==0:
            vector=pygame.Vector2(1,0)
        vector=vector.normalize()
        self.velocity = vector*knockback
        self.velocity.y = min(self.velocity.y-150,-100)
        self.grounded = False
        self.invulnerable = MOVEMENT.invulnerability
        self.flash_time = COMBAT.hit_flash
        self.stun = MOVEMENT.hitstun
        # Hitstun cancels preparation/active phase; no cancel by inventory cycling.
        self.windup = self.attack_time = 0
        self.queued_click = self.combo_left = 0
        self.recovery = .10
        self.events.append("damage")
        return True
