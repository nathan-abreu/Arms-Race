"""Preferências da sessão. Sem salvar progresso nem usar caminhos externos."""
from dataclasses import dataclass


@dataclass
class Settings:
    master: float = .75
    music: float = .45
    effects: float = .8
    mute: bool = False
    shake: float = .65
    particles: int = 1
    fullscreen: bool = False
    resolution: tuple = (1280, 720)

    def set_volume(self, name, value):
        if name not in ("master", "music", "effects"):
            raise ValueError("Canal de volume desconhecido")
        setattr(self, name, max(0.0, min(1.0, float(value))))

    @property
    def particle_limit(self):
        return (65, 125, 180)[self.particles]
