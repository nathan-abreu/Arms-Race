"""Slots, ícones, teclas e feedback visual, sem regras de combate."""
import math
import pygame
from scripts.ui.style import panel,text
from scripts.ui.weapon_icons import weapon_icon
from scripts.effects.neon import CYAN,GOLD

SLOT_W,SLOT_H,GAP=82,76,8
SLOT_X,SLOT_Y=993,600


class InventoryView:
    def __init__(self):
        self.pulses=[0.0]*3
        self.collection=-1
        self.name_time=0.0
        self.flights=[]
        self.clock=0.0

    def update(self,dt,inventory):
        self.clock+=dt
        self.pulses=[max(0,p-dt) for p in self.pulses]
        self.name_time=max(0,self.name_time-dt)
        for flight in self.flights: flight[2]+=dt
        self.flights=[f for f in self.flights if f[2]<.25]
        while inventory.changes:
            event,index,weapon=inventory.changes.popleft()
            if event=='discard' and weapon:
                self.flights.append([index,weapon,0.0])
            else:
                self.pulses[index]=.55 if event=='collect' else .18
            if event=='collect':
                self.collection=index;self.name_time=.75

    def draw(self,surface,inventory):
        for i,weapon in enumerate(inventory.display_slots):
            x=SLOT_X+i*(SLOT_W+GAP)
            chosen=i==inventory.selected
            color=GOLD if chosen and weapon and weapon.icon=='panela' else CYAN if chosen else (149,174,237)
            pulse=self.pulses[i]
            if chosen or pulse:
                panel(surface,(x-3,SLOT_Y-3,SLOT_W+6,SLOT_H+6),(*color,35),fill=(0,0,0,0),width=2)
            panel(surface,(x,SLOT_Y,SLOT_W,SLOT_H),color,(4,9,26,240),2)
            if weapon:
                icon=weapon_icon(weapon.icon)
                bounce=math.sin(min(1,pulse/.55)*math.pi)*5
                surface.blit(icon,(x+(SLOT_W-52)//2,SLOT_Y+(SLOT_H-42)//2-bounce))
                if weapon.ammo is not None:
                    text(surface,str(weapon.ammo),(x+SLOT_W-15,SLOT_Y+SLOT_H-17),16,(210,221,255),True)
            key=pygame.Rect(x+(SLOT_W-24)//2,SLOT_Y+SLOT_H+6,24,20)
            pygame.draw.rect(surface,(137,162,228),key,border_radius=2)
            text(surface,str(i+1),key.center,21,(6,14,38),True,True)
        for index,weapon,age in self.flights:
            icon=weapon_icon(weapon.icon).copy()
            icon.set_alpha(round(255*(1-age/.25)))
            surface.blit(icon,(SLOT_X+index*(SLOT_W+GAP)+15+age*80,SLOT_Y+17-age*170))
        if self.name_time>0:
            text(surface,'PANELA',(SLOT_X+131,SLOT_Y-16),19,GOLD,True)
        if inventory.preview is not None:
            text(surface,'F4 · PRÉVIA DE ÍCONES',(SLOT_X+131,SLOT_Y-37),17,(183,195,239),True)
