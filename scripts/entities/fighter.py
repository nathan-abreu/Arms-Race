import math
from collections import deque
import pygame
from scripts.config import GOLD, WHITE
from scripts.combat.weapon import Inventory, FISTS
from scripts.combat.melee import Melee
from scripts.entities.movement import Movement
from scripts.ui.style import line
from scripts.arena_layout import FIGHTER_HEIGHT, FIGHTER_WIDTH


class Fighter(Movement, Melee):
    """Shared combatant. Position is the center of the feet."""
    WIDTH, HEIGHT = FIGHTER_WIDTH, FIGHTER_HEIGHT

    def __init__(self, position, color):
        self.pos = pygame.Vector2(position)
        self.velocity = pygame.Vector2()
        self.color = color
        self.health = 100
        self.facing = 1
        self.grounded = False
        self.axis = 0
        self.inventory = Inventory()
        self.cooldown = self.attack_time = self.invulnerable = self.stun = 0.0
        self.attack_weapon = FISTS
        self.attack_facing = 1
        self.hit_targets = set()
        self.animation_time = 0.0
        self.rope_cooldown = 0.0
        self.windup = self.recovery = self.landing_time = 0.0
        self.landed_speed = 0.0
        self.events = deque(maxlen=24)
        self.art = None
        self.legacy_art = False
        self.celebrating = False
        self.stride_distance = 0.0
        self.visual_quality = 1
        self.visual_ground = self.pos.y
        self.flash_time = 0.0
        self.pickup_time = 0.0
        self.init_movement()
        self.init_melee()

    @property
    def rect(self):
        return pygame.Rect(round(self.pos.x-self.WIDTH/2), round(self.pos.y-self.HEIGHT),self.WIDTH,self.HEIGHT)

    @property
    def alive(self):
        return self.health>0 and self.pos.y<800 and -120<self.pos.x<1400

    @property
    def body_capsule(self):
        return self.pos+(0,-127),self.pos+(0,-64),26

    def hurt_capsules(self):
        from scripts.entities.poses import pose
        points=self.art.points if self.art and self.art.points else pose(self)
        p={k:self.pos+v for k,v in points.items()}
        result=[(p['shoulder'],p['hip'],15),(p['head'],p['head'],17)]
        for keys in (('shoulder','elbow','hand'),('back_shoulder','back_elbow','back_hand'),('hip','knee_l','foot_l'),('hip','knee_r','foot_r')):
            for a,b in zip(keys,keys[1:]): result.append((p[a],p[b],8))
        return result

    @property
    def weapon_center(self):
        from scripts.entities.poses import pose
        points=self.art.points if self.art and self.art.points else pose(self)
        aim=self.swing_vector() if self.attack_time>0 and self.windup<=0 else self.aim
        return self.pos+points['hand']+aim*22

    def update(self,dt,platforms,walls=()):
        self.animation_time += dt
        self.tick_attack(dt)
        for attr in ('invulnerable','stun','rope_cooldown','landing_time','pickup_time','flash_time'):
            setattr(self,attr,max(0,getattr(self,attr)-dt))
        self.move_step(dt,platforms,walls)
        if self.grounded:
            self.stride_distance += abs(self.velocity.x)*dt
        self.animate(dt)

    def animate(self,dt):
        if self.art is None:
            from scripts.entities.fighter_art import FighterArt
            self.art = FighterArt()
        self.art.update(dt,self)

    def draw(self, surface):
        if self.legacy_art:
            self.draw_legacy(surface)
            return
        if self.art is None:
            from scripts.entities.fighter_art import FighterArt
            self.art = FighterArt()
        self.art.draw(surface, self)

    def draw_legacy(self, surface):
        x, feet = self.pos
        color = WHITE if self.invulnerable > 0 and int(self.invulnerable * 35) % 2 == 0 else self.color
        moving = abs(self.velocity.x) > 30
        step = math.sin(self.animation_time * 17) * 12 if moving and self.grounded else 0
        bob = math.sin(self.animation_time * 4) * 2 if self.grounded else -3
        shoulder = pygame.Vector2(x, feet - 48 + bob)
        hip = pygame.Vector2(x - self.facing * 2, feet - 28 + bob)
        pygame.draw.ellipse(surface, (13, 15, 31), (x - 25, feet - 4, 50, 8))
        for side in (-1, 1):
            foot = (x + side * 12 + side * step, feet - (8 if not self.grounded and side == 1 else 0))
            knee = (x + side * 9 - side * step * .3, feet - 15)
            pygame.draw.lines(surface, color, False, [hip, knee, foot], 8)
        pygame.draw.line(surface, color, shoulder, hip, 18)
        head = pygame.Rect(x - 12 + self.facing * 2, feet - 76 + bob, 25, 24)
        pygame.draw.rect(surface, color, head, border_radius=2)
        pygame.draw.line(surface, (14, 23, 42), (head.centerx, head.y + 9), (head.centerx + self.facing * 10, head.y + 9), 3)
        direction = self.attack_facing if self.attack_time > 0 else self.facing
        reach = 34 if self.attack_time > 0 else 19
        hand = shoulder + (direction * reach, -5 if self.attack_time > 0 else 13)
        elbow = shoulder + (direction * 12, 12)
        pygame.draw.lines(surface, color, False, [shoulder + (-direction * 5, 2), shoulder + (-direction * 15, 17), shoulder + (direction * 3, 20)], 7)
        pygame.draw.lines(surface, color, False, [shoulder, elbow, hand], 8)
        pygame.draw.circle(surface, color, hand, 6)
        weapon = self.attack_weapon if self.attack_time > 0 else self.inventory.weapon
        if weapon is not FISTS:
            end = hand + (direction * 54, -4 if self.attack_time > 0 else -34)
            line(surface, GOLD, hand, end, 6)
        if self.attack_time > 0:
            r = self.attack_rect
            pygame.draw.arc(surface, GOLD if weapon is not FISTS else color, r.inflate(6, 10),
                            -.9 if direction > 0 else 2.2, .9 if direction > 0 else 4.1, 3)
