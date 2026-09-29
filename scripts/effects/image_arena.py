"""Arena v2: uma imagem-base e overlays locais de luz, sem reconstruir cenário.

As superfícies persistem entre quadros e partidas. Coordenadas de máscaras
estão normalizadas na imagem; parallax só desloca luz/poeira, nunca o piso.
"""
import math
import random
from functools import lru_cache
import pygame
from scripts.arena_layout import BACKGROUND_PATH, GROUND_Y
from scripts.config import WIDTH, HEIGHT
from scripts.effects.neon import CYAN, PINK, BLUE, PURPLE, halo


@lru_cache(maxsize=4)
def load_background(path=BACKGROUND_PATH):
    try:
        raw = pygame.image.load(str(path)).convert()
        # Ajuste proporcional: a fonte v2 é 1672×941 (arredondamento de 16:9).
        scale = max(WIDTH/raw.get_width(), HEIGHT/raw.get_height())
        size = (round(raw.get_width()*scale), round(raw.get_height()*scale))
        base = pygame.Surface((WIDTH, HEIGHT)).convert()
        base.fill((3, 7, 25))
        base.blit(pygame.transform.smoothscale(raw, size),
                  ((WIDTH-size[0])//2, (HEIGHT-size[1])//2))
        return base, True
    except (pygame.error, OSError):
        base = pygame.Surface((WIDTH, HEIGHT)).convert()
        for y in range(HEIGHT):
            pygame.draw.line(base, (3, 7+int(5*y/HEIGHT), 22+int(14*y/HEIGHT)), (0,y),(WIDTH,y))
        return base, False


class ImageArena:
    def __init__(self):
        self.base, self.image_found = load_background()
        self.stage = self.base.copy()
        dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dim.fill((2, 7, 26, 24))
        self.stage.blit(dim, (0,0))
        self.overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.dark = pygame.Surface((WIDTH, HEIGHT)).convert()
        self.dark.fill((2, 5, 22))
        self.vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.fog=pygame.Surface((WIDTH,180),pygame.SRCALPHA)
        for y in range(180):
            alpha=round(7*math.sin(math.pi*y/180)**2)
            pygame.draw.line(self.fog,(24,85,175,alpha),(0,y),(WIDTH,y))
        for i in range(30):
            pygame.draw.rect(self.vignette,(1,3,15,max(0,22-i//2)),(i*2,i,WIDTH-i*4,HEIGHT-i*2),2)
        self.stage.blit(self.vignette,(0,0))
        fog_rgb=pygame.Surface(self.fog.get_size()).convert()
        fog_rgb.fill((0,0,0));fog_rgb.blit(self.fog,(0,0))
        self.fog=fog_rgb
        self.time = self.reaction = 0.0
        self.damage = [0.0, 0.0]
        self.rope_pulse = 0.0
        self.quality = 1
        self.fighters = ()
        self.drop = None
        self.winner = None
        self.low_health = False
        rng = random.Random(104)
        self.sticks = []
        # Apenas luzes sobre as duas faixas da plateia, sem silhuetas novas.
        for _ in range(105):
            x = rng.uniform(.02,.98)
            y = rng.uniform(.435,.54) if .25<x<.75 else rng.uniform(.40,.51)
            self.sticks.append((x*WIDTH,y*HEIGHT,rng.uniform(0,math.tau),rng.choice((CYAN,PINK,PURPLE)),rng.uniform(4,8)))
        self.dust = [(rng.random()*WIDTH,rng.uniform(140,530),rng.random()*math.tau) for _ in range(34)]
        self.screens = []
        self.screen_polygons=[]
        quads=( ((.063,.202),(.209,.251),(.209,.380),(.063,.344)),
                ((.390,.255),(.610,.255),(.610,.382),(.390,.382)),
                ((.799,.253),(.939,.202),(.939,.344),(.799,.380)) )
        for box,quad in zip(((.054,.19,.166,.225),(.377,.235,.249,.165),(.784,.19,.166,.225)),quads):
            r = pygame.Rect(round(box[0]*WIDTH),round(box[1]*HEIGHT),round(box[2]*WIDTH),round(box[3]*HEIGHT))
            patch = self.base.subsurface(r).copy().convert_alpha()
            patch.fill((15,25,45), special_flags=pygame.BLEND_RGB_ADD)
            poly=[(round(x*WIDTH),round(y*HEIGHT)) for x,y in quad]
            mask=pygame.Surface(r.size,pygame.SRCALPHA)
            pygame.draw.polygon(mask,(255,255,255,255),[(x-r.x,y-r.y) for x,y in poly])
            patch.blit(mask,(0,0),special_flags=pygame.BLEND_RGBA_MULT)
            self.screen_polygons.append(poly)
            self.screens.append((r,patch))
        # Os gradientes dos holofotes são gerados uma vez. Só a posição varia.
        self.beams = []
        for color in (CYAN,BLUE,PURPLE):
            s = pygame.Surface((240,390),pygame.SRCALPHA)
            for y in range(0,390,5):
                width=5+y*.24
                alpha=round(17*(1-y/420))
                pygame.draw.polygon(s,(*color,alpha),[(120-width,y),(120+width,y),(120+width+2,y+5),(120-width-2,y+5)])
            rgb=pygame.Surface(s.get_size()).convert()
            rgb.fill((0,0,0));rgb.blit(s,(0,0))
            self.beams.append(rgb)
        self.rope_points = [
            [(round(x*WIDTH),round((y+offset)*HEIGHT)) for x,y in ((.17,.557),(.34,.573),(.50,.578),(.66,.573),(.83,.557))]
            for offset in (0,.039,.079)]

    def configure(self, fighters, drop, settings):
        self.fighters, self.drop = fighters, drop
        self.quality = settings.particles
        self.low_health = min(f.health for f in fighters)<=28
        self.winner = next((f for f in fighters if f.celebrating),None)

    def react(self, strength=1, side=None):
        self.reaction=max(self.reaction,min(1.5,strength))
        self.rope_pulse=max(self.rope_pulse,strength)
        if side is not None:
            self.damage[side]=.22

    def update(self, dt):
        self.time+=dt
        self.reaction=max(0,self.reaction-dt*2.7)
        self.rope_pulse=max(0,self.rope_pulse-dt*3)
        self.damage=[max(0,v-dt) for v in self.damage]

    def draw(self, surface, _time=0):
        surface.blit(self.stage,(0,0))
        t=self.time
        q=self.quality
        if self.drop and self.drop.state in ("warning","opening","falling"):
            self.dark.set_alpha(34 if self.drop.state=="falling" else 14)
            surface.blit(self.dark,(0,0))
        elif self.low_health:
            self.dark.set_alpha(round(8+4*math.sin(t*3)))
            surface.blit(self.dark,(0,0))
        if not self.image_found:
            # Fallback honesto: fundo neutro e guia do chão, sem arena antiga.
            pygame.draw.line(surface,(38,73,100),(round(WIDTH*.105),round(HEIGHT*GROUND_Y)),(round(WIDTH*.895),round(HEIGHT*GROUND_Y)),2)
        parallax = ((sum(f.pos.x for f in self.fighters)/2-640)/640 if self.fighters else 0)
        if q:
            surface.blit(self.fog,(round(parallax*2),295+math.sin(t*.25)*3),special_flags=pygame.BLEND_RGB_ADD)
            for i,x in enumerate((185,330,930,1095)):
                beam=self.beams[i%3]
                pos=(x-120+math.sin(t*.35+i)*28+parallax*3,82)
                surface.blit(beam,pos,special_flags=pygame.BLEND_RGB_ADD)
                if self.reaction>.4: surface.blit(beam,pos,special_flags=pygame.BLEND_RGB_ADD)
        for i,(rect,patch) in enumerate(self.screens):
            side=0 if i==0 else 1
            health=self.fighters[side].health/100 if self.fighters else 1
            pulse=math.sin(t*(3 if i==1 else 1.8)+i)
            if i==1 and self.drop and self.drop.state in ('warning','opening'):
                pulse+=3*max(0,math.sin(t*15))
            patch.set_alpha(min(255,round(28+14*pulse+self.reaction*95+(self.damage[side]*350 if i!=1 else 0)+(1-health)*15)))
            surface.blit(patch,(rect.x+round(parallax),rect.y))
        o=self.overlay
        o.fill((0,0,0,0))
        count=(20,55,105)[q]
        for x,y,phase,color,length in self.sticks[:count]:
            sway=math.sin(t*(1.4+self.reaction)+phase)*(2+self.reaction*3)
            alpha=round(35+18*math.sin(t*2+phase)+min(140,self.reaction*100))
            pygame.draw.line(o,(*color,alpha),(x+parallax*2,y),(x+sway+parallax*2,y-length),2)
            if q==2 and math.sin(t*1.1+phase)>.985:
                pygame.draw.circle(o,(230,240,255,90),(round(x),round(y)),2)
        if q:
            for i,(rect,_) in enumerate(self.screens):
                y=rect.top+int((t*22+i*35)%rect.height)
                poly=self.screen_polygons[i]
                crossings=[]
                for a,b in zip(poly,poly[1:]+poly[:1]):
                    if min(a[1],b[1])<=y<max(a[1],b[1]):
                        crossings.append(a[0]+(b[0]-a[0])*(y-a[1])/(b[1]-a[1]))
                if len(crossings)>=2:
                    pygame.draw.line(o,(100,190,255,19),(min(crossings),y),(max(crossings),y),1)
                    if math.sin(t*.9+i)> .99:
                        pygame.draw.line(o,(160,210,255,35),(min(crossings)+4,y),(max(crossings)-4,y),2)
            for i,points in enumerate(self.rope_points):
                alpha=round(9+6*math.sin(t*2+i)+min(95,self.rope_pulse*70))
                offset=math.sin(t*34)*self.rope_pulse*1.5
                path=[(x,y+offset*math.sin(n*math.pi/4)) for n,(x,y) in enumerate(points)]
                pygame.draw.lines(o,(*(PURPLE if i==1 else CYAN),alpha),False,path,3)
            for x,y,p in self.dust[:(15 if q==1 else 34)]:
                px=(x+t*4+parallax*5)%WIDTH
                py=y+math.sin(t*.6+p)*9
                pygame.draw.circle(o,(105,175,240,round(20+12*math.sin(t+p))),(int(px),int(py)),1)
            # Reflexos iluminados apenas no piso, sem alterar sua geometria.
            floor=round(GROUND_Y*HEIGHT)
            for i in range(5 if q==2 else 2):
                x=170+(t*35+i*191)%940
                pygame.draw.line(o,(100,185,255,25),(x,floor+5),(x+28,floor+5),2)
        if self.reaction:
            o.fill((35,80,140,round(min(15,self.reaction*12))),(0,0,WIDTH,round(HEIGHT*.52)))
        surface.blit(o,(0,0))
        for f in self.fighters:
            if q:
                light=halo(tuple(f.color),90)
                surface.blit(light,(f.pos.x-90,f.pos.y-150))
        if self.winner and q:
            beam=self.beams[0 if self.winner is self.fighters[0] else 2]
            surface.blit(beam,(self.winner.pos.x-120,self.winner.pos.y-390),special_flags=pygame.BLEND_RGB_ADD)

    def draw_foreground(self, surface):
        # Somente poeira luminosa em primeiro plano; nunca corpos sobre a luta.
        if self.quality==2:
            for i in range(5):
                x=100+i*230+math.sin(self.time*.4+i)*8
                pygame.draw.circle(surface,(30,55,100),(round(x),round(HEIGHT*.89+math.sin(self.time+i)*3)),1)
