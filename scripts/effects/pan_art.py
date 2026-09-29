"""Frigideira independente: pivô no centro do bojo e rotação cacheada."""
from functools import lru_cache
import pygame

GOLD=(255,214,44)
PAN_PIVOT=(56,40)


@lru_cache(maxsize=8)
def pan_surface(color=GOLD):
    s=pygame.Surface((112,80),pygame.SRCALPHA)
    # Bojo de 56×36 + cabo curto: silhueta total de aproximadamente 76×38.
    for spread,alpha in ((8,10),(5,22),(3,40)):
        pygame.draw.ellipse(s,(*color,alpha),(28-spread,22-spread,56+spread*2,36+spread*2))
        pygame.draw.line(s,(*color,alpha),(79,40),(102,45),7+spread)
    pygame.draw.polygon(s,color,[(80,36),(104,41),(102,49),(80,44)])
    pygame.draw.line(s,(12,16,28),(86,41),(99,44),3)
    pygame.draw.ellipse(s,(8,12,24),(28,22,56,36))
    pygame.draw.ellipse(s,color,(28,22,56,36),5)
    pygame.draw.ellipse(s,(35,31,20),(33,26,46,22))
    pygame.draw.ellipse(s,(9,13,24),(35,27,43,18))
    pygame.draw.arc(s,(255,248,160),(32,24,48,24),.12,2.9,2)
    pygame.draw.arc(s,(148,111,24),(33,29,47,26),3.3,5.8,2)
    return s


@lru_cache(maxsize=360)
def rotated_pan(angle,scale,color,squash):
    base=pan_surface(color)
    if squash!=1:
        # Redimensiona simetricamente: centro do bojo continua no pivô.
        size=(round(base.get_width()*(2-squash)),round(base.get_height()*squash))
        base=pygame.transform.smoothscale(base,size)
    return pygame.transform.rotozoom(base,angle,scale)


def pan(surface,center,angle=0,scale=1,color=GOLD,squash=1):
    sprite=rotated_pan(round(angle/4)*4,round(scale,2),tuple(color),round(squash,1))
    rect=sprite.get_rect(center=(round(center[0]),round(center[1])))
    surface.blit(sprite,rect)
    return rect
