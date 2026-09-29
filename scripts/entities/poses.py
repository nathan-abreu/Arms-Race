"""Silhuetas limpas; pés em apoio percorrem distância, não um relógio."""
import math
import pygame
from scripts.combat.weapon import FISTS
from scripts.arena_layout import SHOULDER_HEIGHT


def elbow_between(shoulder, hand, bend):
    delta=hand-shoulder
    length=max(1,delta.length())
    normal=pygame.Vector2(-delta.y,delta.x)/length
    height=math.sqrt(max(0,35**2-(length*.5)**2))
    return (shoulder+hand)*.5+normal*height*bend


def pose(f):
    t,d=f.animation_time,f.facing
    state=f.movement_state
    compression=11*min(1,f.landing_time/.12)
    lean=d*9+max(-9,min(9,f.velocity.x*.018))
    if state=="freando": lean=-lean*.65
    if state=="dano": lean=max(-15,min(15,-f.velocity.x*.035))
    if f.start_run>0: lean+=d*3
    if f.combo_index==3:
        if f.windup>0: lean-=d*7
        elif f.attack_time>0: lean+=d*6
    aim=f.aim if f.aim_locked else pygame.Vector2(d,0)
    downward=(f.attack_direction if f.attack_time>0 else aim).y>.55
    # Abre espaço ao lado do tronco ao mirar para baixo, sem cruzar o corpo.
    if downward: lean-=d*17
    bob=math.sin(t*4)*.7 if state=="parado" else 0
    hip=pygame.Vector2(-d*4,-63+compression)
    if downward: hip.x-=d*12
    shoulder=pygame.Vector2(lean,-SHOULDER_HEIGHT+compression+bob)
    head=shoulder+pygame.Vector2(d*4,-30)
    points=dict(hip=hip,shoulder=shoulder,head=head,
                foot_l=pygame.Vector2(-23,-4),foot_r=pygame.Vector2(22,-4))
    if state=="correndo":
        travel=1 if f.velocity.x>=0 else -1
        for side,phase_offset in (("l",0),("r",52)):
            phase=(f.stride_distance+phase_offset)%104
            x=26-phase if phase<52 else -26+(phase-52)
            lift=0 if phase<52 else math.sin((phase-52)/52*math.pi)*21
            points['foot_'+side]=pygame.Vector2(x*travel,-4-lift)
    elif state=="pulando":
        points.update(foot_l=pygame.Vector2(-24,-23),foot_r=pygame.Vector2(27,-8))
    elif state=="caindo":
        points.update(foot_l=pygame.Vector2(-21,-7),foot_r=pygame.Vector2(23,-17))
    elif state=="freando":
        points.update(foot_l=pygame.Vector2(-29,-4),foot_r=pygame.Vector2(31,-4))
    if f.grounded and f.combo_index==3 and f.attack_time>0:
        points['foot_r'].x+=d*7
    for side in ('l','r'):
        foot=points['foot_'+side]
        points['knee_'+side]=(hip+foot)*.5+pygame.Vector2(d*8,-3)
    aim=f.aim if f.aim_locked else pygame.Vector2(d,0)
    back_shoulder=shoulder+(-d*7,3)
    guard=shoulder+aim*34+pygame.Vector2(0,-2)
    back_hand=back_shoulder+aim*26+pygame.Vector2(0,8)
    if state=='correndo' and not (f.windup>0 or f.attack_time>0 or f.recovery>0):
        swing=math.sin(f.stride_distance/104*math.tau)*12
        guard+=pygame.Vector2(-d*swing,abs(swing)*.35)
        back_hand+=pygame.Vector2(d*swing,0)
    if downward:
        guard.x+=d*28
        back_hand.x+=d*23
    hand=guard
    if f.windup>0:
        hand=shoulder+f.attack_direction.rotate(-35*d)*26
    elif f.attack_time>0:
        hand=pygame.Vector2(0,-SHOULDER_HEIGHT)+f.swing_vector()*(f.strike_reach()-(22 if f.attack_weapon is not FISTS else 0))
        shoulder+=f.attack_direction*3
        points['shoulder']=shoulder
    elif f.recovery>0:
        hand=shoulder+aim*(40+9*min(1,f.recovery/max(.01,f.attack_recovery)))
    if f.queued_click>0: hand-=aim*4
    points.update(hand=hand,back_hand=back_hand,back_shoulder=back_shoulder)
    bend=-d if downward else d
    points['elbow']=elbow_between(shoulder,hand,bend)
    points['back_elbow']=elbow_between(back_shoulder,back_hand,bend)
    if f.punch_arm==1 and (f.windup>0 or f.attack_time>0 or f.recovery>0):
        points['back_hand'],points['hand']=points['hand'],guard
        points['back_elbow']=elbow_between(back_shoulder,points['back_hand'],bend)
        points['elbow']=elbow_between(shoulder,points['hand'],bend)
    if f.celebrating:
        points['hand']=shoulder+pygame.Vector2(d*28,-46+math.sin(t*7)*5)
        points['elbow']=elbow_between(shoulder,points['hand'],d)
    if state=="dano":
        points['head']+=pygame.Vector2(-d*8,3)
        points['hand']=shoulder+pygame.Vector2(-d*5,25)
        points['elbow']=elbow_between(shoulder,points['hand'],d)
    if not f.alive:
        points={k:pygame.Vector2(v.y*.78*d,v.x*.30-27) for k,v in points.items()}
    return points
