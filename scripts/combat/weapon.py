from dataclasses import dataclass
from collections import deque
import math
import pygame
from scripts.config import GOLD, GRAVITY
from scripts.ui.style import text
from scripts.balance import DELIVERY


@dataclass(frozen=True)
class Weapon:
    name: str
    damage: int
    reach: int
    knockback: float
    cooldown: float
    duration: float
    icon: str = "panela"
    preview_only: bool = False
    ammo: int | None = None


FISTS = Weapon("Soco", 7, 52, 255, .32, .12,"soco")
PAN = Weapon("Panela", 10, 56, 390, .38, .12)
PREVIEW_WEAPONS=(Weapon("Machado",0,0,0,.4,.1,"machado",True),
                 Weapon("Rifle",0,0,0,.4,.1,"rifle",True,30),
                 Weapon("Lançador",0,0,0,.4,.1,"lancador",True,3))


class Inventory:
    def __init__(self):
        self.slots = [None, None, None]
        self.selected = 0
        self.changes=deque(maxlen=16)
        self.preview=None

    @property
    def display_slots(self):
        return self.preview if self.preview is not None else self.slots

    def toggle_preview(self):
        self.preview=None if self.preview is not None else list(PREVIEW_WEAPONS)
        self.changes.append(('cycle',self.selected,None))

    @property
    def weapon(self):
        return self.slots[self.selected] or FISTS

    @property
    def full(self):
        return all(slot is not None for slot in self.slots)

    def cycle(self, direction):
        self.selected = (self.selected + direction) % len(self.slots)
        self.changes.append(('cycle',self.selected,self.display_slots[self.selected]))

    def collect(self, weapon):
        if self.full or weapon.preview_only:
            return False
        index = self.selected if self.slots[self.selected] is None else self.slots.index(None)
        self.slots[index] = weapon
        self.selected = index
        self.changes.append(('collect',index,weapon))
        return True

    def discard(self):
        weapon = self.slots[self.selected]
        self.slots[self.selected] = None
        if weapon: self.changes.append(('discard',self.selected,weapon))
        return weapon


class WeaponDrop:
    """Entrega única, com perigo sinalizado e impacto antes da coleta."""
    def __init__(self, level, rng):
        self.level, self.rng = level, rng
        self.state = "waiting"
        self.timer = level["weapon_interval"]
        self.x, self.y, self.vy = 640.0, -40.0, 0.0
        self.floor_y = level["platforms"][0][1]
        self.lock_owner = None
        self.lock_time = self.pickup_delay = 0.0
        self.sky_drop = True
        self.hit_targets = set()
        self.impact_event = None
        self.damage_events = []
        self.angle = 0.0
        self.trail = []
        self.beam_fade=0.0
        self.impact_age=1.0
        self.collection=None
        from scripts.effects.delivery import DeliveryArt
        self.art=DeliveryArt(self.floor_y)

    def update(self, dt, fighters, platforms):
        self.impact_event = None
        self.damage_events.clear()
        self.beam_fade=max(0,self.beam_fade-dt)
        self.impact_age+=dt
        if self.collection:
            self.collection[2]+=dt
            if self.collection[2]>=DELIVERY.pickup_flight:
                self.collection[0].pickup_time=0
                self.collection=None
        self.lock_time = max(0, self.lock_time-dt)
        self.pickup_delay = max(0, self.pickup_delay-dt)
        if any(PAN in f.inventory.slots for f in fighters):
            self.state = "held"
            return
        if self.state == "held":
            self.state, self.timer = "waiting", self.level["weapon_interval"]
        if self.state in ("waiting", "warning", "opening"):
            self.timer -= dt
            if self.timer <= 0:
                if self.state == "waiting":
                    base = platforms[0]
                    safe = [x for x in self.level["weapon_drop_points"]
                            if base.left+90 < x < base.right-90 and
                            not any(p.left-35 < x < p.right+35 for p in platforms[1:])]
                    self.x = float(self.rng.choice(safe)) if safe else float(base.centerx)
                    self.state, self.timer = "warning", self.level["weapon_warning"]
                    self.y, self.vy, self.angle = -40.0, 0.0, 0.0
                    self.hit_targets.clear()
                    self.trail.clear()
                    self.sky_drop = True
                    self.lock_owner = None
                elif self.state=='warning':
                    # A origem precisa estar vazia mesmo se alguém saltou
                    # durante o aviso. O ponto anunciado no piso não muda.
                    spawn=pygame.Rect(self.x-28,-60,56,50)
                    if not any(spawn.colliderect(f.rect) for f in fighters):
                        self.state,self.timer = "opening",DELIVERY.opening
                    else:
                        self.timer=.1
                else:
                    self.state='falling'
        if self.state == "falling":
            old_y = self.y
            self.vy += (DELIVERY.acceleration if self.sky_drop else GRAVITY)*dt
            self.y += self.vy*dt
            self.angle += dt*420
            self.trail.append((self.x,self.y))
            self.trail = self.trail[-7:]
            if self.sky_drop and self.vy > 0:
                swept = pygame.Rect(self.x-25,old_y-14,50,max(28,self.y-old_y+28))
                for fighter in fighters:
                    if fighter not in self.hit_targets and swept.colliderect(fighter.rect):
                        self.hit_targets.add(fighter)
                        direction = 1 if fighter.pos.x >= self.x else -1
                        if fighter.receive_damage(8, 330, direction):
                            self.damage_events.append(fighter)
            for platform in sorted(platforms,key=lambda p:p.top):
                if platform.left <= self.x <= platform.right and old_y+18 <= platform.top <= self.y+18:
                    self.y, self.vy = platform.top-18, 0
                    self.state = "available"
                    self.pickup_delay = .12 if self.sky_drop else 0
                    if self.sky_drop:
                        self.impact_event = (self.x,platform.top)
                        self.beam_fade=.10
                        self.impact_age=0
                    self.trail.clear()
                    break
            if self.y > 780:
                self.state, self.timer = "waiting", self.level["weapon_interval"]

    def try_collect(self, fighter):
        if self.state != "available" or self.pickup_delay>0 or (fighter is self.lock_owner and self.lock_time>0):
            return False
        rect=pygame.Rect(self.x-28,self.y-20,56,40)
        if fighter.alive and fighter.rect.colliderect(rect) and fighter.inventory.collect(PAN):
            self.state="held"
            self.collection=[fighter,pygame.Vector2(self.x,self.y),0.0]
            fighter.pickup_time=DELIVERY.pickup_flight
            return True
        return False

    def discard(self, fighter):
        if fighter.inventory.preview is not None:
            index=fighter.inventory.selected
            weapon=fighter.inventory.preview[index]
            if weapon:
                fighter.inventory.preview[index]=None
                fighter.inventory.changes.append(('discard',index,weapon))
                fighter.events.append('discard')
            return weapon is not None
        weapon=fighter.inventory.discard()
        if weapon is None:
            return False
        self.collection=None
        fighter.pickup_time=0
        self.x,self.y=fighter.weapon_center
        self.angle=165-math.degrees(math.atan2(fighter.aim.y,fighter.aim.x))
        self.vy=-180
        self.state="falling"
        self.lock_owner,self.lock_time=fighter,1.0
        self.sky_drop=False
        self.trail.clear()
        self.hit_targets.clear()
        fighter.events.append('discard')
        return True

    def draw(self, surface, time):
        self.art.draw(surface,self,time)
