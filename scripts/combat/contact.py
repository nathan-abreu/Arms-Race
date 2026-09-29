"""Contato entre volumes de luva/arma e os membros realmente desenhados."""
import pygame


def closest(point, a, b):
    delta=b-a
    t=max(0,min(1,(point-a).dot(delta)/delta.length_squared())) if delta.length_squared() else 0
    return a+delta*t


def capsule_contact(start,end,radius,capsules):
    for a,b,body_radius in capsules:
        # Segmentos curtos: projeções alternadas convergem, incluindo cruzamento.
        u=closest(a,start,end)
        for _ in range(3):
            v=closest(u,a,b)
            u=closest(v,start,end)
        delta=u-v
        if delta.length_squared()<=(radius+body_radius)**2:
            if delta.length_squared()<=body_radius**2: return u
            normal=delta.normalize() if delta.length_squared()>0 else pygame.Vector2(1,0)
            return v+normal*body_radius
    return None
