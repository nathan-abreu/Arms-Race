"""Liga eventos da luta a áudio e efeitos, sem decidir dano ou vitória."""
from scripts.effects.neon import GOLD
from scripts.balance import COMBAT


class Feedback:
    def __init__(self,audio):
        self.audio=audio
        self.step_time=0.0
        self.step_side=0
        self.motion_sounds={}

    def hit(self,match,attacker,target):
        pan=attacker.attack_weapon.name=="Panela"
        strong=attacker.strong_attack
        point=attacker.attack_contact
        color=GOLD if pan else attacker.color
        match.particles.burst(point,color,14 if pan else 18 if strong else 8,attacker.attack_direction,style='metal' if pan else 'spark')
        if pan: match.particles.burst(point,(250,252,255),4,attacker.attack_direction)
        match.impacts.emit(point,color,.70 if strong else .24,sound=None)
        match.hit_stop=COMBAT.pan_stop if pan else COMBAT.strong_stop if strong else COMBAT.light_stop
        match.camera.impulse(1.2 if pan else 1 if strong else .25,attacker.attack_direction,pixels=8 if pan else 6 if strong else 3)
        match.shake=.14 if strong else .06
        self.audio.play("metal_impact" if pan else "heavy_hit" if strong else "hit",x=point.x)
        self.audio.play('crowd',.35 if strong else .10,x=point.x)
        match.art.react(1.0 if strong else .22,side=0 if target is match.player else 1)
        if strong:
            self.audio.duck(.15)

    def tick(self,match,dt):
        self.step_time+=dt
        for f in match.fighters:
            clock=self.motion_sounds.get(f,0)+dt
            while f.events:
                event=f.events.popleft()
                gain=min(.85,max(.18,f.landed_speed/1000)) if event=='landing' else .2 if event=='miss' else .7
                self.audio.play(event,gain,x=f.pos.x)
            if f.braking:
                match.particles.burst(f.pos,f.color,1,-f.facing)
                if clock>.18: self.audio.play('skid',.25,x=f.pos.x);clock=0
            elif f.velocity.y>450 and clock>.20:
                self.audio.play('fall_wind',.20,x=f.pos.x);clock=0
            self.motion_sounds[f]=clock
            if f.landed_speed>380:
                match.impacts.emit(f.pos,f.color,.65,sound=None)
                match.particles.burst(f.pos,f.color,9)
            if f.grounded and abs(f.velocity.x)>90 and self.step_time>.14:
                match.particles.burst(f.pos,f.color,3,-f.facing)
                self.step_side=1-self.step_side
                self.audio.play('step_l' if self.step_side else 'step_r',.18,x=f.pos.x)
            elif not f.grounded and abs(f.velocity.x)>180:
                match.particles.burst(f.pos+(0,-45),f.color,1,-f.facing,style="trail")
        if self.step_time>.14: self.step_time=0
        for sound,point,strength in match.impacts.drain_audio_events():
            self.audio.play(sound,min(1,strength),x=point[0])

    def drop_impact(self,match):
        match.impacts.emit(match.drop.impact_event,GOLD,1.3,sound=None)
        match.particles.burst(match.drop.impact_event,GOLD,18)
        match.particles.burst(match.drop.impact_event,(171,148,105),8,style='trail')
        match.hit_stop=.04
        match.shake=.14
        match.camera.impulse(1,(0,1),pixels=5)
        self.audio.duck(.15)
        match.art.react(.8)
        self.audio.play("drop_impact",x=match.drop.x)
        self.audio.play("crowd",.3,x=match.drop.x)

    def collect(self,match,fighter):
        match.particles.burst(fighter.rect.center,GOLD,14)
        match.impacts.emit(fighter.rect.center,GOLD,.4,sound=None)
        self.audio.play("collect",x=fighter.pos.x)
        match.art.react(.65)
        self.audio.play("crowd",.18)

    def result(self,match):
        won=match.result=="VITÓRIA"
        self.audio.end_match()
        self.audio.play("knockout",.85)
        self.audio.play('crowd',.6)
        self.audio.play("victory" if won else "defeat",variation=False)
        match.camera.impulse(1.2)
        winner=match.player if won else match.enemy
        winner.celebrating=True
        match.impacts.emit((match.enemy if won else match.player).rect.center,winner.color,1.1,sound=None)
        if won:
            for x,c in ((320,match.player.color),(640,GOLD),(960,match.enemy.color)):
                match.particles.burst((x,250),c,30,style="confetti")
        match.art.react(1.4)
