"""Entrega dourada em camadas, com gradientes locais pré-calculados."""
import math
import pygame
from scripts.effects.pan_art import pan,GOLD
from scripts.balance import DELIVERY


class DeliveryArt:
    def __init__(self,floor):
        self.floor=floor
        self.width=132
        self.beams=[]
        # Perfis transversais suaves: halo 112 px, coluna 44 px, núcleo 16 px.
        for phase in range(6):
            layer=pygame.Surface((self.width,floor+1),pygame.SRCALPHA)
            breath=.94+phase*.018
            for x in range(self.width):
                d=abs(x-self.width/2)/breath
                halo=44*math.exp(-(d/44)**2)
                column=145*math.exp(-(d/20)**4)
                core=110*math.exp(-(d/7.5)**4)
                alpha=min(252,round(halo+column+core))
                warmth=min(1,core/90)
                color=(255,round(222+30*warmth),round(30+180*warmth),alpha)
                pygame.draw.line(layer,color,(x,0),(x,floor))
            self.beams.append(layer)
        self.lines=pygame.Surface((self.width,floor+1),pygame.SRCALPHA)
        self.floor_light=pygame.Surface((200,36),pygame.SRCALPHA)
        for radius in range(95,4,-3):
            alpha=round(2+35*(1-radius/95)**2)
            pygame.draw.ellipse(self.floor_light,(*GOLD,alpha),(100-radius,18-radius*.14,radius*2,radius*.28))

    def draw(self,surface,drop,t):
        state=drop.state
        falling=state=='falling' and drop.sky_drop
        signal=state in ('warning','opening') or falling
        if signal or drop.beam_fade>0:
            strength=1 if falling else min(1,1-drop.timer/DELIVERY.opening) if state=='opening' else 0
            if not signal: strength=drop.beam_fade/.10
            x=drop.x-self.width/2
            if strength>0:
                beam=self.beams[int(t*16)%6]
                beam.set_alpha(round((.94+.04*math.sin(t*9))*255*strength))
                surface.blit(beam,(x,0))
            self.lines.fill((0,0,0,0))
            if strength>0:
                for i,dx in enumerate((-27,-18,21,31)):
                    y=(t*(95+i*38)+i*91)%self.floor
                    pygame.draw.line(self.lines,(255,244,163,95),(66+dx,y),(66+dx,min(self.floor,y+90)),1)
            for i in range(22):
                speed=95+(i%5)*27
                if state=='warning':
                    y=self.floor-(t*speed+i*29)%115
                else:
                    y=(t*speed*(1 if i%3 else -1)+i*39)%self.floor
                px=20+(i*31)%92
                side=3+i%3
                pygame.draw.rect(self.lines,(255,224,65,175),(px,y,side,side))
            if falling:
                for i,(_,y) in enumerate(drop.trail[:-1]):
                    pygame.draw.ellipse(self.lines,(255,230,100,18+i*8),(55,y-5,22,10))
            surface.blit(self.lines,(x,0))
            pulse=1+.07*math.sin(t*11)
            radius=48*pulse
            surface.blit(self.floor_light,(drop.x-100,self.floor-12))
            pygame.draw.ellipse(surface,GOLD,(drop.x-radius,self.floor-5,radius*2,14),3)
            pygame.draw.ellipse(surface,(255,246,161),(drop.x-radius*.85,self.floor-3,radius*1.7,10),1)
        if state in ('falling','available'):
            squash=1
            if state=='available' and drop.impact_age<DELIVERY.impact_compression:
                squash=1-.30*math.sin(math.pi*drop.impact_age/DELIVERY.impact_compression)
            pan(surface,(drop.x,drop.y),drop.angle if state=='falling' else -12,1,squash=squash)
            if state=='available':
                surface.blit(self.floor_light,(drop.x-100,self.floor-12))

    def draw_collection(self,surface,drop):
        if not drop.collection: return
        f,start,elapsed=drop.collection
        u=min(1,elapsed/DELIVERY.pickup_flight)
        ease=1-(1-u)**3
        target=f.weapon_center
        point=start.lerp(target,ease)+pygame.Vector2(0,-math.sin(u*math.pi)*24)
        for k in range(3):
            prev=start.lerp(point,1-k*.13)
            pygame.draw.circle(surface,(180-k*30,143-k*24,30),prev,2)
        aim=f.swing_vector() if f.attack_time>0 and f.windup<=0 else f.aim
        angle=165-math.degrees(math.atan2(aim.y,aim.x))
        delta=(angle+12+180)%360-180
        pan(surface,point,-12+delta*u,1-u*.15)
