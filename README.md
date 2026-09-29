# ARMS RACE — Marco 1

Vertical slice em Python 3.12 e Pygame: menu principal e **Fase 1 — Ringue Neon**, um duelo contra a CPU em uma arena futurista. Interface em português brasileiro, janela de 1280×720 e loop limitado a 60 FPS, com física em passos fixos de 1/60 s.

O documento [docs/ARMS_RACE_GDD.docx](docs/ARMS_RACE_GDD.docx), versão 2.0, é a fonte oficial dos requisitos. Foi lido integralmente e preservado. Esta entrega limita seu escopo ao Marco 1 solicitado; não implementa a campanha completa.

Esta revisão prioriza jogabilidade. Os novos controles solicitados prevalecem
sobre o mapeamento antigo do GDD, que continua intacto. A [lista exata de
arquivos criados e modificados](docs/ARQUIVOS_EXPERIENCIA.md) acompanha a entrega.

A revisão atual preserva **ringue_neon_background_v2.png** como único ambiente,
com overlays animados, silhuetas geométricas de aproximadamente 155 px e combo
de três cliques. O polimento inclui Panela elíptica, entrega em cinco etapas,
inventário com ícones e efeitos sonoros originais em camadas.
Consulte [polimento, arquivos e validação atual](docs/POLIMENTO_PREMIUM.md).
O cenário procedural antigo permanece arquivado no projeto e não é chamado
pelo Ringue Neon. Nenhuma plataforma invisível foi mantida.

Validações históricas da integração da imagem estão no
[relatório v2](docs/RINGUE_BACKGROUND_V2.md). Não houve teste humano dos
controles nem audição; capturas e duelos de validação usam entradas programadas.

Polimento validado com **95 testes**, sintaxe e inicialização sem áudio.
Sessão Windows de 45 s: **61,96 FPS no trecho estável**; média total **57,59 FPS**
incluindo resize/tela cheia. Sessão headless de 180 s: **38,18 FPS**, sete
duelos completos e todas as etapas da entrega. O desempenho inferior do
driver dummy neste ambiente está registrado, sem equipará-lo à janela real.

## Instalação e execução no Windows

Execute no PowerShell, na pasta do projeto. Se `.venv` já existir, preserve-a e pule o comando de criação.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Não é necessário ativar o ambiente nem alterar a política de execução do PowerShell. O jogo funciona offline depois de instalar a dependência. Os caminhos de dados são resolvidos a partir do projeto, independentemente do diretório de execução.

## Controles

| Entrada | Ação |
| --- | --- |
| A / D | Mover |
| Espaço | Pular; soltar cedo reduz a altura |
| Mouse | Apontar braços e golpe |
| Botão esquerdo | Atacar uma vez por clique |
| Q / E ou roda do mouse | Selecionar item |
| X | Descartar |
| Esc | Abrir/fechar pausa |
| R após resultado | Reiniciar |
| Enter | Confirmar; pular a apresentação após tê-la visto uma vez |
| F3 | Ativar/desativar diagnóstico, inicialmente desligado |
| F4 | Prévia temporária de três ícones de armas; somente depuração |

Na pausa: Continuar, Reiniciar, Controles, Configurações e Voltar ao menu.
Nas configurações, use cima/baixo para selecionar e esquerda/direita para
ajustar. Preferências duram a sessão: volume geral, música, efeitos, mute,
tremor de 0–100%, visual/partículas baixo/médio/alto, tela cheia e resolução.
Baixo reduz luzes/plateia e desliga reflexos; Médio é o padrão; Alto habilita
todos os overlays. A/D, Espaço e mouse continuam sendo os controles da luta.

F4 começa desligado e exibe Machado, Rifle e Lançador para validar os slots.
Essas armas são prévias de interface, sem mecânicas de combate: não substituem
os itens reais nem criam munição utilizável. Q/E e roda animam a seleção;
X remove o ícone demonstrativo. F4 novamente restaura a visualização real.
No gameplay normal, a Panela é a única arma disponível.

## Física e revisão de parâmetros

Parâmetros centralizados em `scripts/balance.py`, em pixels e segundos:

| Parâmetro | Valor |
| --- | ---: |
| Velocidade máxima de corrida | 380 px/s |
| Aceleração no chão | 2800 px/s² |
| Aceleração na inversão | 5400 px/s² |
| Frenagem no chão | 3400 px/s² |
| Aceleração no ar | 1820 px/s² (65%) |
| Atrito aéreo | 260 px/s² |
| Gravidade na subida | 1900 px/s² |
| Gravidade na queda | 2700 px/s² |
| Impulso do salto | 720 px/s |
| Velocidade máxima de subida após soltar salto | 270 px/s |
| Coyote time / buffer | 120 ms / 120 ms |
| Hitstun / invulnerabilidade | 130 ms / 220 ms |
| Preparação de ataque | 45 ms |
| Duração total dos socos 1 / 2 / 3 | 230 / 250 / 340 ms |
| Janela de continuação do combo | 400 ms após terminar o golpe |
| Hit-stop soco / terceiro golpe / Panela | 40 / 65 / 80 ms |
| Flash de dano | 50 ms |
| Distância mínima dos centros no chão | 84 px |
| Reação da CPU | 140–240 ms |

Estimativas analíticas para conferir o ajuste: chega à velocidade máxima em
cerca de 136 ms; freia em aproximadamente 112 ms (21 px de deslocamento);
inverte de +380 a -380 px/s em cerca de 141 ms. A altura máxima ideal do salto
é aproximadamente 136 px antes da discretização. A descida usa gravidade
maior para evitar flutuação. Resposta começa no primeiro passo de física.

O controlador usa passos fixos de 1/60 s com delta time, coordenadas fracionárias
e colisões separadas por eixo. O Ringue v2 possui apenas o piso visível.
Plataformas unidirecionais e paredes sólidas continuam suportadas e testadas pelo motor, sem
fechar artificialmente as bordas da arena. Knockback só suspende o controle
durante o hitstun; depois a aceleração volta a conduzir o personagem.

## Combate, arma e CPU

O mouse é convertido de coordenadas da janela para a área lógica e, depois,
para o mundo através da câmera. A mira tem zona morta horizontal de 12 px para
orientação do corpo. A direção é capturada no início do golpe; o braço e a
arma percorrem a mesma trajetória usada na colisão. A Panela varre um arco de
65 graus, com uma amostra da trajetória anterior para reduzir falhas entre
quadros. Preparação não causa dano; cada alvo recebe no máximo um acerto por
golpe. Trocar inventário não altera um golpe em andamento. Receber dano o
cancela; ataques continuam disponíveis no ar.

| Ataque | Dano | Alcance adicional | Cooldown | Impulso |
| --- | ---: | ---: | ---: | ---: |
| Soco 1 | 7 | 52 px | 0,23 s | 255 px/s |
| Soco 2 (outro braço) | 8 | 52 px | 0,25 s | 285 px/s |
| Soco 3 (forte) | 13 | 52 px | 0,34 s | 440 px/s |
| Panela | 10 | 56 px | 0,38 s | 390 px/s |
| Queda da Panela | 8 | Volume varrido durante queda | Um acerto por alvo | 330 px/s |

A Panela é anunciada após seis segundos de luta, com aviso de 0,9 segundo.
O feixe abre em 120 ms, seguido por aproximadamente 0,70 s de queda acelerada.
Núcleo de 16 px, coluna de 44 px e halo de 112 px usam gradientes transparentes
em cache; o feixe desaparece em 100 ms após o impacto. A frigideira tem bojo
escuro elíptico, borda dourada de 5 px, cabo curto e pivô central constante.
Nasce acima da tela, em uma origem vazia; a entrega espera se um corpo estiver
na origem. O marcador permanece no ponto anunciado. Feixe, giro, partículas,
alerta sonoro e impacto antecedem a coleta, liberada 120 ms após tocar o piso.
Há uma única Panela entre cenário e inventários. Descartar não causa dano;
o antigo portador espera um segundo para recolher. Inventário cheio bloqueia
coleta. Ao cair fora da arena, a arma pode ser entregue novamente após o intervalo.
A coleta anima o objeto até a mão em 180 ms, pulsa o slot e mostra PANELA
por 750 ms. O descarte parte da mão e anima o ícone saindo do inventário.

O contato é testado contra cápsulas dos membros desenhados, com um volume
na mão/bojo e varredura entre posições. Um erro não gera partículas de acerto.
As cápsulas corporais separam os lutadores suavemente, permitindo passagem
quando o salto dá altura suficiente. A CPU considera o alcance real e recua.

A CPU observa posições atuais, decide em intervalos de reação, tem 10% de
chance de hesitar numa oportunidade de ataque, procura arma quando vale a
pena, evita o círculo durante a queda, recua durante parte dos cooldowns e
pressiona o jogador com pouca vida. Estados: observar, aproximar, manter
distância, atacar, recuar, pular, buscar arma, desviar de item, recuperar-se e
pressionar. Segurança das bordas e recuperação de dano têm prioridade.

## Apresentação e ritmo

Entrada de 650 ms, contagem 3/2/1/LUTE, controles bloqueados durante a
apresentação e opção de pular por Enter nas tentativas seguintes da sessão.
O último golpe congela por 55 ms e inicia 400 ms de câmera lenta, com física
do derrotado retornando suavemente de 18% à velocidade normal;
dano/IA/coleta param. O vencedor comemora e o resultado aparece.
Empate de eliminação continua contando como derrota do jogador.

O rig procedural interpola articulações e distingue guarda, corrida,
frenagem, salto, queda, pouso, ataque, hitstun e derrota. Efeitos limitados:
poeira/faíscas, rastros, flash branco, arcos, ondas, coleta, confete de vitória,
paleta vermelha na derrota e reação das luzes a golpes fortes. A vida tem
preenchimento animado e rastro atrasado. O HUD mostra cooldown e rejeição de
golpes prematuros.

Câmera acompanha suavemente o centro, muda discretamente o zoom conforme a
distância e os impactos, e dá leve prioridade à arma em queda. O recorte fica
sempre dentro do mundo. Shake pode ser zerado. A janela suporta redimensionamento,
960×540, 1280×720, 1600×900 e 1920×1080, com proporção e barras laterais/superiores
quando necessário. O HUD permanece dentro da área lógica em todas elas.

## Áudio

`AudioManager` usa 17 canais: três para música e 14 divididos entre interface,
personagem, armas, impactos, ambiente e plateia. Há volumes independentes,
mute, panorama estéreo, transição gradual e proteção
contra reiniciar a mesma música. Ringue e camada crítica iniciam sincronizados;
a camada crítica cresce quando alguém chega a 28 de vida ou após 45 s de luta.

Os três loops instrumentais originais de 8 s a 120 BPM foram preservados.
Novos arquivos `premium_*.wav` usam camadas de ruído filtrado, impacto seco,
corpo grave, estalo, ar e ressonâncias metálicas não harmônicas. Soco, terceiro
golpe, Panela no lutador e Panela no chão têm receitas diferentes. Os efeitos
antigos permanecem preservados. Tom varia ±3%, volume entre 94–100%; os sons
são pré-carregados. Arquivos ausentes usam síntese; falha de dispositivo
desativa áudio sem impedir o jogo. As receitas estão em `scripts/audio/layers.py`;
instruções de geração/substituição em `assets/audio/README.md`.

Golpes fortes reduzem a música em 4 dB por 150 ms, com retorno suave. Passos
são discretos e o volume do pouso acompanha a velocidade. O nocaute inicia
fade rápido da música e efeito próprio antes da vinheta de resultado.

## Validação reproduzível

```powershell
.\.venv\Scripts\python.exe -m compileall -q main.py scripts tests tools
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m tools.validate_premium --seconds 180
.\.venv\Scripts\python.exe -m tools.validate_background --seconds 180
.\.venv\Scripts\python.exe -m tools.validate_background --window --seconds 45
.\.venv\Scripts\python.exe main.py --headless --no-audio --scene ringue --frames 120
```

A ferramenta premium gera A (guarda/inventário), B (queda/feixe), C (contato
real da Panela), além das etapas da entrega e mira vertical. Arquivos em
`.local/premium/`; `headless.json` registra a sessão e seus tempos.
As ferramentas anteriores geram capturas preparadas de contagem, corrida,
salto, ataque, impacto, queda da arma, vida baixa, vitória, pausa, configurações,
derrota, F3 e resolução reduzida. Depois executa duelos automatizados por tempo
real, incluindo reinícios e pausa, verificando vida, unicidade da arma e limite
de partículas. Saída: `.local/experiencia/sessao_headless.json` e PNGs.

Não é um teste humano: as entradas da sessão são programadas, e o mixer SDL
dummy não permite avaliar o som por escuta. Nenhuma validação interativa ou
audição manual é alegada. Resultados medidos estão no README.

## Histórico de validação anterior à imagem v2

Os números abaixo pertencem à revisão anterior. Os resultados atuais estão
em [RINGUE_BACKGROUND_V2.md](docs/RINGUE_BACKGROUND_V2.md).

- Antes das alterações: 32 testes aprovados. Depois: **59 testes aprovados**, sem remover a cobertura anterior.
- Sintaxe: `compileall` sem erros. Inicialização: 120 quadros headless com `--no-audio`, sem falhas.
- Foram executadas três sessões de 180 segundos durante os ajustes. A sessão final percorreu **11.106 quadros em 180,01 s**, com 15 duelos encerrados (11 vitórias e 4 derrotas), pausa e reinícios, sem falhas nas verificações.
- Média observada final: **61,70 FPS**; trabalho por quadro de **9,017 ms em média** e **15,706 ms no percentil 95**. Esse tempo exclui a espera do limitador. O pico foi de 111 partículas; todos os estados da entrega da Panela foram percorridos.
- Medição em SDL dummy, 1280×720, incluindo mixer dummy. Não prevê o desempenho da janela/compositor ou de outro computador. O limitador de maior precisão usa `tick_busy_loop`, que pode consumir mais CPU que uma espera comum; a física mantém passos de 1/60 s.
- Treze capturas foram geradas. As imagens dos nove estados solicitados foram abertas e inspecionadas, além de configurações, derrota e resolução reduzida. Painéis e textos ficaram dentro da janela; o HUD fica separado da área dos combatentes. Não houve teste manual interativo nem audição.

Evidências locais (ignoradas pelo Git): [medição JSON](.local/experiencia/sessao_headless.json), [corrida](.local/experiencia/02_corrida.png), [ataque](.local/experiencia/04_ataque.png), [Panela caindo](.local/experiencia/06_panela.png) e [pausa](.local/experiencia/09_pausa.png).

A comparação com a referência confirma a distribuição ciano à esquerda/rosa à direita, fundo azul-escuro, três telões, público em camadas, cordas neon, estrutura inferior e feixe dourado exclusivo da arma. A implementação continua sendo arte procedural simplificada: brilho e volume são mais planos que na ilustração, e a perspectiva é frontal para preservar a leitura das colisões. A sensação de fluidez, força dos golpes e equilíbrio sonoro ainda precisa da avaliação humana descrita abaixo.

## Limitações e teste manual

- Preferências não persistem ao fechar; nenhuma campanha ou save completo foi adicionado.
- Música procedural simples de quatro compassos, sem arranjo longo ou produção de estúdio.
- CPU heurística, sem navegação complexa; avaliar dificuldade e exploração das plataformas.
- Confirmar resposta do teclado/mouse, sensação do salto e do golpe, leitura das poses e conforto do shake.
- Escutar mixagem, loops, transições, volume da Panela e da torcida com alto-falantes/fones reais.
- Testar tela cheia, mudança de resolução, perda de foco e estabilidade de FPS no computador de destino.
- Conferir duelo completo, coleta/descarte, derrota por queda, vitória e reinício rápido.

GDD preservado: SHA-256 `31CB00A4C1DF246C7E66C846CDD3C16508ECE3C8FDDE8AE3EC6317015F4596FA`.

## Organização atual

```text
main.py                     Entrada; --headless e --no-audio
scripts/
  balance.py                Parâmetros de física, combate e CPU
  arena_layout.py           Piso, limites, spawns e altura normalizados
  settings.py               Preferências da sessão
  game.py                   Loop, dispositivos e cenas
  viewport.py               Resolução, proporção e mouse
  match_flow.py             Introdução, contagem e encerramento
  entities/
    fighter.py              Combatente compartilhado
    movement.py             Motor físico e salto
    separation.py           Separação horizontal entre combatentes
    poses.py                Alvos de animação
    fighter_art.py          Interpolação e desenho articulado
    player.py, enemy.py     Entrada e controle
  combat/
    melee.py                Trajetória, hitbox, dano e hitstun
    weapon.py               Inventário e entrega da Panela
  ai/brain.py               Estados e reação da CPU
  audio/
    manager.py              Mixer, volumes, panorama, ducking e fallback
    synth.py                Música e síntese históricas preservadas
    layers.py               Novos efeitos originais compostos em camadas
  effects/
    image_arena.py          Imagem-base v2 e iluminação/plateia animadas
    competitive_arena.py    Cenário anterior arquivado (não usado na fase)
    camera.py               Enquadramento, zoom e shake
    feedback.py             Integração de impactos e sons
    particles.py            Partículas limitadas
    impact.py               Ondas e flash
    delivery.py             Feixe, aviso, impacto e voo de coleta
    pan_art.py              Superfície da frigideira e rotação no pivô
  scenes/
    menu.py, loja.py        Menu e loja provisória preservados
    ringue_neon.py          Coordenação da partida
    pausa.py, options.py    Pausa, controles e configurações
  ui/
    hud.py, style.py        Interface neon
    inventory_view.py      Slots e animações de inventário
    weapon_icons.py        Ícones vetoriais das armas
    debug.py                Diagnóstico F3
assets/audio/
  musica/                   Três loops originais
  efeitos/                  Efeitos históricos + 21 WAVs premium
  interface/                Interface histórica + 10 WAVs premium
dados/levels/               Geometria do Ringue Neon preservada
tests/                      Regressão e novos testes de experiência
tools/validate_experience.py Capturas e sessão prolongada
tools/validate_background.py Capturas v2, janela real e medição
tools/validate_premium.py    Capturas A/B/C e duelos de polimento
docs/                       GDD original e relatórios
```

Os diretórios antigos de assets permanecem preservados. Nenhuma dependência
além de Pygame foi adicionada. Não há download de recursos em tempo de execução.
