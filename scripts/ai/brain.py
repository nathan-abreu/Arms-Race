import random
import pygame
from scripts.balance import AI
from scripts.combat.weapon import PAN


class Brain:
    def __init__(self,seed=31):
        self.rng=random.Random(seed)
        self.timer=0.0
        self.state="observar"
        self.retreat=0.0

    @staticmethod
    def in_range(f,target):
        from scripts.combat.contact import capsule_contact
        from scripts.combat.weapon import FISTS
        weapon=f.inventory.weapon
        point=f.shoulder+f.aim*(weapon.reach+20)
        return capsule_contact(point,point,7 if weapon is FISTS else 22,target.hurt_capsules()) is not None

    def decide(self,f,dt,player,drop,platforms):
        self.timer=max(0,self.timer-dt)
        self.retreat=max(0,self.retreat-dt)
        base=platforms[0]
        if f.stun>0:
            f.state="recuperar-se"
            f.axis=0
            return
        if f.pos.x<base.left+32 or f.pos.x>base.right-32:
            f.state="recuar"
            f.axis=1 if f.pos.x<base.centerx else -1
            if f.pos.y>base.top-15: f.jump()
            return
        warning=drop.state in ("warning","opening","falling") and drop.sky_drop
        if warning and abs(f.pos.x-drop.x)<85:
            f.state="desviar de item"
            f.axis=1 if f.pos.x>=drop.x else -1
            self.timer=0
            return
        if self.retreat>0 and f.attack_time<=0:
            f.set_aim(player.shoulder)
            f.state="recuar"
            f.axis=-f.facing if abs(f.pos.x-player.pos.x)<120 else 0
            return
        if f.axis and abs(f.pos.x-player.pos.x)<88 and self.in_range(f,player) and f.state not in ("buscar arma","desviar de item"):
            f.axis=0
        # Orientação visual acompanha a passagem; decisões continuam humanas.
        f.set_aim(player.shoulder)
        if self.timer>0:
            return
        self.timer=self.rng.uniform(AI.reaction_min,AI.reaction_max)
        # Observe somente posições atuais; nenhum acesso ao teclado/mouse.
        f.set_aim(player.shoulder)
        target_x,target_y=player.pos
        f.state="pressionar" if player.health<=AI.low_health else "aproximar"
        valuable=PAN not in f.inventory.slots and not f.inventory.full
        worthwhile=f.health>20 or abs(f.pos.x-drop.x)<abs(player.pos.x-drop.x)+30
        if valuable and worthwhile and drop.state in ("warning","opening","falling","available"):
            target_x,target_y=drop.x,base.top if drop.state!="available" else drop.y
            f.state="buscar arma"
            if warning:
                target_x+=AI.danger_radius*(1 if f.pos.x>=drop.x else -1)
                f.state="desviar de item"
        target_x=max(base.left+AI.edge_margin,min(base.right-AI.edge_margin,target_x))
        delta=target_x-f.pos.x
        f.axis=1 if delta>22 else -1 if delta<-22 else 0
        if f.grounded and target_y<f.pos.y-70:
            f.jump()
            f.state="pular"
        elif self.in_range(f,player) and not (warning and abs(f.pos.x-drop.x)<100):
            if f.cooldown<=0:
                if self.rng.random()>=AI.mistake_chance:
                    f.axis=0
                    f.state="atacar"
                    if f.attack(): self.retreat=f.attack_total+.12
                else:
                    f.state="observar"
                    f.axis=0
            else:
                f.state="recuar" if self.rng.random()<.32 else "manter distância"
                f.axis=-f.facing if f.state=="recuar" else 0
        elif f.grounded and target_y<f.pos.y-55:
            f.jump()
            f.state="pular"
        elif f.grounded and target_y>f.pos.y+50 and f.pos.y<base.top:
            support=next((p for p in platforms[1:] if abs(p.top-f.pos.y)<2 and p.left<f.pos.x<p.right),None)
            if support: f.axis=1 if support.centerx<base.centerx else -1
        elif f.state=="aproximar" and abs(delta)<180 and self.rng.random()<.055:
            f.jump()
            f.state="pular"
