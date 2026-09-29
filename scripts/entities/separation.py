"""Separação previsível dos corpos; não bloqueia saltos por cima do adversário."""
import math
from scripts.balance import COMBAT


def separate_fighters(a, b, dt):
    if not a.alive or not b.alive:
        return
    atop,abottom,ar=a.body_capsule
    btop,bbottom,br=b.body_capsule
    vertical_gap=max(0,atop.y-bbottom.y,btop.y-abottom.y)
    if vertical_gap>=ar+br:
        return
    spacing=COMBAT.body_spacing*math.sqrt(1-(vertical_gap/(ar+br))**2)
    overlap=spacing-abs(b.pos.x-a.pos.x)
    if overlap<=0:
        return
    direction=1 if b.pos.x>=a.pos.x else -1
    # Resolve quase tudo no primeiro passo; o resto converge suavemente.
    correction=overlap*(1-math.exp(-90*dt))*.5
    a.pos.x-=direction*correction
    b.pos.x+=direction*correction
    if a.stun<=0 and a.velocity.x*direction>0: a.velocity.x*=.4
    if b.stun<=0 and b.velocity.x*direction<0: b.velocity.x*=.4
