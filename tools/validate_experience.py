"""Capturas preparadas e sessão automatizada em tempo real, sem janela.

python -m tools.validate_experience --seconds 180
"""
import os
os.environ["SDL_VIDEODRIVER"]="dummy"
os.environ["SDL_AUDIODRIVER"]="dummy"
import argparse
from collections import defaultdict
import hashlib
import json
import statistics
from time import perf_counter
import pygame
from scripts.config import ROOT,FIXED_DT
from scripts.game import Game
from scripts.combat.weapon import PAN
from scripts.scenes.pausa import Pausa


def screenshots():
    out=ROOT/".local"/"experiencia"
    out.mkdir(parents=True,exist_ok=True)
    game=Game("ringue",audio_enabled=False)
    def fresh():
        game.start_match()
        m=game.scene
        m.flow.phase="fight"
        m.player.set_aim((850,470))
        m.enemy.set_aim((390,470))
        for f in m.fighters: f.animate(.2)
        return m
    def save(name):
        game.scene.draw(game.screen)
        pygame.image.save(game.screen,str(out/(name+".png")))
    m=game.scene
    m.flow.phase="countdown";m.flow.elapsed=1.1
    save("01_contagem")
    m=fresh();m.player.axis=1
    for _ in range(10): m.player.update(FIXED_DT,m.platforms)
    save("02_corrida")
    m=fresh();m.player.jump()
    for _ in range(13): m.player.update(FIXED_DT,m.platforms)
    save("03_salto")
    m=fresh();m.player.inventory.collect(PAN);m.player.set_aim((680,350));m.player.attack()
    for _ in range(6): m.player.update(FIXED_DT,m.platforms)
    save("04_ataque")
    m=fresh();m.player.pos.x=600;m.enemy.pos.x=673
    m.player.inventory.collect(PAN);m.player.set_aim(m.enemy.shoulder);m.player.attack()
    for _ in range(4): m.player.update(FIXED_DT,m.platforms)
    if m.player.resolve_attack(m.enemy): m.feedback.hit(m,m.player,m.enemy)
    m.enemy.animate(.1);m.hud.update(FIXED_DT,m.fighters)
    save("05_impacto")
    m=fresh();m.drop.state="falling";m.drop.x=640;m.drop.y=345;m.drop.angle=-25
    save("06_panela")
    m=fresh();m.player.health=22;m.hud.update(.2,m.fighters)
    save("07_vida_baixa")
    m=fresh();m.enemy.health=0;m.check_result()
    for _ in range(45): m.simulate(FIXED_DT)
    save("08_vitoria")
    m=fresh();game.change_scene(Pausa(game,m));save("09_pausa")
    from scripts.scenes.options import Options
    game.change_scene(Options(game,game.scene));save("10_configuracoes")
    m=fresh();m.player.health=0;m.check_result()
    for _ in range(45): m.simulate(FIXED_DT)
    save("11_derrota")
    m=fresh();game.debug=True;save("12_debug")
    game.settings.resolution=(960,540);game.apply_display()
    game.scene.draw(game.screen);game.viewport.present(game.screen,game.window)
    pygame.image.save(game.window,str(out/"13_resolucao_960.png"))
    game.audio.stop();pygame.quit()
    return out


def soak(seconds,out):
    game=Game("ringue")
    frames=matches=0
    results={"VITÓRIA":0,"DERROTA":0}
    samples=[]
    start=perf_counter()
    last_report=start
    paused=0
    max_particles=0
    drop_states=set()
    while perf_counter()-start<seconds:
        game.clock.tick_busy_loop(60)
        frame_start=perf_counter()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: raise RuntimeError("Sessão encerrada inesperadamente")
        game.audio.update(FIXED_DT)
        m=game.scene
        if isinstance(m,Pausa):
            paused-=1
            if paused<=0: game.change_scene(m.match)
        elif m.result:
            m.simulate(FIXED_DT)
            if m.flow.result_age>1.2:
                results[m.result]+=1;matches+=1
                game.start_match()
                game.scene.flow.skip()
        else:
            keys=defaultdict(bool)
            if m.flow.phase=="fight":
                target=m.drop.x if m.drop.state=="available" and PAN not in m.player.inventory.slots else m.enemy.pos.x
                delta=target-m.player.pos.x
                keys[pygame.K_d]=delta>48;keys[pygame.K_a]=delta<-48
                m.player.set_aim(m.enemy.shoulder)
                if frames%23==0: m.player.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1),m.drop)
                if frames%145==0: m.player.request_jump()
                if frames%145==7: m.player.release_jump()
                if frames%950==0: m.drop.discard(m.player)
            m.simulate(FIXED_DT,keys)
            assert 0<=m.player.health<=100 and 0<=m.enemy.health<=100
            held=sum(f.inventory.slots.count(PAN) for f in m.fighters)
            assert held<=1
            assert not (held and m.drop.state in ("available","falling","warning"))
            assert len(m.particles.items)<=m.particles.limit
            max_particles=max(max_particles,len(m.particles.items))
            drop_states.add(m.drop.state)
            if frames and frames%1500==0:
                game.change_scene(Pausa(game,m));paused=35
        game.scene.draw(game.screen)
        game.viewport.present(game.screen,game.window)
        pygame.display.flip()
        samples.append((perf_counter()-frame_start)*1000)
        frames+=1
        if perf_counter()-last_report>30:
            print(f"{perf_counter()-start:.0f}s | {frames} quadros | {matches} duelos",flush=True)
            last_report=perf_counter()
    elapsed=perf_counter()-start
    data={"wall_seconds":round(elapsed,2),"frames":frames,"matches":matches,"results":results,
          "observed_fps":round(frames/elapsed,2),"frame_work_mean_ms":round(statistics.mean(samples),3),
          "frame_work_p95_ms":round(sorted(samples)[int(len(samples)*.95)],3),
          "max_particles":max_particles,"drop_states":sorted(drop_states),
          "audio_enabled":game.audio.enabled,"driver":pygame.display.get_driver(),
          "gdd_sha256":hashlib.sha256((ROOT/"docs"/"ARMS_RACE_GDD.docx").read_bytes()).hexdigest()}
    (out/"sessao_headless.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(data,ensure_ascii=False),flush=True)
    game.audio.stop();pygame.quit()


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--seconds",type=float,default=180)
    args=parser.parse_args()
    if args.seconds<0: parser.error("Duração inválida")
    output=screenshots()
    if args.seconds: soak(args.seconds,output)
