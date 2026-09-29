"""Loop, dispositivos e troca de cenas. Regras pertencem aos respectivos modulos."""
import pygame
from scripts.config import WIDTH, HEIGHT, FPS, FIXED_DT
from scripts.settings import Settings
from scripts.viewport import Viewport
from scripts.audio.manager import AudioManager


class Game:
    def __init__(self,initial_scene="menu",audio_enabled=True):
        from scripts.ui.style import font
        font.cache_clear()
        pygame.display.init()
        pygame.font.init()
        self.settings=Settings()
        self.window=pygame.display.set_mode((WIDTH,HEIGHT),pygame.RESIZABLE)
        self.screen=pygame.Surface((WIDTH,HEIGHT)).convert()
        self.viewport=Viewport((WIDTH,HEIGHT))
        pygame.display.set_caption("ARMS RACE - Ringue Neon")
        self.clock=pygame.time.Clock()
        self.audio=AudioManager(self.settings,audio_enabled)
        self.running=True
        self.scene=None
        self.intro_seen=False
        self.debug=False
        self.arena_art=None
        if initial_scene=="ringue": self.start_match()
        else: self.show_menu()

    def change_scene(self,scene):
        self.scene=scene

    def show_menu(self):
        from scripts.scenes.menu import Menu
        self.change_scene(Menu(self))
        self.audio.set_music("menu")

    def start_match(self):
        from scripts.scenes.ringue_neon import RingueNeon
        self.change_scene(RingueNeon(self))
        self.audio.set_music("ringue")

    def apply_display(self):
        flags=pygame.FULLSCREEN if self.settings.fullscreen else pygame.RESIZABLE
        try:
            self.window=pygame.display.set_mode(self.settings.resolution,flags)
        except pygame.error:
            self.settings.fullscreen=False
            self.settings.resolution=(1280,720)
            self.window=pygame.display.set_mode((1280,720),pygame.RESIZABLE)
        self.viewport.resize(self.window.get_size())

    def process_event(self,event):
        from scripts.scenes.ringue_neon import RingueNeon
        from scripts.scenes.pausa import Pausa
        if event.type==pygame.QUIT: self.running=False
        elif event.type==pygame.VIDEORESIZE and not self.settings.fullscreen:
            self.settings.resolution=(max(640,event.w),max(360,event.h))
            self.apply_display()
        elif event.type==pygame.KEYDOWN and event.key==pygame.K_F3:
            self.debug=not self.debug
        elif event.type==pygame.WINDOWFOCUSLOST:
            if isinstance(self.scene,RingueNeon) and not self.scene.result:
                self.scene.player.release_jump()
                self.change_scene(Pausa(self,self.scene))
                self.audio.play("pause")
        else:
            if event.type==pygame.KEYDOWN and not isinstance(self.scene,RingueNeon):
                sound="confirm" if event.key in (pygame.K_RETURN,pygame.K_KP_ENTER) else "back" if event.key==pygame.K_ESCAPE else "select"
                self.audio.play(sound,variation=False)
            self.scene.handle_event(event)

    def run(self,max_frames=0):
        accumulator=0.0
        frames=0
        try:
            while self.running:
                # Temporização mais precisa evita intervalos irregulares do
                # sleep do Windows. A simulação continua usando passo fixo.
                elapsed=min(self.clock.tick_busy_loop(FPS)/1000,.1)
                accumulator+=elapsed
                for event in pygame.event.get(): self.process_event(event)
                if not self.running: break
                self.audio.update(elapsed)
                while accumulator>=FIXED_DT:
                    self.scene.update(FIXED_DT)
                    accumulator-=FIXED_DT
                self.scene.draw(self.screen)
                self.viewport.present(self.screen,self.window)
                pygame.display.flip()
                frames+=1
                if max_frames and frames>=max_frames: self.running=False
        finally:
            self.audio.stop()
            from scripts.ui.style import font
            font.cache_clear()
            pygame.quit()
