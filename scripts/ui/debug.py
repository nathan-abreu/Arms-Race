import pygame
from scripts.ui.style import text,panel


class DebugOverlay:
    def draw_world(self,surface,match):
        floor=match.platforms[0]
        pygame.draw.line(surface,(100,255,140),(floor.left,floor.top),(floor.right,floor.top),2)
        for x in (floor.left,floor.right):
            pygame.draw.line(surface,(240,220,80),(x,120),(x,570),1)
        for f in match.fighters:
            top,bottom,radius=f.body_capsule
            pygame.draw.line(surface,(110,160,250),top,bottom,1)
            pygame.draw.circle(surface,(110,160,250),top,radius,1)
            pygame.draw.circle(surface,(110,160,250),bottom,radius,1)
            pygame.draw.circle(surface,(255,255,255),f.pos,4,1)
            if f.art:
                for side in ('l','r'):
                    sole=f.pos+f.art.points['foot_'+side]+(0,4)
                    pygame.draw.line(surface,(255,255,255),sole+(-9,0),sole+(9,0),2)
            pygame.draw.rect(surface,(60,255,100),f.rect,1)
            if f.attack_time>0:
                pygame.draw.rect(surface,(255,240,40),f.attack_rect,1)
                a,b=f.attack_segment()
                pygame.draw.line(surface,(255,255,255),a,b,2)
        p=match.player.aim_point
        pygame.draw.circle(surface,(255,255,255),p,6,1)
        for x in match.level["weapon_drop_points"]:
            pygame.draw.rect(surface,(230,180,40),(x-30,match.platforms[0].top-8,60,16),1)

    def draw(self,surface,match,fps):
        p=match.player
        panel(surface,(16,103,360,151),(70,220,130))
        lines=(f"F3  |  {fps:.1f} FPS  |  {match.flow.phase}",
               f"Pos: {p.pos.x:.1f}, {p.pos.y:.1f}  Vel: {p.velocity.x:.1f}, {p.velocity.y:.1f}",
               f"Estado: {p.movement_state} / {p.attack_phase}",
               f"Grounded: {p.grounded}  Dir: {p.facing}  CD: {p.cooldown:.2f}",
               f"CPU: {match.enemy.state}",
               f"Mira: {p.aim_point.x:.0f}, {p.aim_point.y:.0f}")
        for i,label in enumerate(lines): text(surface,label,(28,115+i*22),20)
