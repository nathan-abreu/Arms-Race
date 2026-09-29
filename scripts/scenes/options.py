"""Controles e configurações acessíveis pela pausa."""
import pygame
from scripts.scenes.base import Scene
from scripts.ui.style import panel,text,shade
from scripts.config import CYAN,WHITE,MUTED


CONTROLS=("A / D — mover", "Espaço — pular (segure para saltar mais alto)",
          "Mouse — mirar   |   Botão esquerdo — atacar", "Q / E ou roda — selecionar item",
          "X — descartar   |   Esc — pausar/continuar", "R — reiniciar após resultado   |   F3 — diagnóstico")


class Controls(Scene):
    def __init__(self,game,parent):
        super().__init__(game)
        self.parent=parent

    def handle_event(self,event):
        if event.type==pygame.KEYDOWN and event.key in (pygame.K_ESCAPE,pygame.K_RETURN):
            self.game.change_scene(self.parent)

    def draw(self,surface):
        self.parent.draw(surface)
        shade(surface)
        panel(surface,(250,163,780,393),CYAN)
        text(surface,"CONTROLES",(640,201),42,CYAN,True,True)
        for i,line in enumerate(CONTROLS): text(surface,line,(288,255+i*38),26)
        text(surface,"ENTER / ESC  voltar",(640,527),23,MUTED,True)


class Options(Controls):
    RESOLUTIONS=((960,540),(1280,720),(1600,900),(1920,1080))

    def __init__(self,game,parent):
        super().__init__(game,parent)
        self.selected=0

    def adjust(self,direction):
        s=self.game.settings
        i=self.selected
        if i<3: s.set_volume(("master","music","effects")[i],getattr(s,("master","music","effects")[i])+direction*.1)
        elif i==3: s.mute=not s.mute
        elif i==4: s.shake=round(max(0,min(1,s.shake+direction*.25)),2)
        elif i==5: s.particles=(s.particles+direction)%3
        elif i==6:
            s.fullscreen=not s.fullscreen
            self.game.apply_display()
        elif i==7:
            current=self.RESOLUTIONS.index(s.resolution) if s.resolution in self.RESOLUTIONS else 1
            s.resolution=self.RESOLUTIONS[(current+direction)%len(self.RESOLUTIONS)]
            self.game.apply_display()
        self.game.audio.update(0)

    def handle_event(self,event):
        if event.type!=pygame.KEYDOWN: return
        if event.key==pygame.K_ESCAPE:
            self.game.change_scene(self.parent)
        elif event.key in (pygame.K_UP,pygame.K_w): self.selected=(self.selected-1)%9
        elif event.key in (pygame.K_DOWN,pygame.K_s): self.selected=(self.selected+1)%9
        elif event.key in (pygame.K_LEFT,pygame.K_RIGHT): self.adjust(-1 if event.key==pygame.K_LEFT else 1)
        elif event.key==pygame.K_RETURN:
            if self.selected==8: self.game.change_scene(self.parent)
            else: self.adjust(1)

    def draw(self,surface):
        self.parent.draw(surface)
        shade(surface)
        panel(surface,(305,118,670,507),CYAN)
        text(surface,"CONFIGURAÇÕES",(640,154),42,CYAN,True,True)
        s=self.game.settings
        labels=(f"Volume geral       {s.master:.0%}",f"Música                  {s.music:.0%}",
                f"Efeitos                   {s.effects:.0%}",f"Mudo                     {'Sim' if s.mute else 'Não'}",
                f"Tremor                   {s.shake:.0%}",f"Visual / partículas    {('Baixo','Médio','Alto')[s.particles]}",
                f"Tela cheia              {'Sim' if s.fullscreen else 'Não'}",f"Resolução              {s.resolution[0]} × {s.resolution[1]}","VOLTAR")
        for i,label in enumerate(labels):
            if i==self.selected: pygame.draw.rect(surface,(15,43,62),(335,191+i*42,610,37),border_radius=4)
            text(surface,label,(354,199+i*42),27,CYAN if i==self.selected else WHITE)
        text(surface,"Setas: selecionar/ajustar   Enter: confirmar   Esc: voltar",(640,603),21,MUTED,True)
