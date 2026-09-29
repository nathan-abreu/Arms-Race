"""Ritmo da arena sem acoplar cronômetros ao renderizador."""
import math


class MatchFlow:
    def __init__(self,enabled=True,can_skip=False):
        self.phase="intro" if enabled else "fight"
        self.elapsed=0.0
        self.can_skip=can_skip
        self.last_count=None
        self.result_age=0.0
        self.low_announced=False

    def update(self,dt,audio):
        self.elapsed+=dt
        if self.phase=="intro":
            if self.elapsed>=.65:
                self.phase="countdown"
                self.elapsed=0
        elif self.phase=="countdown":
            count=max(0,3-int(self.elapsed))
            if count!=self.last_count:
                audio.play("countdown" if count else "confirm",variation=False)
                self.last_count=count
            if self.elapsed>=3.35:
                self.phase="fight"
                self.elapsed=0
        elif self.phase in ("finish","result"):
            self.result_age+=dt
            if self.result_age>=.455:
                self.phase="result"

    def skip(self):
        if self.can_skip and self.phase in ("intro","countdown"):
            self.phase="fight"
            self.elapsed=0
            return True
        return False

    def finish(self):
        self.phase="finish"
        self.result_age=0

    @property
    def label(self):
        if self.phase=="intro": return "FASE 1 — RINGUE NEON"
        if self.phase=="countdown": return str(3-int(self.elapsed)) if self.elapsed<3 else "LUTE!"
        return ""
