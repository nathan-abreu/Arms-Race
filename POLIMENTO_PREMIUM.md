# Ringue Neon — polimento premium

Entrega restrita à Fase 1: personagens, Panela/entrega, inventário e áudio/impacto.
Imagem-base, menu, música existente e GDD preservados. Nenhum commit ou push.

## Personagens e contato

Silhuetas geométricas contínuas, aproximadamente 155 px de altura, cabeça
quadrada de 34 px, membros de 15–17 px, mãos de aproximadamente 13×14 px,
guarda com pés separados por 45 px. Borda de 1 px por lado e halo de 6 px.
O membro traseiro usa 82% do brilho da cor; não há articulações circulares
expostas, linhas de esqueleto ou luvas de boxe. Respiração de 0,7 px.

Ordem: membros traseiros, tronco, perna dianteira, cabeça, braço dianteiro,
mãos/arma e efeitos. O segundo soco usa o outro braço; o terceiro altera
inclinação e apoio. Corrida usa distância percorrida para a passada, pouso
comprime pernas, dano inclina o corpo e nocaute deita a silhueta. O rig
interpola poses e abre espaço ao mirar para baixo.

Cápsula corporal com raio 26 px, separação suave até 84 px entre centros no
chão; altura suficiente permite saltar por cima. A CPU verifica alcance nos
volumes visuais e recua após o ataque. A colisão ofensiva acompanha mão/bojo,
com varredura entre amostras; cápsulas de cabeça, tronco e membros seguem
a pose desenhada. Um golpe errado não emite explosão de acerto.

## Panela e entrega

Superfície independente com pivô no centro do bojo; rotações e escalas em
cache. Bojo elíptico escuro de 56×36 px, borda dourada de 5 px, cabo curto,
silhueta total próxima de 76×38 px. Na mão, escala de 85%.

1. Após seis segundos de luta, aviso de **900 ms**: elipse pulsante, quadrados
   subindo, arena escurecida, telão pulsando, alerta crescente e ARMA CHEGANDO.
2. Abertura do feixe em **120 ms**: núcleo branco-amarelo de 16 px, coluna
   dourada de 44 px e halo de 112 px. Seis gradientes locais em cache,
   variações de largura/alpha, reflexo no piso, linhas e quadrados animados.
3. Queda em aproximadamente **700 ms**, aceleração de 2150 px/s², giro no
   próprio pivô, rastro transparente dourado e controle dos lutadores ativo.
4. Impacto com compressão de **120 ms**, onda, faíscas/poeira, som próprio,
   shake de 5 px e pausa de 40 ms. O feixe some em 100 ms; coleta liberada
   após 120 ms. A queda pode ferir e empurrar quem entrar no ponto anunciado.
5. Coleta com voo interpolado de **180 ms** até a mão, flash, som, pulso no
   slot e nome PANELA por **750 ms**. A arma na mão só aparece ao terminar o
   voo. Descarte nasce na mão, com animação do ícone saindo do slot.

Uma única Panela entre arena e inventários; coleta cheia bloqueada. O ponto
é seguro e a origem é verificada antes da queda. CPU disputa e evita o aviso.

## Inventário

Três slots de 82×76 px, intervalo 8 px, margem direita 25 px, teclas 24×20 px
com margem inferior 18 px. Moldura angular azul-clara, seleção ciano/dourada,
ícones vetoriais nítidos de 52×42 px, pulsos e descarte animado. Slot vazio
não tem texto; nome temporário fica acima. HUD fixo, fora do shake, sem mira
ou linha de debug durante gameplay normal. Dicas pequenas somem após 6 s.

Ícones: **Panela, Machado, Rifle e Lançador**. Só a Panela possui gameplay.
F4, inicialmente desligado, alterna uma prévia isolada de três ícones
(Machado/Rifle/Lançador), com munições demonstrativas 30/3. Q/E/roda e X
permitem inspecionar animações. F4 não injeta armas fictícias no combate e
restaura os slots reais ao desligar. Não foram implementadas novas armas
funcionais, fases ou loja.

## Áudio e impacto

Receitas originais em `scripts/audio/layers.py`: ruído filtrado, corpo grave,
transiente seco, estalo, vento, síntese eletrônica e ressonâncias metálicas
não harmônicas. Soco, terceiro golpe, Panela contra corpo e Panela contra piso
têm camadas distintas. Interface, passos alternados, salto, queda rápida,
derrapagem, pouso proporcional, alerta/feixe, coleta, troca/vazio, vitória,
derrota, nocaute e plateia recebem efeitos próprios. Sem samples externos.

17 canais: música 3; interface 2; personagem 3; armas 2; impactos 3; ambiente
2; plateia 2. Limite de duas cópias por efeito, intervalo mínimo 45 ms,
panorama estéreo conforme posição, tom ±3%, volume aleatório 94–100%.
Pico dos efeitos normalizado a 0,72; orçamento agregado de efeitos 0,70 e
música 0,30, incluindo crossfade/camada crítica. Ducking de **4 dB / 150 ms**
em impactos fortes, retorno suave. Sons pré-carregados; sem dispositivo ou
arquivo o jogo continua, com fallback silencioso/síntese conforme o caso.

| Feedback | Soco | Terceiro golpe | Panela |
| --- | ---: | ---: | ---: |
| Hitstop | 40 ms | 65 ms | 80 ms |
| Shake nominal | 3 px | 6 px | 8 px |
| Flash branco | 50 ms | 50 ms | 50 ms |
| Partículas nominais | 8 | 18 | 14 douradas + 4 brancas |
| Knockback | 255 / 285 px/s | 440 px/s | 390 px/s |
| Dano | 7 / 8 | 13 | 10 |

Shake é multiplicado pela preferência (padrão 65%); partículas seguem a
qualidade (65/125/180 de limite). Microzoom e plateia acompanham golpes
fortes. Nocaute: 55 ms de pausa e 400 ms de câmera lenta com retorno suave,
foco no vencedor e efeito próprio. A física mantém os parâmetros anteriores:
velocidade 380, aceleração 2800, frenagem 3400, salto 720, gravidade 1900/2700,
controle aéreo 65%, coyote/buffer 120 ms. Invulnerabilidade 220 ms, hitstun
130 ms; o flash de 50 ms é independente da invulnerabilidade.

## Comparação visual realizada

Foram abertas e inspecionadas capturas produzidas pelo renderizador, usando
a referência original da conversa e a captura anterior do projeto. A imagem
de referência serve de direção artística; personagens e HUD são dinâmicos.

| Captura | Comparação e refinamento |
| --- | --- |
| A — guarda/inventário | Ciano/rosa sólidos, cabeça quadrada, mãos pequenas, pernas grossas, contorno fino. Pés sobre y=514; centros separados. Slots com margens iguais e ícones sem nomes apertados. |
| B — entrega | Frigideira elíptica escura/cabo lateral. Núcleo inicialmente fraco foi clareado; halo mantém transparência. Rastro que escurecia o feixe foi trocado por alpha dourado. Elipse e reflexo no piso. |
| C — acerto | Captura exige `resolve_attack` verdadeiro antes dos efeitos. Panela encosta no alvo, vida passa de 100 para 90, rastro da barra permanece. Arco ampliado para ficar fora do bojo, flash encurtado e faíscas metálicas direcionais mais visíveis. |

A/B/C em `.local/premium/A_guarda_inventario.png`, `B_entrega_panela.png` e
`C_panela_acerto.png`. Também: `fase_warning`, `fase_opening`, `fase_falling`,
`fase_available`, `fase_coleta` e `mira_para_baixo`. São cenas preparadas com
o renderizador real, não capturas de teste humano interativo. A composição
mantém a arena existente; não tenta reproduzir pixel a pixel a ilustração.

## Validação

Antes: **77 testes aprovados**. Depois: **95 testes aprovados**, incluindo
os 77 existentes com fixtures atualizadas para tempos/alcances e contato
visível. Novos testes cobrem silhueta conectada em movimentos, ambos os
socos/finisher e mira; ordem de desenho; cápsulas/separação/passagem aérea;
contato antes de partículas; pivô em 24 rotações; gradiente do feixe;
entrega completa/tempos/coleta; inventário/Q/E/roda/descarte; F4 isolado;
vozes/grupos, camadas/picos, panorama, ducking, crossfade e ausência de áudio.
A cobertura anterior mantém salto, física, IA, pausa, vitória/derrota e reinício.

`compileall` sem erros. `main.py --headless --no-audio --scene ringue --frames
120` encerrou sem falhas. Métricas de desempenho estão registradas nos JSONs
locais. Foram executadas duas sessões headless de 180 s, além de medições
diagnósticas e duas sessões Windows. Resultados da última sessão de cada tipo:

| Sessão | Resultado |
| --- | --- |
| Headless, SDL dummy, Alto, áudio dummy | 180,01 s; 6.873 quadros; 38,18 FPS; trabalho médio 24,216 ms, p95 42,757 ms; pico 127 partículas; sete duelos (seis vitórias/uma derrota); todos os seis estados da entrega, pausa e reinícios. |
| Janela Windows, Alto, áudio habilitado | 45,01 s; 2.592 quadros; 57,59 FPS incluindo mudanças de modo; trecho estável 61,96 FPS em 2.231 quadros; p95 estável 15,988 ms; uma vitória/uma derrota; pico 113 partículas; todos os estados da entrega. |

Resize para 960×540, tela cheia 1280×720 e retorno à janela foram executados
automaticamente na sessão Windows. O limitador usa 16 ms, por isso a leitura
pode se aproximar de 62 FPS; a simulação continua em passos de 1/60 s.

**Limitação observada:** o driver dummy ficou abaixo da meta, mesmo ao
separar a recriação do display da sessão longa. A primeira sessão, incluindo
trocas de modo, mediu 30,45 FPS. A investigação não isolou completamente a
causa da discrepância. A janela Windows manteve aproximadamente 60 FPS na
luta estável; não se promete o mesmo desempenho para outro hardware nem
para o driver headless. Algumas verificações auxiliares ocorreram durante
a sessão dummy, portanto ela não é um benchmark de máquina ociosa.

Evidências locais: `.local/premium/headless.json`, `.local/premium/janela.json`
e `.local/premium/manifest.json`. As capturas foram efetivamente abertas e
observadas; a sessão em janela foi automatizada, sem teste manual interativo.

## Limitações e teste humano pendente

- Avaliar manualmente resposta do mouse, combo alternando braços, sensação
  de peso, salto por cima e separação durante pressão nas cordas.
- Disputar/coletar/descartar a Panela, girar a mira durante golpes e conferir
  o voo para a mão em movimento. Exercitar F4, Q/E/roda/X e desligar F4.
- Ouvir sons/música em fones e caixas reais: timbre metálico, grave, panorama,
  ducking, repetição e volumes. A trilha continua procedural de quatro
  compassos; efeitos compostos não equivalem a produção de estúdio.
- Conferir conforto do shake, leitura de partículas e desempenho no seu
  computador, em diferentes resoluções/qualidades e tela cheia.
- Não houve teste humano interativo nem audição manual. Testes de janela
  usam entradas automatizadas; driver dummy não prevê o desempenho real.
- Preferências ainda duram a sessão; sem salvamento completo ou novas fases.

GDD SHA-256: `31CB00A4C1DF246C7E66C846CDD3C16508ECE3C8FDDE8AE3EC6317015F4596FA`.
Imagem-base SHA-256: `F4A13C2C6C0978E7735B12CCE2A3CE158898DB0B75318F3C15E255DE08A066F2`.

## Arquivos modificados nesta etapa

Compara??o SHA-256 com o estado anterior ao polimento; nenhum arquivo existente removido.

- `README.md`
- `assets/audio/README.md`
- `scripts/ai/brain.py`
- `scripts/arena_layout.py`
- `scripts/audio/manager.py`
- `scripts/balance.py`
- `scripts/combat/melee.py`
- `scripts/combat/weapon.py`
- `scripts/effects/camera.py`
- `scripts/effects/feedback.py`
- `scripts/effects/image_arena.py`
- `scripts/effects/impact.py`
- `scripts/effects/neon.py`
- `scripts/effects/particles.py`
- `scripts/entities/fighter.py`
- `scripts/entities/fighter_art.py`
- `scripts/entities/player.py`
- `scripts/entities/poses.py`
- `scripts/entities/separation.py`
- `scripts/match_flow.py`
- `scripts/scenes/ringue_neon.py`
- `scripts/ui/debug.py`
- `scripts/ui/hud.py`
- `tests/test_background_v2.py`
- `tests/test_experience.py`
- `tests/test_gameplay.py`
- `tests/test_presentation.py`
- `tools/validate_background.py`

## Arquivos criados nesta etapa

- `assets/audio/efeitos/premium_air_attack.wav`
- `assets/audio/efeitos/premium_beam.wav`
- `assets/audio/efeitos/premium_crowd.wav`
- `assets/audio/efeitos/premium_damage.wav`
- `assets/audio/efeitos/premium_discard.wav`
- `assets/audio/efeitos/premium_drop_impact.wav`
- `assets/audio/efeitos/premium_fall_wind.wav`
- `assets/audio/efeitos/premium_heavy_hit.wav`
- `assets/audio/efeitos/premium_hit.wav`
- `assets/audio/efeitos/premium_jump.wav`
- `assets/audio/efeitos/premium_knockout.wav`
- `assets/audio/efeitos/premium_landing.wav`
- `assets/audio/efeitos/premium_metal_impact.wav`
- `assets/audio/efeitos/premium_metal_swing.wav`
- `assets/audio/efeitos/premium_miss.wav`
- `assets/audio/efeitos/premium_skid.wav`
- `assets/audio/efeitos/premium_step.wav`
- `assets/audio/efeitos/premium_step_l.wav`
- `assets/audio/efeitos/premium_step_r.wav`
- `assets/audio/efeitos/premium_swing.wav`
- `assets/audio/efeitos/premium_warning.wav`
- `assets/audio/interface/premium_back.wav`
- `assets/audio/interface/premium_collect.wav`
- `assets/audio/interface/premium_confirm.wav`
- `assets/audio/interface/premium_countdown.wav`
- `assets/audio/interface/premium_defeat.wav`
- `assets/audio/interface/premium_pause.wav`
- `assets/audio/interface/premium_select.wav`
- `assets/audio/interface/premium_slot_empty.wav`
- `assets/audio/interface/premium_slot_switch.wav`
- `assets/audio/interface/premium_victory.wav`
- `docs/POLIMENTO_PREMIUM.md`
- `scripts/audio/layers.py`
- `scripts/combat/contact.py`
- `scripts/effects/delivery.py`
- `scripts/effects/pan_art.py`
- `scripts/ui/inventory_view.py`
- `scripts/ui/weapon_icons.py`
- `tests/test_premium.py`
- `tools/validate_premium.py`
