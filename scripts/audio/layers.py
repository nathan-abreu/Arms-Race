"""Efeitos originais compostos por ruído filtrado, transientes e ressonâncias.

Cada receita é mixada/normalizada antes da reprodução, ocupando uma voz.
Não utiliza amostras externas. A música existente não passa por este gerador.
"""
from dataclasses import dataclass
from functools import lru_cache
from array import array
import math
import random
import wave
from scripts.audio.synth import RATE
from scripts.config import ROOT


@dataclass(frozen=True)
class Layer:
    kind: str
    duration: float
    gain: float
    frequency: float=100
    delay: float=0


@dataclass(frozen=True)
class Cue:
    group: str
    layers: tuple
    copies: int=2


def cue(group,*layers): return Cue(group,tuple(layers))


WHOOSH=(Layer('air',.14,.65,1300),Layer('noise',.08,.18,3200,.015))
BODY=(Layer('thud',.095,.8,95),Layer('noise',.035,.58,1800),Layer('crack',.018,.28,6500),*WHOOSH)
METAL=(Layer('metal',.31,.70,570),Layer('metal',.22,.38,923,.005),Layer('thud',.12,.55,76),Layer('crack',.024,.22,7000))
CUES={
    'swing':cue('personagem',*WHOOSH),
    'air_attack':cue('personagem',*WHOOSH),
    'miss':cue('personagem',Layer('air',.11,.5,1600)),
    'hit':cue('impactos',*BODY),
    'heavy_hit':cue('impactos',*BODY,Layer('sub',.16,.8,52),Layer('electric',.075,.30,210)),
    'metal_swing':cue('armas',*WHOOSH,Layer('metal',.10,.24,1300)),
    'metal_impact':cue('impactos',*METAL),
    'drop_impact':cue('impactos',*METAL,Layer('sub',.22,.8,48),Layer('noise',.12,.42,500)),
    'warning':cue('ambiente',Layer('rise',.90,.45,380),Layer('electric',.90,.2,160),Layer('air',.90,.3,1500)),
    'beam':cue('armas',Layer('rise',.35,.35,200),Layer('electric',.65,.35,320),Layer('air',.68,.4,1900)),
    'step':cue('personagem',Layer('noise',.055,.45,600),Layer('thud',.07,.3,120)),
    'step_l':cue('personagem',Layer('noise',.055,.45,560),Layer('thud',.07,.3,110)),
    'step_r':cue('personagem',Layer('noise',.052,.42,700),Layer('thud',.07,.3,125)),
    'jump':cue('personagem',Layer('air',.10,.4,700),Layer('thud',.065,.3,150)),
    'landing':cue('personagem',Layer('noise',.085,.5,800),Layer('thud',.13,.6,85)),
    'skid':cue('personagem',Layer('air',.12,.4,1500),Layer('crack',.08,.25,4500)),
    'fall_wind':cue('ambiente',Layer('air',.22,.5,900)),
    'damage':cue('personagem',Layer('thud',.09,.4,80),Layer('noise',.06,.3,1300)),
    'collect':cue('interface',Layer('rise',.20,.32,850),Layer('metal',.16,.18,1600),Layer('crack',.02,.25,5000)),
    'discard':cue('armas',Layer('air',.15,.45,700),Layer('metal',.10,.16,800)),
    'slot_switch':cue('interface',Layer('crack',.024,.4,3000),Layer('metal',.07,.15,1100)),
    'slot_empty':cue('interface',Layer('noise',.04,.3,1300),Layer('thud',.06,.2,240)),
    'select':cue('interface',Layer('crack',.02,.25,3600),Layer('metal',.06,.18,1150)),
    'confirm':cue('interface',Layer('metal',.13,.3,1000),Layer('crack',.026,.25,3100),Layer('rise',.09,.2,600)),
    'back':cue('interface',Layer('noise',.04,.2,2300),Layer('thud',.09,.3,260)),
    'pause':cue('interface',Layer('air',.13,.2,800),Layer('metal',.12,.3,450)),
    'countdown':cue('interface',Layer('thud',.1,.4,200),Layer('metal',.13,.35,880)),
    'crowd':cue('plateia',Layer('crowd',.65,.5,1200),Layer('crowd',.52,.25,2600,.025)),
    'knockout':cue('impactos',Layer('sub',.32,.9,40),Layer('noise',.095,.5,1300),Layer('electric',.14,.35,100)),
    'victory':cue('interface',Layer('rise',.55,.3,330),Layer('metal',.5,.3,660),Layer('metal',.4,.2,990,.1),Layer('crack',.07,.2,2000)),
    'defeat':cue('interface',Layer('sub',.40,.45,90),Layer('metal',.40,.25,196),Layer('air',.4,.25,500)),
}


def compose(recipe,seed='cue'):
    duration=max(l.delay+l.duration for l in recipe.layers)
    mix=[0.0]*round(duration*RATE)
    for number,layer in enumerate(recipe.layers):
        rng=random.Random(str(seed)+str(number))
        low=high=phase=0.0
        alpha=1-math.exp(-math.tau*min(layer.frequency,RATE*.4)/RATE)
        for i in range(round(layer.duration*RATE)):
            t=i/RATE;u=t/layer.duration
            attack=min(1,t/.0015)
            env=attack*(1-u)**2
            noise=rng.uniform(-1,1)
            low+=alpha*(noise-low)
            high+=.08*(noise-high)
            if layer.kind in ('air','noise','crack','crowd'):
                value=(noise-high if layer.kind=='crack' else low)
                if layer.kind=='air': env=math.sin(math.pi*u)**1.3
                if layer.kind=='crowd': env=math.sin(math.pi*u)**.7*(.65+.35*math.sin(t*39)**2)
            elif layer.kind in ('thud','sub'):
                frequency=layer.frequency*(1+.65*math.exp(-t*45))
                phase+=math.tau*frequency/RATE
                value=math.sin(phase)*.8+low*.2
            elif layer.kind=='metal':
                value=sum(math.sin(math.tau*layer.frequency*k*t)*g*math.exp(-t*decay)
                          for k,g,decay in ((1,.5,6),(1.414,.24,12),(2.37,.16,18),(3.93,.10,30)))
            elif layer.kind=='rise':
                phase+=math.tau*layer.frequency*(1+u*3)/RATE
                value=math.sin(phase)*.45+math.sin(phase*1.007)*.25+low*.30
                env=attack*math.sin(math.pi*u*.92)**.7
            else:
                phase+=math.tau*layer.frequency*(1+u*.4)/RATE
                value=(math.sin(phase)*math.sin(phase*1.71)+low)*.5
            env*=min(1,(layer.duration-t)/.010)
            index=i+round(layer.delay*RATE)
            if index<len(mix): mix[index]+=value*env*layer.gain
    peak=max(.001,max(abs(x) for x in mix))
    samples=array('h')
    for value in mix:
        v=round(value/peak*.72*32767)
        samples.extend((v,v))
    return samples.tobytes()


@lru_cache(maxsize=120)
def pcm_cue(name,pitch=1.0):
    if pitch==1:
        return compose(CUES.get(name,CUES['hit']),name)
    original=array('h',pcm_cue(name))
    frames=len(original)//2
    result=array('h')
    for i in range(int(frames/pitch)-1):
        pos=i*pitch;j=int(pos);weight=pos-j
        value=round(original[j*2]*(1-weight)+original[min(j+1,frames-1)*2]*weight)
        result.extend((value,value))
    return result.tobytes()


def cue_path(name):
    group=CUES.get(name,CUES['hit']).group
    folder='interface' if group=='interface' else 'efeitos'
    return ROOT/'assets'/'audio'/folder/('premium_'+name+'.wav')


def generate(overwrite=False):
    for name in CUES:
        path=cue_path(name)
        if path.exists() and not overwrite: continue
        path.parent.mkdir(parents=True,exist_ok=True)
        with wave.open(str(path),'wb') as out:
            out.setnchannels(2);out.setsampwidth(2);out.setframerate(RATE)
            out.writeframes(pcm_cue(name))


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--force',action='store_true',help='Regenera somente os WAVs premium deste módulo')
    generate(parser.parse_args().force)
