import random
import pygame


class Particles:
    LIMIT=180

    def __init__(self):
        self.items=[]
        self.limit=self.LIMIT
        self.rng=random.Random(51)

    def burst(self,position,color,count=14,direction=0,style="spark"):
        count=max(1,round(count*self.limit/self.LIMIT))
        vector=pygame.Vector2(direction,0) if isinstance(direction,(int,float)) else pygame.Vector2(direction)
        for _ in range(min(count,self.limit-len(self.items))):
            v=pygame.Vector2(self.rng.uniform(-160,160),self.rng.uniform(-230,30))
            if vector.length_squared()>0: v+=vector*self.rng.uniform(80,220)
            if style=='metal': v*=1.65
            life=self.rng.uniform(.18,.4) if style!="confetti" else self.rng.uniform(1,2)
            self.items.append([pygame.Vector2(position),v,life,life,color,style])

    def update(self,dt):
        for p in self.items:
            p[0]+=p[1]*dt
            p[1].y+=(100 if p[5]=="confetti" else 450)*dt
            p[2]-=dt
        self.items=[p for p in self.items if p[2]>0][:self.limit]

    def draw(self,surface):
        for pos,v,life,total,color,style in self.items:
            c=tuple(int(channel*max(.12,life/total)) for channel in color)
            if style=="trail": pygame.draw.line(surface,c,pos,pos-v*.025,3)
            elif style=="confetti": pygame.draw.rect(surface,c,(pos.x,pos.y,4,6))
            elif style=='metal':
                pygame.draw.line(surface,c,pos,pos-v*.022,3)
                pygame.draw.line(surface,(255,250,203),pos,pos-v*.012,1)
            else: pygame.draw.line(surface,c,pos,pos-v*.012,max(1,int(life*8)))
