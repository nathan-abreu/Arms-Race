import pygame
from scripts.effects.neon import CYAN, PINK, GOLD, pan
from scripts.config import WHITE, MUTED
from scripts.ui.style import panel, text
from scripts.ui.inventory_view import InventoryView


class HUD:
    def __init__(self):
        self.delayed = [100.0,100.0]
        self.previous = [100,100]
        self.hold = [0.0,0.0]
        self.displayed = [100.0,100.0]
        self.layer=pygame.Surface((1280,720),pygame.SRCALPHA)
        self.inventory_view=InventoryView()
        self.time=0.0

    def update(self,dt,fighters):
        self.time+=dt
        self.inventory_view.update(dt,fighters[0].inventory)
        for i,f in enumerate(fighters):
            if f.health < self.previous[i]:
                self.hold[i]=.3
            self.previous[i]=f.health
            self.displayed[i]=max(f.health,self.displayed[i]-dt*180)
            self.hold[i]=max(0,self.hold[i]-dt)
            if self.hold[i]==0:
                self.delayed[i]=max(f.health,self.delayed[i]-dt*45)

    def draw(self,surface,player,enemy,name,drop):
        self.layer.fill((0,0,0,0))
        self._draw(self.layer,player,enemy,name,drop)
        surface.blit(self.layer,(0,0),area=(0,0,1280,165))
        surface.blit(self.layer,(0,550),area=(0,550,1280,170))

    def _draw(self,surface,player,enemy,name,drop):
        for i,(fighter,x,label,c) in enumerate(((player,15,"JOGADOR",CYAN),(enemy,924,"INIMIGO",PINK))):
            panel(surface,(x,15,341,71),c,(3,9,25,228),2)
            pygame.draw.polygon(surface,c,[(x+23,26),(x+43,30),(x+39,50),(x+19,46)])
            pygame.draw.line(surface,c,(x+26,52),(x+18,72),13)
            pygame.draw.lines(surface,c,False,[(x+30,54),(x+43,66),(x+52,61)],7)
            text(surface,label,(x+66,23),28,WHITE,bold=True)
            pygame.draw.rect(surface,(35,22,51),(x+66,53,194,18),border_radius=3)
            pygame.draw.rect(surface,(244,195,225),(x+66,53,round(194*self.delayed[i]/100),18),border_radius=3)
            bar=pygame.Rect(x+66,53,round(194*self.displayed[i]/100),18)
            pygame.draw.rect(surface,(*c,26),bar.inflate(10,8),border_radius=6)
            pygame.draw.rect(surface,c,bar,border_radius=3)
            pygame.draw.line(surface,tuple(min(255,v+60) for v in c),bar.topleft,bar.topright,2)
            text(surface,f"{fighter.health}/100",(x+267,53),23,c,bold=True)
        panel(surface,(409,15,462,48),CYAN,(3,9,28,230),3)
        text(surface,name,(640,38),29,WHITE,True,True)
        panel(surface,(550,62,180,26),CYAN,(3,9,28,230),2)
        text(surface,"DUELO",(640,75),24,CYAN,True,True)
        self.inventory_view.draw(surface,player.inventory)
        if self.time<6:
            text(surface,"A/D mover · ESPAÇO pular · MOUSE atacar · ESC pausa",(24,688),17,(160,176,207))
        ratio=max(0,min(1,1-player.cooldown/player.attack_total))
        pygame.draw.rect(surface,(40,34,64),(24,655,120,6))
        pygame.draw.rect(surface,PINK if player.denied_time>0 else CYAN,(24,655,round(120*ratio),6))
        label="PRÓXIMO GOLPE" if player.queued_click>0 else "RECUPERANDO" if player.denied_time>0 else f"COMBO {player.combo_index}/3" if player.combo_left>0 and player.combo_index else "GOLPE"
        text(surface,label,(24,632),18,PINK if player.denied_time>0 else MUTED)
        if 0<min(player.health,enemy.health)<=28:
            text(surface,"VIDA BAIXA — CADA GOLPE CONTA",(640,110),24,PINK,True,True)
        if drop.state=="warning":
            text(surface,"ARMA CHEGANDO",(640,140),22,(255,220,60),True)
