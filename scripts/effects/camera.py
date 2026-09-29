import math
import random
import pygame


class Camera:
    def __init__(self,settings):
        self.settings=settings
        self.center=pygame.Vector2(640,360)
        self.zoom=1.0
        self.trauma=0.0
        self.punch=0.0
        self.direction=pygame.Vector2(1,0)
        self.shake_pixels=0.0
        self.view=pygame.Rect(0,0,1280,720)
        self.rng=random.Random(92)

    def impulse(self,strength=1,direction=None,pixels=None):
        self.trauma=min(1,self.trauma+strength*.5)
        self.punch=max(self.punch,.018*strength)
        self.shake_pixels=max(self.shake_pixels,pixels if pixels is not None else strength*5)
        if direction is not None and pygame.Vector2(direction).length_squared()>0:
            self.direction=pygame.Vector2(direction).normalize()

    def update(self,dt,fighters,drop=None,intro=False):
        a,b=fighters
        distance=abs(a.pos.x-b.pos.x)
        target=(a.pos+b.pos)*.5+pygame.Vector2(0,-150)
        winner=next((f for f in fighters if f.celebrating),None)
        if winner: target=target.lerp(winner.pos+pygame.Vector2(0,-150),.45)
        target.y=max(310,min(400,target.y))
        zoom=1+max(0,min(.035,(650-distance)/16000))
        if drop and drop.state=="falling" and drop.sky_drop:
            target=target.lerp(pygame.Vector2(drop.x,340),.15)
        if intro: zoom=1.05
        self.zoom+=(zoom+self.punch-self.zoom)*(1-math.exp(-dt*5))
        self.zoom=max(1,min(1.065,self.zoom))
        if self.center.distance_to(target)>22:
            self.center=self.center.lerp(target,1-math.exp(-dt*4))
        self.trauma=max(0,self.trauma-dt*3)
        self.punch=max(0,self.punch-dt*.10)
        self.shake_pixels=max(0,self.shake_pixels-dt*36)
        # Crop sempre contido no mundo; shake nunca revela pixels fora da arena.
        w,h=round(1280/self.zoom),round(720/self.zoom)
        amount=self.shake_pixels*self.settings.shake
        pulse=self.rng.uniform(-amount,amount)
        x=self.center.x-w/2+self.direction.x*pulse
        y=self.center.y-h/2+self.direction.y*pulse+self.rng.uniform(-amount*.25,amount*.25)
        self.view=pygame.Rect(max(0,min(1280-w,x)),max(0,min(720-h,y)),w,h)

    def to_world(self,logical):
        return pygame.Vector2(self.view.x+logical[0]*self.view.width/1280,
                              self.view.y+logical[1]*self.view.height/720)

    def to_screen(self,world):
        return pygame.Vector2((world[0]-self.view.x)*1280/self.view.width,
                              (world[1]-self.view.y)*720/self.view.height)

    def present(self,world,surface):
        if self.view.size==(1280,720): surface.blit(world,(0,0))
        # A imagem-base e a escala final da janela usam filtro suave. O pequeno
        # zoom interno usa escala direta para não refiltrar 921 mil pixels.
        else: pygame.transform.scale(world.subsurface(self.view),(1280,720),surface)
