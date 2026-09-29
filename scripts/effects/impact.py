"""Ondas, flash e fila de eventos consumida pelo sistema de feedback."""
from collections import deque
import pygame


class ImpactEffects:
    def __init__(self):
        self.waves = []
        self.audio_events = deque(maxlen=24)
        self.layer = pygame.Surface((1280,720),pygame.SRCALPHA)
        self.clear_rect = pygame.Rect(0,0,1280,720)

    def emit(self, position, color, strength=1, sound="metal_impact"):
        self.waves.append([pygame.Vector2(position),0.0,color,strength])
        self.waves=self.waves[-16:]
        if sound:
            self.audio_events.append((sound,tuple(position),strength))

    def drain_audio_events(self):
        """Entrega os eventos ao Feedback/AudioManager sem duplicar reprodução."""
        result=list(self.audio_events)
        self.audio_events.clear()
        return result

    def update(self,dt,fighters,base):
        for wave in self.waves:
            wave[1]+=dt
        self.waves=[w for w in self.waves if w[1]<.4]

    def draw(self,surface):
        if not self.waves:
            return
        self.layer.fill((0,0,0,0),self.clear_rect)
        bounds = []
        for pos,age,color,strength in self.waves:
            radius=10+age*220*strength
            extent=max(radius,34*strength)
            bounds.append(pygame.Rect(pos.x-extent-4,pos.y-extent-4,extent*2+8,extent*2+8))
            alpha=int(220*(1-age/.4))
            pygame.draw.ellipse(self.layer,(*color,alpha),(pos.x-radius,pos.y-radius*.28,radius*2,radius*.56),3)
            if age<.045:
                pygame.draw.circle(self.layer,(*color,int(105*(1-age/.045))),pos,max(2,int(16*strength)))
        region=bounds[0].unionall(bounds[1:]).clip(surface.get_rect())
        self.clear_rect=region
        surface.blit(self.layer,region.topleft,region,special_flags=pygame.BLEND_ALPHA_SDL2)

