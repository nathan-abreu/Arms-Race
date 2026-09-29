"""Capturas A/B/C reais do renderizador e sessão automatizada de polimento."""
import os
os.environ['SDL_VIDEODRIVER']='dummy'
os.environ['SDL_AUDIODRIVER']='dummy'
import argparse
from pathlib import Path
import pygame
from scripts.game import Game
from scripts.config import FIXED_DT,ROOT
from scripts.combat.weapon import PAN


def sparring(match,keys,frame,completed):
    """Entradas humanas possíveis: kite/jump antes da entrega, depois disputar."""
    player,enemy=match.fighters
    if match.time<8 and match.drop.state not in ('available','held'):
        target=245 if enemy.pos.x>640 else 1035
        keys[pygame.K_a]=player.pos.x>target+25
        keys[pygame.K_d]=player.pos.x<target-25
        if abs(player.pos.x-enemy.pos.x)<160 and player.grounded:
            player.request_jump()
    if frame%14==0 and abs(player.pos.x-enemy.pos.x)<130:
        player.attack()


def capture(out):
    out.mkdir(parents=True,exist_ok=True)
    game=Game('ringue',audio_enabled=False)
    def fresh():
        game.start_match();m=game.scene;m.flow.phase='fight';m.hud.time=8
        m.player.set_aim(m.enemy.shoulder);m.enemy.set_aim(m.player.shoulder)
        m.drop.timer=99
        for f in m.fighters: f.animate(1)
        return m
    def save(name):
        game.scene.draw(game.screen)
        pygame.image.save(game.screen,str(out/(name+'.png')))
    m=fresh()
    m.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_F4))
    m.hud.update(.25,m.fighters)
    save('A_guarda_inventario')
    m=fresh();m.time=7.5;m.drop.state='falling';m.drop.x=640;m.drop.y=315;m.drop.angle=-18
    m.drop.trail=[(640,y) for y in (231,244,258,272,287,300,315)]
    save('B_entrega_panela')
    m=fresh();m.player.pos.x=560;m.enemy.pos.x=644
    m.player.set_aim(m.enemy.shoulder);m.enemy.set_aim(m.player.shoulder)
    m.player.inventory.collect(PAN)
    for f in m.fighters: f.animate(1)
    m.player.attack()
    m.player.update(.105,m.platforms)
    assert m.player.resolve_attack(m.enemy),'A captura C exige contato real antes dos efeitos'
    m.feedback.hit(m,m.player,m.enemy)
    m.enemy.animate(.025)
    m.particles.update(.045)
    m.impacts.update(.015,m.fighters,m.platforms[0]);m.hud.update(.04,m.fighters)
    save('C_panela_acerto')
    # Série auxiliar para examinar a sequência, sem saltar etapas da máquina.
    m=fresh();m.drop.timer=0
    captured=set()
    for frame in range(170):
        previous=m.drop.state
        m.drop.update(FIXED_DT,m.fighters,m.platforms);m.time+=FIXED_DT
        m.art.update(FIXED_DT)
        if m.drop.state in ('warning','opening','falling','available') and m.drop.state not in captured:
            captured.add(m.drop.state);save('fase_'+m.drop.state)
        if m.drop.state=='available' and m.drop.pickup_delay==0:
            m.player.pos.x=m.drop.x
            m.player.animate(1)
            if m.drop.try_collect(m.player):
                m.feedback.collect(m,m.player)
                m.drop.update(.075,m.fighters,m.platforms)
                m.hud.update(.075,m.fighters)
                save('fase_coleta');break
    # Guardas com mira vertical e poses extremas também são verificáveis.
    m=fresh();m.player.set_aim((m.player.pos.x,650));m.player.animate(1)
    save('mira_para_baixo')
    game.audio.stop();pygame.quit()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--seconds',type=float,default=0)
    args=parser.parse_args()
    if args.seconds<0: parser.error('Duração inválida')
    out=ROOT/'.local'/'premium'
    capture(out)
    if args.seconds:
        from tools.validate_background import run
        # Resize/fullscreen são exercitados separadamente em janela Windows.
        # SDL dummy perde desempenho depois de recriar seu display neste host.
        run(args.seconds,out,exercise_display=False,player_policy=sparring)


if __name__=='__main__': main()
