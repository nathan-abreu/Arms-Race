"""Arte exclusiva da Fase 1. O menu conserva o cenário anterior."""
import math
import random
import pygame
from scripts.effects.neon import BLUE, CYAN, PINK, PURPLE, glow_line, halo
from scripts.ui.style import text


class CompetitiveArena:
    def __init__(self, platforms):
        self.platforms = platforms
        self.background = pygame.Surface((1280, 720)).convert()
        self.ring = pygame.Surface((1280, 720), pygame.SRCALPHA)
        self.foreground = pygame.Surface((1280, 720), pygame.SRCALPHA)
        self.lights = pygame.Surface((1280, 720), pygame.SRCALPHA)
        self.sticks = []
        self.reaction = 0.0
        self._build()
        # Base opaca com iluminação ampla já composta; só os núcleos pulsam.
        self.stage = self.background.copy()
        self.beams = []
        self.lights.fill((0,0,0,0))
        for x,c,phase in ((190,CYAN,0),(350,BLUE,1),(930,PINK,2),(1090,PURPLE,3)):
            drift=math.sin(phase)*65
            for width,alpha in ((130,18),(85,26),(40,43)):
                pygame.draw.polygon(self.lights,(*c,alpha),[(x-5,105),(x+5,105),(x+drift+width,535),(x+drift-width,535)])
            variants=[]
            for level in range(8):
                # Brilho aditivo RGB evita multiplicar dois canais alpha
                # para centenas de milhares de pixels a cada quadro.
                beam=pygame.Surface((150,440)).convert()
                beam.fill((0,0,0))
                color=tuple(round(v*(level+1)*.012) for v in c)
                pygame.draw.polygon(beam,color,[(70,0),(80,0),(140,430),(10,430)])
                variants.append(beam)
            self.beams.append((x,c,phase,variants))
        self.stage.blit(self.lights,(0,0))
        self.stage.blit(self.ring,(0,0))

    def _crowd(self, s, baseline, size, seed, foreground=False):
        rng = random.Random(seed)
        for x in range(-20, 1300, int(size * 1.65)):
            y = baseline + rng.randrange(-12, 13)
            color = (3, 5, 20) if foreground else rng.choice(((7,10,33),(10,16,53),(15,19,66)))
            pygame.draw.circle(s, color, (x, y - size * 3), size)
            pygame.draw.polygon(s, color, [(x-size,y-size*2),(x+size,y-size*2),(x+size*2,y+size*2),(x-size*2,y+size*2)])
            if rng.random() < .7:
                tip = (x + rng.choice((-1, 1)) * size * 2, y - size * 5)
                pygame.draw.line(s, color, (x, y-size), tip, max(3, size // 2))
                c = rng.choice((CYAN, PINK, PURPLE))
                end = (tip[0] + 5, tip[1] - size * 2)
                glow_line(s, c, tip, end, 3 if foreground else 2)
                if not foreground:
                    self.sticks.append((tip, end, c, rng.random() * 6))

    def _screen(self, s, rect, color, facing):
        r = pygame.Rect(rect)
        pygame.draw.rect(s, (2, 9, 37), r)
        for x in range(r.x+6,r.right-4,5):
            for y in range(r.y+6,r.bottom-4,6):
                pygame.draw.circle(s, (15, 37, 91), (x,y), 1)
        for a,b in ((r.topleft,r.topright),(r.topright,r.bottomright),(r.bottomright,r.bottomleft),(r.bottomleft,r.topleft)):
            glow_line(s, BLUE, a,b,3)
        # Silhueta própria, desenhada por segmentos articulados.
        cx, cy = r.centerx, r.centery + 20
        def p(x,y): return (cx+x*facing,cy+y)
        pygame.draw.polygon(s,color,[p(-10,-54),p(14,-46),p(8,-22),p(-17,-29)])
        pygame.draw.line(s,color,p(-7,-17),p(-18,24),18)
        for pts in ([p(-17,21),p(-43,47),p(-57,62)], [p(-13,23),p(15,44),p(28,61)],
                    [p(-3,-11),p(21,12),p(38,-4)], [p(-12,-9),p(-26,13),p(-3,20)]):
            pygame.draw.lines(s,color,False,pts,10)
        text(s,"ARMS RACE",(r.centerx,r.bottom-12),16,color,True)

    def _build(self):
        s = self.background
        for y in range(720):
            pygame.draw.line(s,(3+int(y/100),5+int(y/65),24+int(35*math.sin(y/720*math.pi))), (0,y),(1280,y))
        for x in (110,310,490,790,970,1170):
            pygame.draw.rect(s,(9,15,45),(x-12,86,24,423))
            for y in range(90,500,32):
                pygame.draw.line(s,(32,39,88),(x-12,y),(x+12,y+32),3)
        for y in (105,133):
            pygame.draw.lines(s,(25,36,84),False,[(0,y-40),(310,y),(970,y),(1280,y-40)],5)
        for x in range(0,1280,32):
            pygame.draw.line(s,(27,38,78),(x,105),(x+24,133),3)
        for y in (255,345,432):
            self._crowd(s,y,6 if y<300 else 8,y)
            pygame.draw.lines(s,(27,30,89),False,[(0,y-20),(320,y+15),(960,y+15),(1280,y-20)],13)
            pygame.draw.lines(s,(62,37,160),False,[(0,y-25),(320,y+10),(960,y+10),(1280,y-25)],2)
        self._screen(s,(58,150,245,176),CYAN,1)
        self._screen(s,(977,150,245,176),PINK,-1)
        pygame.draw.rect(s,(3,14,51),(493,169,294,131))
        for a,b in (((493,169),(787,169)),((493,169),(493,300)),((787,169),(787,300)),((493,300),(787,300))):
            glow_line(s,BLUE,a,b,4)
        for x,d in ((500,1),(780,-1)):
            glow_line(s,BLUE,(x,179),(x+d*62,232),6)
            glow_line(s,BLUE,(x,290),(x+d*48,248),5)
        trophy = [(610,195),(670,195),(666,233),(650,246),(630,246),(614,233),(610,195)]
        pygame.draw.lines(s,CYAN,False,trophy,4)
        pygame.draw.lines(s,BLUE,False,[(612,204),(591,204),(596,229),(620,236)],4)
        pygame.draw.lines(s,BLUE,False,[(668,204),(689,204),(684,229),(660,236)],4)
        glow_line(s,CYAN,(640,245),(640,268),3)
        glow_line(s,CYAN,(621,272),(659,272),4)
        self._crowd(s,492,9,233)
        for x,c in ((30,PURPLE),(330,CYAN),(950,PINK),(1250,PURPLE)):
            for yy in (98,115):
                glow_line(s,c,(x,yy),(x+20,yy),5)
        s.blit(halo(BLUE,230),(35,110))
        s.blit(halo(PURPLE,230),(930,100))
        self._build_ring()
        # Primeiro plano abaixo do piso; desfoque leve por redução de resolução.
        self._crowd(self.foreground,736,19,848,True)
        small = pygame.transform.smoothscale(self.foreground,(640,360))
        self.foreground = pygame.transform.smoothscale(small,(1280,720))
        self.ring = self.ring.convert_alpha()
        self.foreground = self.foreground.convert_alpha()
        self.ring.set_alpha(255, pygame.RLEACCEL)
        self.foreground.set_alpha(255, pygame.RLEACCEL)

    def _build_ring(self):
        s = self.ring
        base = self.platforms[0]
        y = base.top
        # Structure porteuse visible et croisée.
        for x in range(base.left,base.right,120):
            pygame.draw.rect(s,(10,19,51),(x,y+20,12,126))
            pygame.draw.lines(s,(37,44,99),False,[(x,y+30),(x+110,y+118),(x+110,y+30),(x,y+118)],8)
            glow_line(s,PURPLE,(x+30,y+67),(x+73,y+67),4)
        pygame.draw.polygon(s,(16,28,69),[(base.left,y-27),(base.right,y-27),(base.right+30,y+12),(base.left-30,y+12)])
        for yy in (y-22,y-10,y+4):
            glow_line(s,BLUE,(base.left-10,yy),(base.right+10,yy),1)
        for x in range(base.left,base.right,57):
            pygame.draw.line(s,(54,64,115),(x+13,y-26),(x,y+13),2)
        pygame.draw.rect(s,(4,8,26),(base.left-20,y+12,base.width+40,22))
        glow_line(s,CYAN,(base.left-20,y+12),(640,y+12),3)
        glow_line(s,PINK,(640,y+12),(base.right+20,y+12),3)
        for x in range(base.left,base.right,70):
            pygame.draw.line(s,(13,19,52),(x,y+14),(x-5,y+32),3)
        for yy,c in ((y-111,CYAN),(y-70,PURPLE),(y-30,CYAN)):
            glow_line(s,c,(base.left+12,yy),(base.right-12,yy),3)
        for x,front in ((base.left+12,False),(base.right-12,False),(base.left-36,True),(base.right+36,True)):
            top = y-158 if front else y-140
            pygame.draw.rect(s,(2,7,22),(x-14,top,28,y-top+14))
            pygame.draw.rect(s,(66,64,124),(x-14,top,28,y-top+14),2)
            glow_line(s,CYAN,(x,top+18),(x,y+2),5)
            for yy,c in ((y-111,CYAN),(y-70,PURPLE),(y-30,CYAN)):
                pygame.draw.rect(s,(6,7,25),(x-20,yy-6,40,12),border_radius=3)
                if front:
                    backx = base.left+12 if x<640 else base.right-12
                    glow_line(s,c,(x,yy),(backx,yy-5),3)
        for p in self.platforms[1:]:
            pygame.draw.rect(s,(12,19,45),p)
            glow_line(s,PURPLE,p.topleft,p.topright,3)
            for x in range(p.left+8,p.right-10,24):
                pygame.draw.line(s,(56,53,108),(x,p.y+6),(x+12,p.bottom-2),2)

    def react(self,strength):
        self.reaction=max(self.reaction,strength)

    def update(self,dt):
        self.reaction=max(0,self.reaction-dt*3)

    def draw(self,surface,time):
        surface.blit(self.stage,(0,0))
        for x,c,phase,variants in self.beams:
            level=max(0,min(7,round(2+2*math.sin(time*.9+phase)+4*self.reaction)))
            surface.blit(variants[level],(x-75,105),special_flags=pygame.BLEND_RGB_ADD)
            pygame.draw.circle(surface,c,(x,105),7)
        for a,b,c,phase in self.sticks[::4]:
            if self.reaction>.2 or math.sin(time*2+phase)>.25:
                pygame.draw.line(surface,c,a,b,2)

    def draw_foreground(self,surface):
        surface.blit(self.foreground,(0,580),(0,580,1280,140),special_flags=pygame.BLEND_ALPHA_SDL2)
