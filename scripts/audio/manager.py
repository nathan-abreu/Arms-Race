"""Mixer central com fallback silencioso, crossfade e limite de vozes."""
import random
import math
import pygame
from scripts.audio.synth import RATE, MUSIC, UI, EFFECTS, pcm, path_for
from scripts.audio.layers import CUES, Cue, pcm_cue, cue_path

GROUPS={'interface':(3,4),'personagem':(5,6,7),'armas':(8,9),
        'impactos':(10,11,12),'ambiente':(13,14),'plateia':(15,16)}
PITCHES=(.97,1.0,1.03)


class AudioManager:
    def __init__(self,settings,enabled=True):
        self.settings=settings
        self.enabled=False
        self.sounds={}
        self.music_name=None
        self.intense=False
        self.music_levels={name:0.0 for name in MUSIC}
        self.rng=random.Random()
        self.last_sound={}
        self.time=0.0
        self.music_starts=0
        self.duck_time=0.0
        self.duck_gain=1.0
        self.active={}
        self.voice_limit=17
        self.duck_floor=10**(-4/20)
        if enabled:
            try:
                if not pygame.mixer.get_init():
                    pygame.mixer.init(RATE,-16,2,512)
                pygame.mixer.set_num_channels(self.voice_limit)
                pygame.mixer.set_reserved(self.voice_limit)
                self.enabled=True
            except (pygame.error,OSError):
                pass
        if self.enabled:
            # Síntese e decodificação acontecem no carregamento, nunca no golpe.
            for name in CUES:
                for pitch in PITCHES: self.load(name,pitch)

    def load(self,name,variant=1.0):
        if not self.enabled:
            return None
        key=(name,variant)
        if key not in self.sounds:
            try:
                path=path_for(name) if name in MUSIC else cue_path(name)
                source=pcm if name in MUSIC else pcm_cue
                self.sounds[key]=pygame.mixer.Sound(str(path)) if variant==1 and path.exists() else pygame.mixer.Sound(buffer=source(name,variant))
            except (pygame.error,OSError,ValueError):
                self.sounds[key]=None
        return self.sounds[key]

    @staticmethod
    def stereo_pan(x=None):
        if x is None: return 2**-.5,2**-.5
        p=max(-.85,min(.85,(x-640)/640))
        return math.sqrt((1-p)/2),math.sqrt((1+p)/2)

    def register_layers(self,name,layers,group='impactos'):
        if group not in GROUPS: raise ValueError('Grupo de áudio desconhecido')
        CUES[name]=Cue(group,tuple(layers))
        pcm_cue.cache_clear()
        for pitch in PITCHES:
            self.sounds.pop((name,pitch),None)
            self.load(name,pitch)

    def _mix_effects(self):
        if not self.enabled: return
        self.active={i:entry for i,entry in self.active.items() if pygame.mixer.Channel(i).get_busy()}
        # Orçamento de pico total dos efeitos; reserva margem para a música.
        gains={i:entry[1]*self.settings.master*self.settings.effects for i,entry in self.active.items()}
        peak=sum(gains.values())*.72
        headroom=min(1,.70/max(.001,peak))
        for i,(_,_,x) in self.active.items():
            left,right=self.stereo_pan(x)
            gain=0 if self.settings.mute else gains[i]*headroom
            pygame.mixer.Channel(i).set_volume(gain*left,gain*right)

    def play(self,name,volume=1,variation=True,x=None):
        if not self.enabled or self.settings.mute:
            return
        if self.time-self.last_sound.get(name,-100)<.045:
            return
        self.last_sound[name]=self.time
        self._mix_effects()
        recipe=CUES.get(name,CUES['hit'])
        if sum(v[0]==name for v in self.active.values())>=recipe.copies:
            return
        variant=self.rng.choice(PITCHES) if variation else 1.0
        sound=self.load(name,variant)
        if sound is None:
            return
        index=next((i for i in GROUPS[recipe.group] if not pygame.mixer.Channel(i).get_busy()),None)
        if index is not None:
            channel=pygame.mixer.Channel(index)
            gain=max(0,min(1,volume))*(self.rng.uniform(.94,1) if variation else 1)
            channel.set_volume(0)
            channel.play(sound)
            self.active[index]=(name,gain,x)
            self._mix_effects()
            return index

    def set_music(self,name,intense=False):
        if name not in ("menu","ringue"):
            return
        self.intense=intense
        if self.music_name==name:
            return
        self.music_name=name
        if not self.enabled:
            return
        tracks=("ringue","critical") if name=="ringue" else ("menu",)
        for track in tracks:
            channel=pygame.mixer.Channel(MUSIC.index(track))
            sound=self.load(track)
            if sound and not channel.get_busy():
                channel.set_volume(0)
                channel.play(sound,loops=-1)
                self.music_starts+=1

    def update(self,dt):
        self.time+=dt
        self.duck_time=max(0,self.duck_time-dt)
        target_duck=self.duck_floor if self.duck_time>0 else 1.0
        self.duck_gain+=max(-dt*18,min(dt*4,target_duck-self.duck_gain))
        if not self.enabled:
            return
        for name in MUSIC:
            target=1.0 if name==self.music_name or (name=="critical" and self.music_name=="ringue" and self.intense) else 0.0
            v=self.music_levels[name]
            v+=max(-dt*2,min(dt*2,target-v))
            self.music_levels[name]=v
        # O orçamento de .30 vale para a soma das trilhas no crossfade/crítico.
        gain=0 if self.settings.mute else min(.30,self.settings.master*self.settings.music*.65)
        gain/=max(1,sum(self.music_levels.values()))
        for i,name in enumerate(MUSIC):
            v=self.music_levels[name]
            pygame.mixer.Channel(i).set_volume(v*gain*self.duck_gain)
        self._mix_effects()

    def stop(self):
        if self.enabled and pygame.mixer.get_init():
            pygame.mixer.stop()

    def duck(self,duration=.15):
        self.duck_time=max(self.duck_time,duration)

    def end_match(self):
        self.music_name=None
        self.intense=False
        self.duck(.18)
