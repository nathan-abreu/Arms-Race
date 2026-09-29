"""Capturas v2 e duelos automatizados, com opção de janela real.

python -m tools.validate_background --seconds 180
python -m tools.validate_background --window --seconds 45
Entradas são programadas; esta ferramenta não é um teste humano.
"""
import argparse
import os
from collections import defaultdict
import json
import statistics
from time import perf_counter


def capture(out):
    import pygame
    from scripts.game import Game
    from scripts.config import FIXED_DT
    from scripts.combat.weapon import PAN
    game=Game('ringue',audio_enabled=False)
    def fresh():
        game.start_match()
        m=game.scene
        m.flow.phase='fight'
        m.player.set_aim(m.enemy.shoulder);m.enemy.set_aim(m.player.shoulder)
        for f in m.fighters: f.animate(1)
        return m
    def save(name):
        game.scene.draw(game.screen)
        game.viewport.present(game.screen,game.window)
        pygame.display.flip()
        pygame.image.save(game.screen,str(out/(name+'.png')))
    m=fresh();save('01_inicio')
    m=fresh();m.player.axis=1
    for _ in range(11): m.player.update(FIXED_DT,m.platforms)
    save('02_corrida')
    m=fresh();m.player.jump()
    for _ in range(12): m.player.update(FIXED_DT,m.platforms)
    save('03_salto')
    m=fresh();m.player.pos.x=570;m.enemy.pos.x=655
    m.player.set_aim(m.enemy.shoulder);m.enemy.set_aim(m.player.shoulder)
    m.player.attack()
    for _ in range(4): m.player.update(FIXED_DT,m.platforms)
    save('04_soco')
    m=fresh();m.player.pos.x=570;m.enemy.pos.x=657
    m.player.set_aim(m.enemy.shoulder)
    for _ in range(2):
        m.player.attack()
        for _ in range(16): m.player.update(FIXED_DT,m.platforms)
    m.player.attack()
    for _ in range(4): m.player.update(FIXED_DT,m.platforms)
    assert m.player.combo_index==3
    save('05_combo_final')
    assert m.player.resolve_attack(m.enemy)
    m.feedback.hit(m,m.player,m.enemy)
    m.enemy.animate(.08);m.hud.update(FIXED_DT,m.fighters)
    save('07_impacto')
    m=fresh();m.drop.state='falling';m.drop.x=640;m.drop.y=330;m.drop.angle=34
    save('06_panela_caindo')
    m=fresh();m.player.inventory.collect(PAN);m.enemy.health=0;m.check_result()
    for _ in range(45): m.simulate(FIXED_DT)
    save('08_vitoria')
    m=fresh();game.debug=True;save('09_alinhamento_f3');game.debug=False
    for q,label in ((0,'baixo'),(1,'medio'),(2,'alto')):
        game.settings.particles=q;m.simulate(FIXED_DT);save('10_qualidade_'+label)
    game.settings.resolution=(1000,800);game.apply_display()
    game.scene.draw(game.screen);game.viewport.present(game.screen,game.window)
    pygame.image.save(game.window,str(out/'11_redimensionado.png'))
    game.settings.fullscreen=True;game.apply_display()
    game.viewport.present(game.screen,game.window);pygame.display.flip()
    pygame.image.save(game.window,str(out/'12_tela_cheia.png'))
    game.settings.fullscreen=False;game.apply_display()
    game.audio.stop();pygame.quit()


def run(seconds,out,window=False,exercise_display=True,player_policy=None):
    import pygame
    from scripts.game import Game
    from scripts.config import FIXED_DT
    from scripts.scenes.pausa import Pausa
    from scripts.combat.weapon import PAN
    game=Game('ringue')
    game.settings.particles=2  # pior caso gráfico disponível
    samples=[];frames=completed=0;max_particles=0
    results=defaultdict(int);states=set();sizes=[]
    start=last=perf_counter()
    steady_start=None
    steady_frames=0
    steady_samples=[]
    paused=0
    while perf_counter()-start<seconds:
        elapsed=min(game.clock.tick_busy_loop(60)/1000,.1)
        begin=perf_counter()
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                game.running=False
        if not game.running: break
        # Exercita a troca de modo no mesmo dispositivo usado para a sessão.
        if exercise_display and frames in (120,200,280):
            game.settings.resolution=(960,540) if frames==120 else (1280,720)
            game.settings.fullscreen=frames==200
            game.apply_display();sizes.append([list(game.window.get_size()),game.settings.fullscreen])
        game.audio.update(elapsed)
        m=game.scene
        if isinstance(m,Pausa):
            paused-=1
            if paused<=0: game.change_scene(m.match)
        elif m.result:
            m.simulate(FIXED_DT)
            if m.flow.result_age>1:
                results[m.result]+=1;completed+=1
                game.start_match();game.scene.flow.skip()
        else:
            keys=defaultdict(bool)
            if m.flow.phase=='fight':
                target=m.drop.x if m.drop.state=='available' and PAN not in m.player.inventory.slots else m.enemy.pos.x
                delta=target-m.player.pos.x
                keys[pygame.K_d]=delta>75;keys[pygame.K_a]=delta<-75
                m.player.set_aim(m.enemy.shoulder)
                # Deixa a primeira entrega chegar antes de pressionar a CPU.
                if frames%15==0 and m.time>9: m.player.attack()
                if frames%151==0: m.player.request_jump()
                if frames%151==8: m.player.release_jump()
                if frames%800==0: m.drop.discard(m.player)
                if player_policy: player_policy(m,keys,frames,completed)
            m.simulate(FIXED_DT,keys)
            assert 0<=m.player.health<=100 and 0<=m.enemy.health<=100
            assert sum(f.inventory.slots.count(PAN) for f in m.fighters)<=1
            assert len(m.particles.items)<=m.particles.limit
            if all(f.grounded for f in m.fighters):
                assert abs(m.player.pos.x-m.enemy.pos.x)>m.player.WIDTH-3
            states.add(m.drop.state)
            max_particles=max(max_particles,len(m.particles.items))
            if frames and frames%1400==0:
                game.change_scene(Pausa(game,m));paused=20
        game.scene.draw(game.screen)
        game.viewport.present(game.screen,game.window)
        pygame.display.flip()
        samples.append((perf_counter()-begin)*1000)
        if frames==360:
            steady_start=perf_counter()
        elif frames>360:
            steady_frames+=1
            steady_samples.append(samples[-1])
        frames+=1
        if perf_counter()-last>30:
            print(f'{perf_counter()-start:.0f}s | {frames} quadros | {completed} partidas',flush=True)
            last=perf_counter()
    duration=perf_counter()-start
    report=dict(seconds=round(duration,2),frames=frames,matches=completed,results=dict(results),
                fps=round(frames/duration,2),work_mean_ms=round(statistics.mean(samples),3),
                work_p95_ms=round(sorted(samples)[int(len(samples)*.95)],3),
                driver=pygame.display.get_driver(),audio=game.audio.enabled,quality='alto',
                image_loaded=game.arena_art.image_found,display_modes=sizes,
                display_changes=exercise_display,
                max_particles=max_particles,drop_states=sorted(states))
    if steady_start is not None and steady_samples:
        report['steady_fps']=round(steady_frames/(perf_counter()-steady_start),2)
        report['steady_work_p95_ms']=round(sorted(steady_samples)[int(len(steady_samples)*.95)],3)
        report['steady_frames']=steady_frames
    (out/('janela.json' if window else 'headless.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    pygame.image.save(game.window,str(out/('partida_janela.png' if window else 'partida_headless.png')))
    print(json.dumps(report,ensure_ascii=False),flush=True)
    game.audio.stop();pygame.quit()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--window',action='store_true')
    parser.add_argument('--seconds',type=float,default=180)
    args=parser.parse_args()
    if args.seconds<0: parser.error('Duração deve ser positiva')
    if args.window:
        os.environ.pop('SDL_VIDEODRIVER',None)
        os.environ.pop('SDL_AUDIODRIVER',None)
    else:
        os.environ['SDL_VIDEODRIVER']='dummy'
        os.environ['SDL_AUDIODRIVER']='dummy'
    from scripts.config import ROOT
    out=ROOT/'.local'/'background_v2';out.mkdir(parents=True,exist_ok=True)
    if not args.window: capture(out)
    if args.seconds: run(args.seconds,out,args.window)


if __name__=='__main__': main()
