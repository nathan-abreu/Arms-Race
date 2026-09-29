"""Silhueta geométrica: preenchimento contínuo, borda de 1 px e halo de 6 px."""
import math
import pygame
from scripts.combat.weapon import FISTS
from scripts.effects.pan_art import pan
from scripts.entities.poses import pose
from scripts.arena_layout import SHOULDER_HEIGHT

INK=(5,18,37)
DRAW_ORDER=('back_limbs','torso','front_leg','head','front_arm','hands','weapon','effects')


def limb(surface,color,points,width):
    for a,b in zip(points,points[1:]):
        delta=b-a
        normal=pygame.Vector2(-delta.y,delta.x)
        if normal.length_squared(): normal.scale_to_length(width*.5)
        pygame.draw.polygon(surface,color,[a+normal,b+normal,b-normal,a-normal])
    # Pequeno preenchimento quadrado une os segmentos, sem bolotas articulares.
    for point in points[1:-1]:
        pygame.draw.rect(surface,color,(point.x-width*.4,point.y-width*.4,width*.8,width*.8))


class FighterArt:
    draw_order=DRAW_ORDER

    def __init__(self):
        self.sprite=pygame.Surface((300,270),pygame.SRCALPHA)
        self.reflection=pygame.Surface((300,34),pygame.SRCALPHA)
        self.points={}

    def update(self,dt,f):
        target=pose(f)
        alpha=1-math.exp(-32*dt)
        for key,value in target.items():
            self.points[key]=self.points.get(key,value).lerp(value,alpha)
        if f.grounded:
            for key in ('foot_l','foot_r'): self.points[key]=target[key]
        if f.attack_time>0 and f.windup<=0:
            for key in ('hand','elbow','back_hand','back_elbow'):
                self.points[key]=target[key]

    def _body(self,s,p,f,color,extra=0,flat=False):
        rear=color if flat else tuple(round(v*.82) for v in color[:3])
        limb(s,rear,[p['hip'],p['knee_l'],p['foot_l']+(0,-4)],16+extra)
        limb(s,rear,[p['back_shoulder'],p['back_elbow'],p['back_hand']],15+extra)
        h,sh=p['hip'],p['shoulder']
        pygame.draw.polygon(s,color,[sh+(-15-extra/2,-4),sh+(15+extra/2,-4),h+(14+extra/2,6),h+(-14-extra/2,6)])
        limb(s,color,[h,p['knee_r'],p['foot_r']+(0,-4)],17+extra)
        for side,c in (('l',rear),('r',color)):
            foot=p['foot_'+side]
            pygame.draw.rect(s,c,(foot.x-9-extra/2,foot.y-6-extra/2,23+extra,10+extra))
        # Cabeça inclinável, ligada por pescoço curto; nenhuma linha interna.
        limb(s,color,[sh,p['head']+(0,12)],10+extra)
        tilt=f.facing*.10+max(-.16,min(.16,f.velocity.x*.00025))
        if not f.alive: tilt=-f.facing*1.25
        half=17+extra/2
        vertices=[p['head']+pygame.Vector2(x,y).rotate_rad(tilt) for x,y in ((-half,-half),(half,-half),(half,half),(-half,half))]
        pygame.draw.polygon(s,color,vertices)
        limb(s,color,[sh,p['elbow'],p['hand']],16+extra)
        if f.punch_arm==1 and (f.attack_time>0 or f.windup>0):
            limb(s,rear,[p['back_shoulder'],p['back_elbow'],p['back_hand']],15+extra)
        for key,c in (('back_hand',rear),('hand',color)):
            hand=p[key]
            pygame.draw.polygon(s,c,[hand+(-6-extra/2,-7-extra/2),hand+(7+extra/2,-5-extra/2),
                                     hand+(6+extra/2,7+extra/2),hand+(-6-extra/2,6+extra/2)])

    def draw(self,surface,f):
        if not self.points: self.update(1,f)
        s=self.sprite;s.fill((0,0,0,0))
        origin=pygame.Vector2(150,218)
        p={k:v+origin for k,v in self.points.items()}
        color=(249,255,255) if f.flash_time>0 else f.color
        if f.visual_quality:
            self._body(s,p,f,(*f.color,12),extra=12,flat=True)
            self._body(s,p,f,(*f.color,22),extra=6,flat=True)
        self._body(s,p,f,INK,extra=2,flat=True)
        self._body(s,p,f,color)
        weapon=f.attack_weapon if f.attack_time>0 else f.inventory.weapon
        aim=f.swing_vector() if f.attack_time>0 and f.windup<=0 else (f.aim if f.aim_locked else pygame.Vector2(f.facing,0))
        if weapon is not FISTS and f.pickup_time<=0:
            pan(s,p['hand']+aim*22,165-math.degrees(math.atan2(aim.y,aim.x)),.85)
        if f.attack_time>0 and f.windup<=0:
            progress=1-f.attack_time/f.attack_duration
            arc=[origin+(0,-SHOULDER_HEIGHT)+f.swing_vector(max(0,progress-i*.065))*(f.strike_reach(max(0,progress-i*.065))+(18 if weapon is not FISTS else 0)) for i in range(7)]
            pygame.draw.lines(s,(255,226,108,190) if weapon is not FISTS else (*color,115),False,arc,4 if weapon is not FISTS else 2)
        x,y=f.pos.x-origin.x,f.pos.y-origin.y
        if f.grounded:
            pygame.draw.ellipse(surface,(4,10,29),(f.pos.x-39,f.pos.y-2,78,6))
            if f.visual_quality>0:
                pygame.transform.smoothscale(s,(300,34),self.reflection)
                reflected=pygame.transform.flip(self.reflection,False,True)
                reflected.set_alpha(27 if f.visual_quality==2 else 16)
                surface.blit(reflected,(x,f.pos.y+2),area=(0,0,300,13))
        elif f.pos.y<f.visual_ground:
            width=max(30,78-(f.visual_ground-f.pos.y)*.18)
            pygame.draw.ellipse(surface,(7,15,36),(f.pos.x-width/2,f.visual_ground-2,width,5))
        surface.blit(s,(x,y))
