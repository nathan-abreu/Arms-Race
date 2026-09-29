"""Áudio original gerado por osciladores, envelopes e ruído determinístico.

Sem samples externos. Música: 120 BPM, quatro compassos, loop de 8 segundos.
"""
from array import array
from functools import lru_cache
import math
import random
import wave
from scripts.config import ROOT

RATE=22050
MUSIC=("menu","ringue","critical")
UI=("select","confirm","back","pause","countdown")
EFFECTS=("step","jump","landing","air_attack","swing","hit","miss","metal_impact",
         "damage","collect","warning","drop_impact","victory","defeat","crowd","heavy_hit","knockout")


@lru_cache(maxsize=80)
def pcm(name,pitch=1.0):
    rng=random.Random(name)
    music=name in MUSIC
    duration=8.0 if music else (.38 if name in ("heavy_hit","knockout") else 1.1 if name in ("victory","defeat","crowd") else .19)
    samples=array('h')
    frequencies={"select":800,"confirm":1046,"back":350,"pause":520,"countdown":880,
                 "step":95,"jump":380,"landing":75,"air_attack":650,"swing":440,
                 "hit":120,"miss":320,"metal_impact":740,"damage":150,"collect":1300,
                 "warning":990,"drop_impact":230,"victory":523,"defeat":196,"crowd":170,"heavy_hit":68,"knockout":48}
    notes=(110,130.81,146.83,164.81,110,130.81,196,146.83)
    for i in range(int(duration*RATE)):
        t=i/RATE
        if music:
            beat=t*2
            step=int(beat*2)
            local=(beat*2)%1/4
            freq=notes[(step//2)%len(notes)]
            bass=math.sin(math.tau*freq*t)*math.exp(-local*15)*.20
            lead=math.sin(math.tau*freq*4*t)*math.exp(-local*22)*.10
            b=beat%1/2
            kick=math.sin(math.tau*(54*b+55*(1-math.exp(-b*30))/30))*math.exp(-b*18)*.34
            noise=rng.uniform(-1,1)
            hat=noise*math.exp(-local*100)*.06
            snare=noise*math.exp(-b*30)*.09 if int(beat)%2 else 0
            if name=="menu":
                value=(bass*.6+lead*.65+kick*.45+hat*.3)
            elif name=="critical":
                # Camada síncrona sobre ringue; não troca/recomeça o loop.
                value=math.sin(math.tau*freq*8*t)*math.exp(-local*30)*.10+hat+snare
            else:
                value=bass+lead+kick+hat+snare
            # Emenda de 4 ms em zero, musicalmente sobre o ataque do kick.
            value*=min(1,t/.004,(duration-t)/.004)
        else:
            freq=frequencies.get(name,440)*pitch
            env=(1-t/duration)**2*min(1,t/.003)
            noise=rng.uniform(-1,1)
            if name in ("heavy_hit","knockout"):
                value=math.sin(math.tau*(freq*t+20*(1-math.exp(-t*20))/20))*.62+noise*math.exp(-t*45)*.3
            elif name in ("metal_impact","drop_impact"):
                value=sum(math.sin(math.tau*freq*ratio*t)*amp for ratio,amp in ((1,.3),(1.47,.22),(2.31,.14)))*math.exp(-t*8)+noise*.08
            elif name in ("hit","damage","step","landing"):
                value=math.sin(math.tau*freq*t)*.4+noise*.28
            elif name in ("swing","miss","air_attack","crowd"):
                value=noise*.35*(.6+.4*math.sin(math.tau*7*t))
            else:
                glide=1+t*1.8 if name not in ("defeat","back") else max(.3,1-t*.6)
                value=math.sin(math.tau*freq*glide*t)*.45
            value*=env
        v=int(max(-.95,min(.95,value))*32767)
        samples.extend((v,v))
    return samples.tobytes()


def path_for(name):
    folder="musica" if name in MUSIC else "interface" if name in UI else "efeitos"
    return ROOT/"assets"/"audio"/folder/(name+".wav")


def generate_assets():
    for name in (*MUSIC,*UI,*EFFECTS):
        path=path_for(name)
        path.parent.mkdir(parents=True,exist_ok=True)
        # A ferramenta não substitui arquivos editados pelo usuário.
        if path.exists():
            continue
        with wave.open(str(path),'wb') as out:
            out.setnchannels(2); out.setsampwidth(2); out.setframerate(RATE)
            out.writeframes(pcm(name))


if __name__=="__main__":
    generate_assets()
