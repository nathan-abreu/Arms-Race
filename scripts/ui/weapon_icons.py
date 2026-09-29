"""Ícones vetoriais nítidos, desenhados na resolução final de 52×42."""
from functools import lru_cache
import pygame

INK=(5,12,30)
ICE=(182,200,255)


@lru_cache(maxsize=12)
def weapon_icon(kind,color=ICE):
    s=pygame.Surface((52,42),pygame.SRCALPHA)
    def geometry(c,dx,dy):
        def poly(points): pygame.draw.polygon(s,c,[(x+dx,y+dy) for x,y in points])
        if kind=='panela':
            pygame.draw.ellipse(s,c,(3+dx,11+dy,34,22),4)
            poly([(33,19),(49,24),(47,29),(32,25)])
            pygame.draw.arc(s,c,(7+dx,14+dy,26,14),.1,2.7,2)
        elif kind=='machado':
            poly([(9,37),(13,40),(37,10),(33,7)])
            poly([(23,8),(30,2),(44,8),(49,8),(47,21),(40,23),(33,15)])
        elif kind=='rifle':
            poly([(3,20),(12,16),(30,13),(32,10),(40,11),(43,14),(50,13),(51,17),(43,20),(25,24),(22,28),(18,27),(14,25),(5,29)])
            poly([(28,23),(35,21),(37,33),(32,34)])
            poly([(18,26),(22,27),(20,33),(17,33)])
            pygame.draw.line(s,c,(15+dx,13+dy),(25+dx,10+dy),2)
        elif kind=='lancador':
            poly([(3,17),(41,5),(48,8),(49,24),(10,36),(4,33)])
            poly([(23,31),(29,29),(32,38),(25,40)])
            pygame.draw.line(s,INK,(11+dx,16+dy),(15+dx,33+dy),2)
            pygame.draw.line(s,INK,(40+dx,7+dy),(44+dx,25+dy),2)
        else:
            poly([(14,13),(34,13),(38,27),(28,34),(14,27)])
    geometry(INK,1,2)
    geometry(tuple(color),0,0)
    return s
